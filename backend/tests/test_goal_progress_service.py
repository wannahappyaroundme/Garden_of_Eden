"""
Unit tests for Goal Progress Service
Tests milestone generation, trend analysis, and insight generation
"""
import pytest
import asyncio
from datetime import date, datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.goal_progress_service import GoalProgressService
from models.goal_progress import (
    GoalProgressTracker,
    Milestone,
    ProgressSnapshot,
    GoalMetric,
    ProgressTrend,
    GoalInsight,
    MoodRating,
    MetricType,
    InsightType
)
from models.user_profile import UserProfile, OneThing, CorePitfall


# ==================== Fixtures ====================

@pytest.fixture
def mock_db_service():
    """Mock DynamoDB service"""
    db = Mock()
    db.get_goal_progress = AsyncMock(return_value=None)
    db.save_goal_progress = AsyncMock(return_value=True)
    db.update_milestone = AsyncMock(return_value=True)
    db.get_progress_history = AsyncMock(return_value=[])
    return db


@pytest.fixture
def mock_gemini_service():
    """Mock Gemini LLM service"""
    gemini = Mock()
    gemini.generate_content = AsyncMock()
    return gemini


@pytest.fixture
def goal_service(mock_db_service, mock_gemini_service):
    """Goal progress service with mocked dependencies"""
    return GoalProgressService(
        db_service=mock_db_service,
        gemini_service=mock_gemini_service
    )


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing"""
    return UserProfile(
        user_id="test_user_123",
        one_thing=OneThing(
            value="Python 마스터하기",
            confidence_score=0.9,
            extracted_at=datetime.now()
        ),
        core_pitfall=CorePitfall(
            value="과도한 완벽주의",
            confidence_score=0.85,
            triggers=["세부사항", "완벽", "100%"],
            first_detected=datetime.now()
        )
    )


@pytest.fixture
def sample_goal_tracker():
    """Sample goal tracker with milestones and snapshots"""
    tracker = GoalProgressTracker(
        user_id="test_user_123",
        goal_id="goal_456",
        one_thing="Python 마스터하기",
        description="6개월 안에 Python 고급 기술 습득",
        start_date=date.today() - timedelta(days=30),
        target_date=date.today() + timedelta(days=150),
        tracked_metrics=["Study Hours", "Projects Completed"],
        metric_units={"Study Hours": "hours", "Projects Completed": "개"}
    )

    # Add milestones
    tracker.milestones = [
        Milestone(
            milestone_id="m1",
            description="Python 기초 문법 완료",
            target_date=date.today() - timedelta(days=10),
            is_completed=True,
            completed_at=date.today() - timedelta(days=12)
        ),
        Milestone(
            milestone_id="m2",
            description="OOP 개념 이해",
            target_date=date.today() + timedelta(days=5),
            is_completed=False
        ),
        Milestone(
            milestone_id="m3",
            description="첫 프로젝트 완성",
            target_date=date.today() + timedelta(days=30),
            is_completed=False
        )
    ]

    # Add progress snapshots
    for i in range(10):
        snapshot_date = date.today() - timedelta(days=10 - i)
        tracker.snapshots.append(
            ProgressSnapshot(
                snapshot_id=f"snap_{i}",
                snapshot_date=snapshot_date,
                metrics=[
                    GoalMetric(
                        name="Study Hours",
                        value=2.0 + i * 0.2,  # Progressive increase
                        unit="hours",
                        metric_type=MetricType.TIME
                    )
                ],
                reflection=f"Day {i+1} reflection",
                mood_rating=MoodRating.GOOD
            )
        )

    return tracker


# ==================== Test: Milestone Generation ====================

@pytest.mark.asyncio
async def test_suggest_milestones_success(goal_service, mock_gemini_service):
    """Test AI-powered milestone generation"""
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = """[
        {
            "description": "Python 기초 문법 학습",
            "target_date": "2025-12-01",
            "reward": "첫 단계 완료!"
        },
        {
            "description": "간단한 프로그램 작성",
            "target_date": "2025-12-15",
            "reward": "실전 경험 획득"
        }
    ]"""
    mock_gemini_service.generate_content.return_value = mock_response

    # Test milestone suggestion
    milestones = await goal_service.suggest_milestones(
        goal="Python 마스터하기",
        timeframe_days=180,
        user_context="초보자, 프로그래밍 경험 없음"
    )

    # Assertions
    assert len(milestones) == 2
    assert milestones[0].description == "Python 기초 문법 학습"
    assert milestones[0].reward == "첫 단계 완료!"
    assert mock_gemini_service.generate_content.called


@pytest.mark.asyncio
async def test_suggest_milestones_empty_goal(goal_service):
    """Test milestone generation with empty goal"""
    milestones = await goal_service.suggest_milestones(
        goal="",
        timeframe_days=180
    )

    assert milestones == []


# ==================== Test: Progress Trend Analysis ====================

@pytest.mark.asyncio
async def test_analyze_progress_trend_improving(goal_service, sample_goal_tracker):
    """Test trend analysis with improving progress"""
    trend = await goal_service.analyze_progress_trend(
        snapshots=sample_goal_tracker.snapshots,
        tracked_metric_name="Study Hours"
    )

    assert trend is not None
    assert trend.direction == "improving"
    assert trend.velocity > 0
    assert trend.current_streak >= 10  # All 10 days have progress
    assert trend.consistency_score > 0.8


@pytest.mark.asyncio
async def test_analyze_progress_trend_no_snapshots(goal_service):
    """Test trend analysis with no snapshots"""
    trend = await goal_service.analyze_progress_trend(
        snapshots=[],
        tracked_metric_name="Study Hours"
    )

    assert trend is None


@pytest.mark.asyncio
async def test_analyze_progress_trend_declining(goal_service):
    """Test trend analysis with declining progress"""
    # Create declining snapshots
    snapshots = []
    for i in range(5):
        snapshot_date = date.today() - timedelta(days=5 - i)
        snapshots.append(
            ProgressSnapshot(
                snapshot_id=f"snap_{i}",
                snapshot_date=snapshot_date,
                metrics=[
                    GoalMetric(
                        name="Study Hours",
                        value=5.0 - i * 0.5,  # Declining
                        unit="hours",
                        metric_type=MetricType.TIME
                    )
                ],
                mood_rating=MoodRating.LOW
            )
        )

    trend = await goal_service.analyze_progress_trend(
        snapshots=snapshots,
        tracked_metric_name="Study Hours"
    )

    assert trend is not None
    assert trend.direction == "declining"
    assert trend.velocity < 0


# ==================== Test: Goal Creation ====================

@pytest.mark.asyncio
async def test_create_goal_from_one_thing_success(
    goal_service,
    mock_db_service,
    mock_gemini_service,
    sample_user_profile
):
    """Test goal creation from user's One Thing"""
    # Mock milestone generation
    mock_response = Mock()
    mock_response.text = """[
        {
            "description": "첫 단계 완료",
            "target_date": "2025-12-15"
        }
    ]"""
    mock_gemini_service.generate_content.return_value = mock_response

    # Create goal
    tracker = await goal_service.create_goal_from_one_thing(
        user_profile=sample_user_profile,
        target_date=date.today() + timedelta(days=180),
        description="6개월 Python 마스터 플랜"
    )

    # Assertions
    assert tracker is not None
    assert tracker.one_thing == "Python 마스터하기"
    assert tracker.description == "6개월 Python 마스터 플랜"
    assert len(tracker.milestones) >= 1
    assert mock_db_service.save_goal_progress.called


@pytest.mark.asyncio
async def test_create_goal_no_one_thing(goal_service):
    """Test goal creation without One Thing"""
    profile = UserProfile(user_id="test_user", one_thing=None)

    tracker = await goal_service.create_goal_from_one_thing(
        user_profile=profile
    )

    assert tracker is None


# ==================== Test: Progress Recording ====================

@pytest.mark.asyncio
async def test_record_progress_success(
    goal_service,
    mock_db_service,
    sample_goal_tracker
):
    """Test progress recording"""
    mock_db_service.get_goal_progress.return_value = sample_goal_tracker

    metrics = [
        GoalMetric(
            name="Study Hours",
            value=3.5,
            unit="hours",
            metric_type=MetricType.TIME
        )
    ]

    success = await goal_service.record_progress(
        user_id="test_user_123",
        metrics=metrics,
        reflection="오늘 많이 배웠다!",
        mood_rating=MoodRating.EXCELLENT
    )

    assert success is True
    assert mock_db_service.save_goal_progress.called


@pytest.mark.asyncio
async def test_record_progress_no_goal(goal_service, mock_db_service):
    """Test progress recording without existing goal"""
    mock_db_service.get_goal_progress.return_value = None

    success = await goal_service.record_progress(
        user_id="test_user_123",
        reflection="Test"
    )

    assert success is False


# ==================== Test: Stagnation Detection ====================

@pytest.mark.asyncio
async def test_detect_stagnation_true(goal_service):
    """Test stagnation detection (7+ days no progress)"""
    # Create tracker with old last snapshot
    tracker = GoalProgressTracker(
        user_id="test",
        goal_id="goal1",
        one_thing="Test Goal"
    )

    old_snapshot = ProgressSnapshot(
        snapshot_id="old",
        snapshot_date=date.today() - timedelta(days=10),
        metrics=[]
    )
    tracker.snapshots = [old_snapshot]

    is_stagnant = await goal_service._detect_stagnation(
        tracker=tracker,
        threshold_days=7
    )

    assert is_stagnant is True


@pytest.mark.asyncio
async def test_detect_stagnation_false(goal_service):
    """Test stagnation detection (recent progress)"""
    tracker = GoalProgressTracker(
        user_id="test",
        goal_id="goal1",
        one_thing="Test Goal"
    )

    recent_snapshot = ProgressSnapshot(
        snapshot_id="recent",
        snapshot_date=date.today() - timedelta(days=3),
        metrics=[]
    )
    tracker.snapshots = [recent_snapshot]

    is_stagnant = await goal_service._detect_stagnation(
        tracker=tracker,
        threshold_days=7
    )

    assert is_stagnant is False


# ==================== Test: Insight Generation ====================

@pytest.mark.asyncio
async def test_generate_insights_success(
    goal_service,
    mock_gemini_service,
    sample_goal_tracker,
    sample_user_profile
):
    """Test AI-powered insight generation"""
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = """[
        {
            "insight_type": "achievement",
            "title": "꾸준한 성장",
            "description": "지난 10일간 꾸준히 학습하셨네요!",
            "actionable": false,
            "priority": 1
        },
        {
            "insight_type": "suggestion",
            "title": "다음 단계",
            "description": "이제 프로젝트를 시작해보세요",
            "actionable": true,
            "priority": 2
        }
    ]"""
    mock_gemini_service.generate_content.return_value = mock_response

    insights = await goal_service.generate_progress_insights(
        tracker=sample_goal_tracker,
        user_profile=sample_user_profile
    )

    assert len(insights) == 2
    assert insights[0].insight_type == InsightType.ACHIEVEMENT
    assert insights[1].actionable is True


@pytest.mark.asyncio
async def test_generate_insights_no_data(
    goal_service,
    sample_user_profile
):
    """Test insight generation with insufficient data"""
    empty_tracker = GoalProgressTracker(
        user_id="test",
        goal_id="goal1",
        one_thing="Test"
    )

    insights = await goal_service.generate_progress_insights(
        tracker=empty_tracker,
        user_profile=sample_user_profile
    )

    # Should still generate insights based on lack of data
    assert isinstance(insights, list)


# ==================== Test: Goal Summary ====================

@pytest.mark.asyncio
async def test_get_goal_summary_success(
    goal_service,
    mock_db_service,
    sample_goal_tracker
):
    """Test goal summary retrieval"""
    mock_db_service.get_goal_progress.return_value = sample_goal_tracker

    summary = await goal_service.get_goal_summary("test_user_123")

    assert summary is not None
    assert summary["goal"] == "Python 마스터하기"
    assert "completion_percentage" in summary
    assert "milestones" in summary
    assert "insights" in summary


@pytest.mark.asyncio
async def test_get_goal_summary_no_goal(goal_service, mock_db_service):
    """Test goal summary with no goal"""
    mock_db_service.get_goal_progress.return_value = None

    summary = await goal_service.get_goal_summary("test_user_123")

    assert summary is None


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
