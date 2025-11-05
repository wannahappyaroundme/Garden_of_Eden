"""
Goal Progress Service for Project Eden V2
Business logic for goal tracking, milestone generation, and progress analysis with AI insights
"""
import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import json

from models.user_profile import UserProfile
from models.goal_progress import (
    GoalProgressTracker,
    ProgressSnapshot,
    Milestone,
    GoalMetric,
    ProgressTrend,
    GoalInsight,
    MoodRating,
    MetricType
)
from services.dynamodb_service_v2 import DynamoDBService
from services.gemini_service import GeminiService
from utils.logger import get_logger

logger = get_logger(__name__)


class GoalProgressService:
    """Service for managing goal progress tracking and AI-powered insights"""

    def __init__(
        self,
        db_service: DynamoDBService,
        gemini_service: GeminiService
    ):
        self.db = db_service
        self.gemini = gemini_service

    # ==================== Goal Creation & Initialization ====================

    async def create_goal_from_one_thing(
        self,
        user_profile: UserProfile,
        target_date: Optional[date] = None,
        description: Optional[str] = None
    ) -> Optional[GoalProgressTracker]:
        """Initialize goal tracker from user's One Thing"""
        try:
            if not user_profile.one_thing or not user_profile.one_thing.value:
                logger.warning(f"Cannot create goal - no One Thing set for user {user_profile.user_id}")
                return None

            goal_id = str(uuid.uuid4())

            # Create tracker
            tracker = GoalProgressTracker(
                user_id=user_profile.user_id,
                goal_id=goal_id,
                one_thing=user_profile.one_thing.value,
                description=description,
                start_date=date.today(),
                target_date=target_date
            )

            # Generate initial milestones using AI
            if target_date:
                days_until_target = (target_date - date.today()).days
                milestones = await self.suggest_milestones(
                    goal=user_profile.one_thing.value,
                    timeframe_days=days_until_target,
                    user_context=self._build_user_context(user_profile)
                )
                for milestone in milestones:
                    tracker.add_milestone(milestone)

            # Save to database
            success = await self.db.save_goal_progress(tracker)

            if success:
                logger.info(f"Created goal tracker for user {user_profile.user_id}")
                return tracker
            else:
                logger.error(f"Failed to save goal tracker for {user_profile.user_id}")
                return None

        except Exception as e:
            logger.error(f"Error creating goal from One Thing: {e}")
            return None

    async def suggest_milestones(
        self,
        goal: str,
        timeframe_days: int,
        user_context: Optional[str] = None
    ) -> List[Milestone]:
        """Generate AI-powered milestone suggestions"""
        try:
            prompt = f"""You are a goal-setting expert. Create a detailed milestone plan for achieving this goal:

Goal: {goal}
Timeframe: {timeframe_days} days

{f"User Context: {user_context}" if user_context else ""}

Create 3-7 specific, measurable milestones that:
1. Are evenly distributed across the timeframe
2. Build progressively toward the goal
3. Are realistic and achievable
4. Include specific success criteria

Return ONLY a JSON array of milestones with this exact structure:
[
  {{
    "description": "Complete first chapter of the book",
    "target_date": "2025-12-15",
    "order": 1
  }},
  ...
]

Requirements:
- Use ISO date format (YYYY-MM-DD)
- Start dates should begin 20% into the timeframe
- End dates should be 90% of the timeframe
- Each milestone should be 1-2 sentences
- Order starts at 1"""

            response = await self.gemini.generate_content(prompt)

            # Parse response
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()

            milestone_data = json.loads(response_text)

            # Convert to Milestone objects
            milestones = []
            for data in milestone_data:
                milestone = Milestone(
                    milestone_id=str(uuid.uuid4()),
                    description=data["description"],
                    target_date=date.fromisoformat(data["target_date"]) if data.get("target_date") else None,
                    order=data.get("order", len(milestones) + 1),
                    is_completed=False
                )
                milestones.append(milestone)

            logger.info(f"Generated {len(milestones)} milestones for goal: {goal[:50]}...")
            return milestones

        except Exception as e:
            logger.error(f"Error suggesting milestones: {e}")
            # Return default milestones as fallback
            return self._generate_default_milestones(goal, timeframe_days)

    def _generate_default_milestones(self, goal: str, timeframe_days: int) -> List[Milestone]:
        """Generate basic default milestones if AI fails"""
        start_date = date.today()
        milestones = [
            Milestone(
                milestone_id=str(uuid.uuid4()),
                description=f"Begin working on: {goal}",
                target_date=start_date + timedelta(days=int(timeframe_days * 0.2)),
                order=1
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                description=f"Reach halfway point for: {goal}",
                target_date=start_date + timedelta(days=int(timeframe_days * 0.5)),
                order=2
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                description=f"Complete final phase of: {goal}",
                target_date=start_date + timedelta(days=int(timeframe_days * 0.9)),
                order=3
            )
        ]
        return milestones

    # ==================== Progress Recording ====================

    async def record_progress(
        self,
        user_id: str,
        metrics: Optional[List[GoalMetric]] = None,
        reflection: Optional[str] = None,
        mood_rating: Optional[MoodRating] = None,
        photo_url: Optional[str] = None
    ) -> bool:
        """Record a progress snapshot"""
        try:
            snapshot = ProgressSnapshot(
                snapshot_id=str(uuid.uuid4()),
                date=date.today(),
                metrics=metrics or [],
                reflection=reflection,
                mood_rating=mood_rating,
                photo_url=photo_url
            )

            success = await self.db.add_progress_snapshot(user_id, snapshot)

            if success:
                logger.info(f"Recorded progress snapshot for user {user_id}")

                # Analyze trend after recording
                await self._update_progress_trend(user_id)

                # Check for stagnation
                await self.detect_stagnation(user_id)

            return success

        except Exception as e:
            logger.error(f"Error recording progress for {user_id}: {e}")
            return False

    async def setup_tracked_metrics(
        self,
        user_id: str,
        metric_names: List[str],
        metric_units: Dict[str, str]
    ) -> bool:
        """Configure which metrics to track for a goal"""
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                logger.warning(f"Cannot setup metrics - no tracker found for {user_id}")
                return False

            tracker.tracked_metrics = metric_names
            tracker.metric_units = metric_units
            tracker.updated_at = datetime.now()

            return await self.db.save_goal_progress(tracker)

        except Exception as e:
            logger.error(f"Error setting up metrics for {user_id}: {e}")
            return False

    # ==================== Progress Analysis ====================

    async def analyze_progress_trend(
        self,
        snapshots: List[ProgressSnapshot],
        tracked_metric_name: Optional[str] = None
    ) -> Optional[ProgressTrend]:
        """Analyze progress trend from snapshots"""
        try:
            if len(snapshots) < 2:
                return None

            # Sort by date (oldest first for analysis)
            sorted_snapshots = sorted(snapshots, key=lambda s: s.snapshot_date)

            # Calculate streak
            current_streak = self._calculate_current_streak(sorted_snapshots)
            best_streak = self._calculate_best_streak(sorted_snapshots)

            # Calculate velocity if tracking a metric
            velocity = 0.0
            direction = "stable"

            if tracked_metric_name and len(sorted_snapshots) >= 3:
                values = []
                for snapshot in sorted_snapshots:
                    value = snapshot.get_metric_value(tracked_metric_name)
                    if value is not None:
                        values.append(value)

                if len(values) >= 3:
                    # Simple linear regression for velocity
                    velocity = (values[-1] - values[0]) / len(values)

                    if velocity > 0.1:
                        direction = "improving"
                    elif velocity < -0.1:
                        direction = "declining"

            # Calculate consistency score (0.0-1.0)
            consistency_score = min(current_streak / 30.0, 1.0)  # Max score at 30-day streak

            # Calculate average mood
            mood_ratings = [s.mood_rating for s in sorted_snapshots if s.mood_rating is not None]
            avg_mood = sum(mood_ratings) / len(mood_ratings) if mood_ratings else None

            trend = ProgressTrend(
                direction=direction,
                velocity=velocity,
                consistency_score=consistency_score,
                best_streak=best_streak,
                current_streak=current_streak,
                total_entries=len(sorted_snapshots),
                avg_mood=avg_mood
            )

            return trend

        except Exception as e:
            logger.error(f"Error analyzing progress trend: {e}")
            return None

    async def _update_progress_trend(self, user_id: str) -> bool:
        """Update the trend analysis for a user's goal"""
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                return False

            # Get primary metric if available
            primary_metric = tracker.tracked_metrics[0] if tracker.tracked_metrics else None

            # Analyze trend
            trend = await self.analyze_progress_trend(tracker.snapshots, primary_metric)

            if trend:
                tracker.current_trend = trend
                tracker.updated_at = datetime.now()
                return await self.db.save_goal_progress(tracker)

            return False

        except Exception as e:
            logger.error(f"Error updating progress trend for {user_id}: {e}")
            return False

    def _calculate_current_streak(self, sorted_snapshots: List[ProgressSnapshot]) -> int:
        """Calculate current consecutive day streak"""
        if not sorted_snapshots:
            return 0

        streak = 0
        current_date = date.today()

        # Work backwards from today
        for i in range(len(sorted_snapshots) - 1, -1, -1):
            snapshot = sorted_snapshots[i]
            expected_date = current_date - timedelta(days=streak)

            if snapshot.snapshot_date == expected_date:
                streak += 1
            elif snapshot.snapshot_date < expected_date:
                # Gap found
                break

        return streak

    def _calculate_best_streak(self, sorted_snapshots: List[ProgressSnapshot]) -> int:
        """Calculate longest consecutive day streak in history"""
        if not sorted_snapshots:
            return 0

        best_streak = 1
        current_streak = 1

        for i in range(1, len(sorted_snapshots)):
            prev_date = sorted_snapshots[i - 1].date
            curr_date = sorted_snapshots[i].date

            if (curr_date - prev_date).days == 1:
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 1

        return best_streak

    # ==================== Stagnation Detection ====================

    async def detect_stagnation(self, user_id: str, threshold_days: int = 7) -> Optional[GoalInsight]:
        """Detect if user has stopped making progress"""
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker or not tracker.snapshots:
                return None

            # Get most recent snapshot
            most_recent = max(tracker.snapshots, key=lambda s: s.snapshot_date)
            days_since_last = (date.today() - most_recent.snapshot_date).days

            if days_since_last >= threshold_days:
                insight = GoalInsight(
                    insight_type="concern",
                    title=f"{days_since_last}일 동안 기록이 없습니다",
                    description=f"마지막 기록 이후 {days_since_last}일이 지났습니다. 작은 진전이라도 기록해보는 것은 어떨까요?",
                    actionable=True,
                    priority=2
                )

                logger.info(f"Detected stagnation for user {user_id}: {days_since_last} days")
                return insight

            return None

        except Exception as e:
            logger.error(f"Error detecting stagnation for {user_id}: {e}")
            return None

    # ==================== AI Insights Generation ====================

    async def generate_progress_insights(
        self,
        tracker: GoalProgressTracker,
        user_profile: Optional[UserProfile] = None
    ) -> List[GoalInsight]:
        """Generate AI-powered insights about user's progress"""
        try:
            insights = []

            # Build context for AI
            context = self._build_insight_context(tracker, user_profile)

            prompt = f"""You are a supportive goal achievement coach. Analyze this user's progress and provide 2-3 specific insights.

{context}

Generate insights that:
1. Acknowledge specific achievements or patterns
2. Offer actionable advice based on their progress
3. Are encouraging but realistic
4. Consider their emotional state and consistency

Return ONLY a JSON array of insights with this exact structure:
[
  {{
    "insight_type": "achievement|encouragement|concern|suggestion",
    "title": "Short title (max 50 chars)",
    "description": "Detailed insight (2-3 sentences)",
    "actionable": true/false,
    "priority": 0-2
  }},
  ...
]

Keep insights personal, specific, and motivating."""

            response = await self.gemini.generate_content(prompt)

            # Parse response
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()

            insights_data = json.loads(response_text)

            # Convert to GoalInsight objects
            for data in insights_data:
                insight = GoalInsight(
                    insight_type=data["insight_type"],
                    title=data["title"],
                    description=data["description"],
                    actionable=data.get("actionable", False),
                    priority=data.get("priority", 0)
                )
                insights.append(insight)

            # Update last insight generation time
            tracker.last_insight_generated = datetime.now()
            await self.db.save_goal_progress(tracker)

            logger.info(f"Generated {len(insights)} insights for user {tracker.user_id}")
            return insights

        except Exception as e:
            logger.error(f"Error generating progress insights: {e}")
            return []

    def _build_insight_context(
        self,
        tracker: GoalProgressTracker,
        user_profile: Optional[UserProfile]
    ) -> str:
        """Build context string for AI insight generation"""
        context_parts = [
            f"Goal: {tracker.one_thing}",
            f"Started: {tracker.start_date.isoformat()}",
            f"Days since start: {tracker.days_since_start()}",
        ]

        if tracker.target_date:
            context_parts.append(f"Target date: {tracker.target_date.isoformat()}")
            days_remaining = tracker.days_until_target()
            if days_remaining is not None:
                context_parts.append(f"Days remaining: {days_remaining}")

        # Progress stats
        completion = tracker.get_completion_percentage()
        context_parts.append(f"Completion: {completion:.1f}%")
        context_parts.append(f"Total snapshots: {len(tracker.snapshots)}")

        # Trend analysis
        if tracker.current_trend:
            trend = tracker.current_trend
            context_parts.append(f"Trend direction: {trend.direction}")
            context_parts.append(f"Current streak: {trend.current_streak} days")
            context_parts.append(f"Best streak: {trend.best_streak} days")
            context_parts.append(f"Consistency score: {trend.consistency_score:.2f}")
            if trend.avg_mood:
                context_parts.append(f"Average mood: {trend.avg_mood:.1f}/5")

        # Recent snapshot
        if tracker.snapshots:
            recent = max(tracker.snapshots, key=lambda s: s.snapshot_date)
            context_parts.append(f"Most recent entry: {recent.snapshot_date.isoformat()}")
            if recent.reflection:
                context_parts.append(f"Recent reflection: {recent.reflection}")

        # User profile context
        if user_profile:
            if user_profile.core_pitfall:
                context_parts.append(f"User's core pitfall: {user_profile.core_pitfall.value}")

            top_traits = user_profile.get_top_traits(3)
            if top_traits:
                traits_str = ", ".join([t.name for t in top_traits])
                context_parts.append(f"Personality traits: {traits_str}")

        return "\n".join(context_parts)

    def _build_user_context(self, user_profile: UserProfile) -> str:
        """Build user context string for milestone generation"""
        context_parts = []

        if user_profile.core_pitfall:
            context_parts.append(f"User tends to: {user_profile.core_pitfall.value}")

        top_traits = user_profile.get_top_traits(3)
        if top_traits:
            traits_str = ", ".join([t.name for t in top_traits])
            context_parts.append(f"Personality: {traits_str}")

        return " ".join(context_parts) if context_parts else ""

    # ==================== Milestone Management ====================

    async def complete_milestone(self, user_id: str, milestone_id: str) -> bool:
        """Mark a milestone as completed"""
        return await self.db.update_milestone(user_id, milestone_id, True)

    async def uncomplete_milestone(self, user_id: str, milestone_id: str) -> bool:
        """Unmark a milestone"""
        return await self.db.update_milestone(user_id, milestone_id, False)

    async def add_custom_milestone(
        self,
        user_id: str,
        description: str,
        target_date: Optional[date] = None,
        reward: Optional[str] = None
    ) -> bool:
        """Add a custom milestone to the goal"""
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                logger.warning(f"Cannot add milestone - no tracker found for {user_id}")
                return False

            milestone = Milestone(
                milestone_id=str(uuid.uuid4()),
                description=description,
                target_date=target_date,
                reward=reward,
                order=len(tracker.milestones) + 1
            )

            tracker.add_milestone(milestone)
            return await self.db.save_goal_progress(tracker)

        except Exception as e:
            logger.error(f"Error adding custom milestone for {user_id}: {e}")
            return False

    # ==================== Retrieval Methods ====================

    async def get_goal_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive goal summary with insights"""
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                return None

            # Get user profile for context
            user_profile = await self.db.get_user_profile(user_id)

            # Generate fresh insights if needed
            insights = []
            if not tracker.last_insight_generated or \
               (datetime.now() - tracker.last_insight_generated).days >= 7:
                insights = await self.generate_progress_insights(tracker, user_profile)

            # Check for stagnation
            stagnation_insight = await self.detect_stagnation(user_id)
            if stagnation_insight:
                insights.append(stagnation_insight)

            summary = {
                "goal": tracker.one_thing,
                "goal_id": tracker.goal_id,
                "start_date": tracker.start_date.isoformat(),
                "target_date": tracker.target_date.isoformat() if tracker.target_date else None,
                "days_active": tracker.days_since_start(),
                "days_remaining": tracker.days_until_target(),
                "completion_percentage": tracker.get_completion_percentage(),
                "total_entries": len(tracker.snapshots),
                "milestones": {
                    "total": len(tracker.milestones),
                    "completed": sum(1 for m in tracker.milestones if m.is_completed),
                    "upcoming": [
                        {
                            "id": m.milestone_id,
                            "description": m.description,
                            "target_date": m.target_date.isoformat() if m.target_date else None,
                            "days_until": m.days_until_target()
                        }
                        for m in sorted(tracker.milestones, key=lambda x: x.order)
                        if not m.is_completed
                    ][:3]  # Next 3 milestones
                },
                "trend": tracker.current_trend.dict() if tracker.current_trend else None,
                "insights": [
                    {
                        "type": i.insight_type,
                        "title": i.title,
                        "description": i.description,
                        "actionable": i.actionable,
                        "priority": i.priority
                    }
                    for i in sorted(insights, key=lambda x: x.priority, reverse=True)
                ],
                "recent_snapshot": None
            }

            # Add most recent snapshot if available
            if tracker.snapshots:
                recent = max(tracker.snapshots, key=lambda s: s.snapshot_date)
                summary["recent_snapshot"] = {
                    "date": recent.snapshot_date.isoformat(),
                    "reflection": recent.reflection,
                    "mood": recent.mood_rating,
                    "metrics": [
                        {
                            "name": m.name,
                            "value": m.value,
                            "unit": m.unit
                        }
                        for m in recent.metrics
                    ]
                }

            return summary

        except Exception as e:
            logger.error(f"Error getting goal summary for {user_id}: {e}")
            return None
