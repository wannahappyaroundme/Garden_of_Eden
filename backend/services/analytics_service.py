"""
Analytics Service for Project Eden V2
Provides data analysis and insights for goal progress tracking
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from collections import defaultdict
import statistics

from models.goal_progress import GoalProgressTracker, ProgressSnapshot, MoodRating
from services.dynamodb_service_v2 import DynamoDBService
from exceptions.goal_exceptions import GoalNotFoundException, InsufficientDataException
from utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analyzing goal progress data and generating analytics"""

    def __init__(self, db_service: DynamoDBService):
        self.db = db_service

    # ==================== Time Series Analysis ====================

    async def get_progress_timeline(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get time series data for progress visualization

        Returns:
            {
                "dates": ["2025-11-01", "2025-11-02", ...],
                "completion_trend": [10.5, 12.3, 15.0, ...],
                "mood_trend": [4, 5, 4, ...],
                "metrics": {
                    "Study Hours": [2.5, 3.0, 2.0, ...],
                    "Pages Read": [25, 30, 20, ...]
                },
                "daily_streaks": [1, 2, 3, 4, 0, 1, 2, ...]
            }
        """
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                raise GoalNotFoundException(user_id)

            if len(tracker.snapshots) < 2:
                raise InsufficientDataException(user_id, 2, len(tracker.snapshots))

            logger.info(
                f"Generating progress timeline",
                extra={"user_id": user_id, "days": days, "snapshots": len(tracker.snapshots)}
            )

            # Get snapshots within date range
            cutoff_date = date.today() - timedelta(days=days)
            recent_snapshots = [
                s for s in tracker.snapshots
                if s.snapshot_date >= cutoff_date
            ]
            recent_snapshots.sort(key=lambda s: s.snapshot_date)

            # Build time series
            dates = []
            completion_trend = []
            mood_trend = []
            metrics_by_name = defaultdict(list)
            daily_streaks = []

            # Calculate completion percentage over time
            start_date = tracker.start_date
            total_days = (tracker.target_date - start_date).days if tracker.target_date else 180

            current_streak = 0
            prev_date = None

            for snapshot in recent_snapshots:
                dates.append(snapshot.snapshot_date.isoformat())

                # Calculate completion at that point in time
                days_elapsed = (snapshot.snapshot_date - start_date).days
                estimated_completion = (days_elapsed / total_days) * 100 if total_days > 0 else 0
                completion_trend.append(round(estimated_completion, 1))

                # Mood
                mood_trend.append(snapshot.mood_rating.value if snapshot.mood_rating else None)

                # Metrics
                for metric in snapshot.metrics:
                    metrics_by_name[metric.name].append(metric.value)

                # Streak calculation
                if prev_date is None or (snapshot.snapshot_date - prev_date).days == 1:
                    current_streak += 1
                else:
                    current_streak = 1
                daily_streaks.append(current_streak)
                prev_date = snapshot.snapshot_date

            # Pad missing metrics with None
            max_length = len(dates)
            for metric_name in metrics_by_name:
                while len(metrics_by_name[metric_name]) < max_length:
                    metrics_by_name[metric_name].append(None)

            return {
                "dates": dates,
                "completion_trend": completion_trend,
                "mood_trend": mood_trend,
                "metrics": dict(metrics_by_name),
                "daily_streaks": daily_streaks,
                "total_entries": len(recent_snapshots)
            }

        except (GoalNotFoundException, InsufficientDataException):
            raise
        except Exception as e:
            logger.error(
                f"Error generating progress timeline",
                extra={"user_id": user_id, "error": str(e)}
            )
            raise

    # ==================== Statistical Analysis ====================

    async def get_progress_statistics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get statistical analysis of progress data

        Returns:
            {
                "mood_stats": {
                    "average": 4.2,
                    "median": 4.0,
                    "mode": 5,
                    "std_dev": 0.8
                },
                "consistency_score": 0.85,
                "velocity": 2.5,  # Average progress per day
                "most_productive_weekdays": ["Monday", "Wednesday"],
                "metrics_stats": {
                    "Study Hours": {
                        "average": 2.5,
                        "total": 75.0,
                        "trend": "improving"
                    }
                }
            }
        """
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                raise GoalNotFoundException(user_id)

            if len(tracker.snapshots) < 3:
                raise InsufficientDataException(user_id, 3, len(tracker.snapshots))

            logger.info(
                f"Calculating progress statistics",
                extra={"user_id": user_id, "days": days}
            )

            # Get recent snapshots
            cutoff_date = date.today() - timedelta(days=days)
            recent_snapshots = [
                s for s in tracker.snapshots
                if s.snapshot_date >= cutoff_date
            ]

            # Mood statistics
            mood_values = [
                s.mood_rating.value for s in recent_snapshots
                if s.mood_rating is not None
            ]

            mood_stats = {}
            if mood_values:
                mood_stats = {
                    "average": round(statistics.mean(mood_values), 2),
                    "median": statistics.median(mood_values),
                    "mode": statistics.mode(mood_values) if len(mood_values) > 1 else mood_values[0],
                    "std_dev": round(statistics.stdev(mood_values), 2) if len(mood_values) > 1 else 0.0,
                    "sample_size": len(mood_values)
                }

            # Consistency score (0-1): Based on streak and regularity
            if tracker.current_trend:
                consistency_score = tracker.current_trend.consistency_score
                velocity = tracker.current_trend.velocity
            else:
                consistency_score = 0.0
                velocity = 0.0

            # Most productive weekdays
            weekday_counts = defaultdict(int)
            for snapshot in recent_snapshots:
                weekday_name = snapshot.snapshot_date.strftime("%A")
                weekday_counts[weekday_name] += 1

            most_productive_weekdays = sorted(
                weekday_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            most_productive_weekdays = [day for day, _ in most_productive_weekdays]

            # Metrics statistics
            metrics_stats = {}
            tracked_metrics = tracker.tracked_metrics or []

            for metric_name in tracked_metrics:
                values = []
                for snapshot in recent_snapshots:
                    value = snapshot.get_metric_value(metric_name)
                    if value is not None:
                        values.append(value)

                if values:
                    # Calculate trend
                    if len(values) >= 3:
                        first_half_avg = statistics.mean(values[:len(values)//2])
                        second_half_avg = statistics.mean(values[len(values)//2:])

                        if second_half_avg > first_half_avg * 1.1:
                            trend = "improving"
                        elif second_half_avg < first_half_avg * 0.9:
                            trend = "declining"
                        else:
                            trend = "stable"
                    else:
                        trend = "stable"

                    metrics_stats[metric_name] = {
                        "average": round(statistics.mean(values), 2),
                        "total": round(sum(values), 2),
                        "max": max(values),
                        "min": min(values),
                        "trend": trend,
                        "sample_size": len(values)
                    }

            return {
                "mood_stats": mood_stats,
                "consistency_score": round(consistency_score, 2),
                "velocity": round(velocity, 2),
                "most_productive_weekdays": most_productive_weekdays,
                "metrics_stats": metrics_stats,
                "analysis_period_days": days,
                "total_snapshots_analyzed": len(recent_snapshots)
            }

        except (GoalNotFoundException, InsufficientDataException):
            raise
        except Exception as e:
            logger.error(
                f"Error calculating statistics",
                extra={"user_id": user_id, "error": str(e)}
            )
            raise

    # ==================== Pattern Detection ====================

    async def detect_patterns(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect behavioral patterns in progress data

        Returns:
            {
                "time_patterns": {
                    "most_active_time": "evening",
                    "least_active_time": "morning"
                },
                "streak_patterns": {
                    "longest_streak": 15,
                    "current_streak": 7,
                    "average_streak": 5.2
                },
                "mood_patterns": {
                    "mood_improving": true,
                    "mood_correlation_with_progress": 0.75
                },
                "productivity_patterns": [
                    "Most productive on Mondays",
                    "Struggles on Fridays",
                    "Evening sessions are 30% more effective"
                ]
            }
        """
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                raise GoalNotFoundException(user_id)

            if len(tracker.snapshots) < 5:
                raise InsufficientDataException(user_id, 5, len(tracker.snapshots))

            logger.info(
                f"Detecting behavioral patterns",
                extra={"user_id": user_id, "days": days}
            )

            # Get recent snapshots
            cutoff_date = date.today() - timedelta(days=days)
            recent_snapshots = [
                s for s in tracker.snapshots
                if s.snapshot_date >= cutoff_date
            ]
            recent_snapshots.sort(key=lambda s: s.snapshot_date)

            # Streak patterns
            streaks = []
            current_streak = 0
            prev_date = None

            for snapshot in tracker.snapshots:
                if prev_date is None or (snapshot.snapshot_date - prev_date).days == 1:
                    current_streak += 1
                else:
                    if current_streak > 0:
                        streaks.append(current_streak)
                    current_streak = 1
                prev_date = snapshot.snapshot_date

            if current_streak > 0:
                streaks.append(current_streak)

            streak_patterns = {
                "longest_streak": max(streaks) if streaks else 0,
                "current_streak": tracker.current_trend.current_streak if tracker.current_trend else 0,
                "average_streak": round(statistics.mean(streaks), 1) if streaks else 0.0,
                "total_streaks": len(streaks)
            }

            # Mood patterns
            mood_values = [
                (s.snapshot_date, s.mood_rating.value)
                for s in recent_snapshots
                if s.mood_rating is not None
            ]

            mood_improving = False
            if len(mood_values) >= 3:
                first_half = [m for _, m in mood_values[:len(mood_values)//2]]
                second_half = [m for _, m in mood_values[len(mood_values)//2:]]
                mood_improving = statistics.mean(second_half) > statistics.mean(first_half)

            mood_patterns = {
                "mood_improving": mood_improving,
                "average_mood_recent": round(statistics.mean([m for _, m in mood_values]), 2) if mood_values else None,
                "mood_volatility": round(statistics.stdev([m for _, m in mood_values]), 2) if len(mood_values) > 1 else 0.0
            }

            # Productivity patterns (weekday analysis)
            weekday_data = defaultdict(list)
            for snapshot in recent_snapshots:
                weekday = snapshot.snapshot_date.strftime("%A")
                # Count metrics as proxy for productivity
                productivity_score = len(snapshot.metrics)
                if snapshot.reflection:
                    productivity_score += 1
                weekday_data[weekday].append(productivity_score)

            productivity_by_weekday = {}
            for weekday, scores in weekday_data.items():
                productivity_by_weekday[weekday] = round(statistics.mean(scores), 2)

            # Generate insights
            productivity_patterns = []
            if productivity_by_weekday:
                most_productive = max(productivity_by_weekday.items(), key=lambda x: x[1])
                least_productive = min(productivity_by_weekday.items(), key=lambda x: x[1])

                productivity_patterns.append(f"{most_productive[0]}이(가) 가장 생산적입니다")
                productivity_patterns.append(f"{least_productive[0]}에 활동이 적습니다")

            if mood_improving:
                productivity_patterns.append("기분이 점차 개선되고 있습니다")

            if streak_patterns["current_streak"] >= 7:
                productivity_patterns.append(f"{streak_patterns['current_streak']}일 연속 기록 중입니다!")

            return {
                "streak_patterns": streak_patterns,
                "mood_patterns": mood_patterns,
                "productivity_by_weekday": productivity_by_weekday,
                "productivity_patterns": productivity_patterns,
                "analysis_period_days": days,
                "total_snapshots_analyzed": len(recent_snapshots)
            }

        except (GoalNotFoundException, InsufficientDataException):
            raise
        except Exception as e:
            logger.error(
                f"Error detecting patterns",
                extra={"user_id": user_id, "error": str(e)}
            )
            raise

    # ==================== Comparison Analysis ====================

    async def get_period_comparison(
        self,
        user_id: str,
        period1_days: int = 7,
        period2_days: int = 14
    ) -> Dict[str, Any]:
        """
        Compare two time periods (e.g., this week vs last week)

        Returns:
            {
                "period1": {
                    "start_date": "2025-11-01",
                    "end_date": "2025-11-07",
                    "avg_mood": 4.2,
                    "total_entries": 5,
                    "avg_metrics": {"Study Hours": 2.5}
                },
                "period2": {
                    ...
                },
                "comparison": {
                    "mood_change": "+5%",
                    "entries_change": "+20%",
                    "overall_trend": "improving"
                }
            }
        """
        try:
            tracker = await self.db.get_goal_progress(user_id)
            if not tracker:
                raise GoalNotFoundException(user_id)

            logger.info(
                f"Comparing periods",
                extra={
                    "user_id": user_id,
                    "period1_days": period1_days,
                    "period2_days": period2_days
                }
            )

            today = date.today()

            # Period 1: Most recent
            period1_start = today - timedelta(days=period1_days)
            period1_snapshots = [
                s for s in tracker.snapshots
                if period1_start <= s.snapshot_date <= today
            ]

            # Period 2: Previous period
            period2_end = period1_start - timedelta(days=1)
            period2_start = period2_end - timedelta(days=period2_days)
            period2_snapshots = [
                s for s in tracker.snapshots
                if period2_start <= s.snapshot_date <= period2_end
            ]

            def analyze_period(snapshots, start, end):
                mood_values = [s.mood_rating.value for s in snapshots if s.mood_rating]

                metrics_totals = defaultdict(float)
                for snapshot in snapshots:
                    for metric in snapshot.metrics:
                        metrics_totals[metric.name] += metric.value

                return {
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "avg_mood": round(statistics.mean(mood_values), 2) if mood_values else None,
                    "total_entries": len(snapshots),
                    "metrics_totals": dict(metrics_totals),
                    "has_reflection_rate": sum(1 for s in snapshots if s.reflection) / len(snapshots) if snapshots else 0.0
                }

            period1 = analyze_period(period1_snapshots, period1_start, today)
            period2 = analyze_period(period2_snapshots, period2_start, period2_end)

            # Calculate comparison
            comparison = {}

            if period1["avg_mood"] and period2["avg_mood"]:
                mood_change = ((period1["avg_mood"] - period2["avg_mood"]) / period2["avg_mood"]) * 100
                comparison["mood_change"] = f"{mood_change:+.1f}%"

            if period2["total_entries"] > 0:
                entries_change = ((period1["total_entries"] - period2["total_entries"]) / period2["total_entries"]) * 100
                comparison["entries_change"] = f"{entries_change:+.1f}%"

            # Overall trend
            improving_indicators = 0
            total_indicators = 0

            if period1["avg_mood"] and period2["avg_mood"]:
                total_indicators += 1
                if period1["avg_mood"] > period2["avg_mood"]:
                    improving_indicators += 1

            if period2["total_entries"] > 0:
                total_indicators += 1
                if period1["total_entries"] >= period2["total_entries"]:
                    improving_indicators += 1

            if total_indicators > 0:
                if improving_indicators / total_indicators >= 0.6:
                    comparison["overall_trend"] = "improving"
                elif improving_indicators / total_indicators <= 0.4:
                    comparison["overall_trend"] = "declining"
                else:
                    comparison["overall_trend"] = "stable"
            else:
                comparison["overall_trend"] = "insufficient_data"

            return {
                "period1": period1,
                "period2": period2,
                "comparison": comparison
            }

        except GoalNotFoundException:
            raise
        except Exception as e:
            logger.error(
                f"Error comparing periods",
                extra={"user_id": user_id, "error": str(e)}
            )
            raise
