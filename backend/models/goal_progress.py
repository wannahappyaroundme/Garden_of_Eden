"""
Goal Progress Tracking Models for Project Eden V2
Enables users to track progress toward their "One Thing" with metrics and milestones
"""
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class MetricType(str, Enum):
    """Types of metrics that can be tracked"""
    TIME = "time"  # Hours, minutes
    COUNT = "count"  # Number of times
    BOOLEAN = "boolean"  # Yes/No, Done/Not Done
    RATING = "rating"  # 1-5, 1-10 scale
    PERCENTAGE = "percentage"  # 0-100%
    CUSTOM = "custom"  # Custom metric


class MoodRating(int, Enum):
    """Mood rating scale"""
    VERY_LOW = 1
    LOW = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


class GoalMetric(BaseModel):
    """Individual metric measurement"""
    name: str  # e.g., "Study Hours", "Exercise Sessions"
    value: float  # Numeric value
    unit: str  # e.g., "hours", "sessions", "pages"
    metric_type: MetricType = MetricType.COUNT
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class Milestone(BaseModel):
    """Goal milestone/checkpoint"""
    milestone_id: str  # Unique identifier
    description: str  # e.g., "Complete first chapter"
    target_date: Optional[date] = None
    is_completed: bool = False
    completed_date: Optional[datetime] = None
    reward: Optional[str] = None  # Optional reward/celebration
    order: int = 0  # Order in sequence

    def mark_completed(self):
        """Mark milestone as completed"""
        self.is_completed = True
        self.completed_date = datetime.now()

    def days_until_target(self) -> Optional[int]:
        """Calculate days until target date"""
        if not self.target_date:
            return None
        delta = self.target_date - date.today()
        return delta.days


class ProgressSnapshot(BaseModel):
    """Single progress snapshot/entry"""
    snapshot_id: str  # Unique identifier
    snapshot_date: date = Field(default_factory=date.today)
    metrics: List[GoalMetric] = Field(default_factory=list)
    reflection: Optional[str] = None  # User's reflection on progress
    mood_rating: Optional[MoodRating] = None
    photo_url: Optional[str] = None  # Optional progress photo
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True

    def get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get value for specific metric"""
        for metric in self.metrics:
            if metric.name == metric_name:
                return metric.value
        return None


class ProgressTrend(BaseModel):
    """Analysis of progress trend"""
    direction: str  # "improving", "declining", "stable"
    velocity: float  # Rate of change
    consistency_score: float  # 0.0-1.0 (how consistent is progress)
    best_streak: int  # Longest consecutive days of progress
    current_streak: int  # Current consecutive days
    total_entries: int
    avg_mood: Optional[float] = None


class GoalInsight(BaseModel):
    """AI-generated insight about goal progress"""
    insight_type: str  # "achievement", "encouragement", "concern", "suggestion"
    title: str
    description: str
    actionable: bool = False  # Is this actionable advice?
    priority: int = 0  # 0=low, 1=medium, 2=high
    generated_at: datetime = Field(default_factory=datetime.now)


class GoalProgressTracker(BaseModel):
    """Main goal progress tracking model"""
    user_id: str
    goal_id: str  # Unique identifier for this goal
    one_thing: str  # The user's primary goal
    description: Optional[str] = None  # More detailed description

    # Timeframe
    start_date: date = Field(default_factory=date.today)
    target_date: Optional[date] = None

    # Progress tracking
    milestones: List[Milestone] = Field(default_factory=list)
    snapshots: List[ProgressSnapshot] = Field(default_factory=list)

    # Metrics configuration
    tracked_metrics: List[str] = Field(default_factory=list)  # Names of metrics to track
    metric_units: Dict[str, str] = Field(default_factory=dict)  # metric_name -> unit

    # Analysis
    current_trend: Optional[ProgressTrend] = None
    last_insight_generated: Optional[datetime] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = 1

    def add_snapshot(self, snapshot: ProgressSnapshot):
        """Add new progress snapshot"""
        self.snapshots.append(snapshot)
        self.snapshots.sort(key=lambda s: s.date, reverse=True)  # Most recent first
        self.updated_at = datetime.now()

    def add_milestone(self, milestone: Milestone):
        """Add new milestone"""
        self.milestones.append(milestone)
        self.milestones.sort(key=lambda m: m.order)
        self.updated_at = datetime.now()

    def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Get specific milestone by ID"""
        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id:
                return milestone
        return None

    def complete_milestone(self, milestone_id: str) -> bool:
        """Mark milestone as completed"""
        milestone = self.get_milestone(milestone_id)
        if milestone:
            milestone.mark_completed()
            self.updated_at = datetime.now()
            return True
        return False

    def get_recent_snapshots(self, days: int = 30) -> List[ProgressSnapshot]:
        """Get snapshots from last N days"""
        cutoff_date = date.today().replace(day=date.today().day - days)
        return [s for s in self.snapshots if s.date >= cutoff_date]

    def get_completion_percentage(self) -> float:
        """Calculate overall completion percentage based on milestones"""
        if not self.milestones:
            return 0.0
        completed = sum(1 for m in self.milestones if m.is_completed)
        return (completed / len(self.milestones)) * 100

    def days_since_start(self) -> int:
        """Days since goal started"""
        delta = date.today() - self.start_date
        return delta.days

    def days_until_target(self) -> Optional[int]:
        """Days until target date"""
        if not self.target_date:
            return None
        delta = self.target_date - date.today()
        return delta.days

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DynamoDB storage"""
        return {
            "user_id": self.user_id,
            "goal_id": self.goal_id,
            "one_thing": self.one_thing,
            "description": self.description,
            "start_date": self.start_date.isoformat(),
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "milestones": [m.dict() for m in self.milestones],
            "snapshots": [s.dict() for s in self.snapshots],
            "tracked_metrics": self.tracked_metrics,
            "metric_units": self.metric_units,
            "current_trend": self.current_trend.dict() if self.current_trend else None,
            "last_insight_generated": self.last_insight_generated.isoformat() if self.last_insight_generated else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoalProgressTracker":
        """Create from dictionary (DynamoDB format)"""
        # Convert ISO date strings back to date/datetime objects
        if data.get("start_date"):
            data["start_date"] = date.fromisoformat(data["start_date"])
        if data.get("target_date"):
            data["target_date"] = date.fromisoformat(data["target_date"])
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("last_insight_generated"):
            data["last_insight_generated"] = datetime.fromisoformat(data["last_insight_generated"])

        # Convert milestone dicts to Milestone objects
        if data.get("milestones"):
            data["milestones"] = [Milestone(**m) for m in data["milestones"]]

        # Convert snapshot dicts to ProgressSnapshot objects
        if data.get("snapshots"):
            data["snapshots"] = [ProgressSnapshot(**s) for s in data["snapshots"]]

        # Convert trend dict to ProgressTrend object
        if data.get("current_trend"):
            data["current_trend"] = ProgressTrend(**data["current_trend"])

        return cls(**data)


class GoalProgressResponse(BaseModel):
    """API response for goal progress"""
    tracker: GoalProgressTracker
    insights: List[GoalInsight] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
