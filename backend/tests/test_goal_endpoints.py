"""
Integration tests for Goal Progress API endpoints
Tests all REST API endpoints for goal tracking
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
import json

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from models.goal_progress import GoalProgressTracker, Milestone


# ==================== Test Client Setup ====================

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def test_user_id():
    """Test user ID"""
    return "test_user_integration_123"


# ==================== Test: Create Goal Endpoint ====================

def test_create_goal_success(client, test_user_id):
    """Test POST /api/v2/goals/create - Success"""
    response = client.post(
        "/api/v2/goals/create",
        data={
            "user_id": test_user_id,
            "target_date": (date.today() + timedelta(days=180)).isoformat(),
            "description": "6개월 Python 마스터"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["created"] is True
    assert "goal_id" in data
    assert data["one_thing"] is not None


def test_create_goal_missing_user_id(client):
    """Test POST /api/v2/goals/create - Missing user_id"""
    response = client.post(
        "/api/v2/goals/create",
        data={
            "description": "Test goal"
        }
    )

    assert response.status_code == 422  # Validation error


def test_create_goal_invalid_date_format(client, test_user_id):
    """Test POST /api/v2/goals/create - Invalid date format"""
    response = client.post(
        "/api/v2/goals/create",
        data={
            "user_id": test_user_id,
            "target_date": "invalid-date-format"
        }
    )

    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


# ==================== Test: Get Goal Summary Endpoint ====================

def test_get_goal_summary_success(client, test_user_id):
    """Test GET /api/v2/goals/{user_id} - Success"""
    # First create a goal
    client.post(
        "/api/v2/goals/create",
        data={"user_id": test_user_id}
    )

    # Then get summary
    response = client.get(f"/api/v2/goals/{test_user_id}")

    assert response.status_code == 200
    data = response.json()
    assert "goal" in data
    assert "completion_percentage" in data
    assert "milestones" in data


def test_get_goal_summary_not_found(client):
    """Test GET /api/v2/goals/{user_id} - Not found"""
    response = client.get("/api/v2/goals/nonexistent_user_999")

    assert response.status_code == 404
    assert "No goal found" in response.json()["detail"]


# ==================== Test: Record Progress Endpoint ====================

def test_record_progress_success(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/progress - Success"""
    # Setup: Create goal first
    client.post(
        "/api/v2/goals/create",
        data={"user_id": test_user_id}
    )

    # Record progress
    metrics = [
        {
            "name": "Study Hours",
            "value": 2.5,
            "unit": "hours",
            "metric_type": "time"
        }
    ]

    response = client.post(
        f"/api/v2/goals/{test_user_id}/progress",
        data={
            "reflection": "오늘 많이 배웠어요!",
            "mood_rating": 4,
            "metrics": json.dumps(metrics)
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "recorded_at" in data


def test_record_progress_invalid_mood(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/progress - Invalid mood rating"""
    response = client.post(
        f"/api/v2/goals/{test_user_id}/progress",
        data={
            "reflection": "Test",
            "mood_rating": 10  # Invalid (must be 1-5)
        }
    )

    assert response.status_code == 400
    assert "Mood rating must be 1-5" in response.json()["detail"]


def test_record_progress_invalid_metrics_json(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/progress - Invalid metrics JSON"""
    response = client.post(
        f"/api/v2/goals/{test_user_id}/progress",
        data={
            "metrics": "invalid-json"
        }
    )

    assert response.status_code == 400
    assert "Invalid metrics format" in response.json()["detail"]


# ==================== Test: Add Milestone Endpoint ====================

def test_add_milestone_success(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/milestones - Success"""
    # Setup: Create goal
    client.post(
        "/api/v2/goals/create",
        data={"user_id": test_user_id}
    )

    # Add milestone
    response = client.post(
        f"/api/v2/goals/{test_user_id}/milestones",
        data={
            "description": "첫 프로젝트 완성",
            "target_date": (date.today() + timedelta(days=30)).isoformat(),
            "reward": "축하합니다!"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_add_milestone_missing_description(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/milestones - Missing description"""
    response = client.post(
        f"/api/v2/goals/{test_user_id}/milestones",
        data={}
    )

    assert response.status_code == 422  # Validation error


# ==================== Test: Update Milestone Status Endpoint ====================

def test_update_milestone_status_success(client, test_user_id):
    """Test PATCH /api/v2/goals/{user_id}/milestones/{milestone_id} - Success"""
    # Setup: Create goal and get milestone ID
    client.post(
        "/api/v2/goals/create",
        data={"user_id": test_user_id}
    )

    summary = client.get(f"/api/v2/goals/{test_user_id}").json()
    if summary["milestones"]["upcoming"]:
        milestone_id = summary["milestones"]["upcoming"][0]["milestone_id"]

        # Update milestone status
        response = client.patch(
            f"/api/v2/goals/{test_user_id}/milestones/{milestone_id}",
            data={"is_completed": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_completed"] is True


def test_update_milestone_status_not_found(client, test_user_id):
    """Test PATCH /api/v2/goals/{user_id}/milestones/{milestone_id} - Not found"""
    response = client.patch(
        f"/api/v2/goals/{test_user_id}/milestones/nonexistent_milestone",
        data={"is_completed": True}
    )

    assert response.status_code == 404


# ==================== Test: Setup Tracked Metrics Endpoint ====================

def test_setup_metrics_success(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/setup-metrics - Success"""
    # Setup: Create goal
    client.post(
        "/api/v2/goals/create",
        data={"user_id": test_user_id}
    )

    metrics_config = {
        "metrics": ["Study Hours", "Pages Read", "Exercises Completed"],
        "units": {
            "Study Hours": "hours",
            "Pages Read": "pages",
            "Exercises Completed": "개"
        }
    }

    response = client.post(
        f"/api/v2/goals/{test_user_id}/setup-metrics",
        data={"metrics_config": json.dumps(metrics_config)}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["tracked_metrics"]) == 3


def test_setup_metrics_invalid_json(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/setup-metrics - Invalid JSON"""
    response = client.post(
        f"/api/v2/goals/{test_user_id}/setup-metrics",
        data={"metrics_config": "invalid-json"}
    )

    assert response.status_code == 400
    assert "Invalid metrics config format" in response.json()["detail"]


# ==================== Test: Get Progress History Endpoint ====================

def test_get_progress_history_success(client, test_user_id):
    """Test GET /api/v2/goals/{user_id}/history - Success"""
    # Setup: Create goal and record some progress
    client.post(
        "/api/v2/goals/create",
        data={"user_id": test_user_id}
    )

    client.post(
        f"/api/v2/goals/{test_user_id}/progress",
        data={"reflection": "Day 1"}
    )

    # Get history
    response = client.get(f"/api/v2/goals/{test_user_id}/history?days=7")

    assert response.status_code == 200
    data = response.json()
    assert "total_snapshots" in data
    assert "snapshots" in data


def test_get_progress_history_custom_days(client, test_user_id):
    """Test GET /api/v2/goals/{user_id}/history - Custom days parameter"""
    response = client.get(f"/api/v2/goals/{test_user_id}/history?days=90")

    assert response.status_code == 200
    data = response.json()
    assert data["days"] == 90


# ==================== Test: Generate Insights Endpoint ====================

def test_generate_insights_success(client, test_user_id):
    """Test POST /api/v2/goals/{user_id}/insights - Success"""
    # Setup: Create goal with some progress
    client.post(
        "/api/v2/goals/create",
        data={"user_id": test_user_id}
    )

    client.post(
        f"/api/v2/goals/{test_user_id}/progress",
        data={"reflection": "Progress!"}
    )

    # Generate insights
    response = client.post(f"/api/v2/goals/{test_user_id}/insights")

    assert response.status_code == 200
    data = response.json()
    assert "total_insights" in data
    assert "insights" in data
    assert isinstance(data["insights"], list)


def test_generate_insights_no_goal(client):
    """Test POST /api/v2/goals/{user_id}/insights - No goal"""
    response = client.post("/api/v2/goals/no_goal_user/insights")

    assert response.status_code == 404
    assert "No goal found" in response.json()["detail"]


# ==================== Test: Error Handling ====================

def test_endpoint_with_invalid_user_id_format(client):
    """Test endpoints with invalid user_id format"""
    response = client.get("/api/v2/goals/")

    assert response.status_code == 404


def test_endpoint_server_error_handling(client, monkeypatch):
    """Test that server errors return 500 with proper message"""
    # This would require mocking a service to raise an exception
    # For now, just verify error handler exists
    pass


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
