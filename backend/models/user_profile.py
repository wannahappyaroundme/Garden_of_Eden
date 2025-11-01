"""
User Profile Models for Project Eden V2
Based on the Am-muk-ji (implicit knowledge) system with weighted traits
"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Evidence for a trait or characteristic"""
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(ge=0.0, le=1.0)


class CoreElement(BaseModel):
    """Core elements of user identity"""
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)


class PersonalityTrait(BaseModel):
    """Weighted personality trait (neural network style)"""
    name: str
    weight: float = Field(ge=0.0, le=1.0, default=0.5)
    last_updated: datetime = Field(default_factory=datetime.now)
    evidence_count: int = 0
    recent_evidence: List[str] = Field(default_factory=list, max_length=5)

    @property
    def days_since_update(self) -> int:
        """Calculate days since last update"""
        return (datetime.now() - self.last_updated).days


class CorePitfall(BaseModel):
    """User's core pitfall (biggest distraction pattern)"""
    value: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    triggers: List[str] = Field(default_factory=list)
    warning_phrases: List[str] = Field(default_factory=list)


class EmotionalSnapshot(BaseModel):
    """Snapshot of emotional state at a point in time"""
    date: datetime = Field(default_factory=datetime.now)
    state: str
    trigger: str
    intensity: float = Field(ge=0.0, le=1.0)


class EmotionalPatterns(BaseModel):
    """User's emotional patterns over time"""
    recent_states: List[EmotionalSnapshot] = Field(default_factory=list, max_length=20)
    common_triggers: List[str] = Field(default_factory=list)
    recovery_patterns: List[str] = Field(default_factory=list)


class QuestionPattern(BaseModel):
    """Pattern of questions user asks"""
    topic: str
    count: int = 0
    last_asked: datetime = Field(default_factory=datetime.now)
    trend: str = "stable"  # increasing, stable, decreasing
    flagged_as_distraction: bool = False


class SubGoal(BaseModel):
    """Sub-goal under the main One Thing"""
    description: str
    progress: float = Field(ge=0.0, le=1.0, default=0.0)
    deadline: Optional[datetime] = None
    completed: bool = False


class OneThing(BaseModel):
    """User's primary goal"""
    value: str
    target_date: Optional[datetime] = None
    confidence: float = Field(ge=0.0, le=1.0)
    sub_goals: List[SubGoal] = Field(default_factory=list)


class ChildhoodExperience(BaseModel):
    """Formative childhood experience"""
    description: str
    impact: str
    weight: float = Field(ge=0.0, le=1.0)


class LearningPreferences(BaseModel):
    """How user prefers to learn"""
    learning_style: str = "unknown"
    preferred_formats: List[str] = Field(default_factory=list)
    energy_peaks: List[str] = Field(default_factory=list)
    stress_response: str = "unknown"


class MetaLearning(BaseModel):
    """Metadata about the learning process"""
    total_conversations: int = 0
    profile_updates: int = 0
    pitfall_warnings_given: int = 0
    pitfall_warnings_heeded: int = 0
    emotional_support_sessions: int = 0
    learning_velocity: str = "unknown"


class UserProfile(BaseModel):
    """
    Complete user profile with Am-muk-ji (implicit knowledge)
    This is the living profile that grows with each conversation
    """
    user_id: str
    profile_version: int = 1
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    # Core Elements
    core_identity: Optional[CoreElement] = None
    core_motivation: Optional[CoreElement] = None
    one_thing: Optional[OneThing] = None
    core_pitfall: Optional[CorePitfall] = None

    # Personality Traits (weighted)
    personality_traits: Dict[str, PersonalityTrait] = Field(default_factory=dict)

    # Childhood Context
    childhood_experiences: List[ChildhoodExperience] = Field(default_factory=list)

    # Learning Preferences
    learning_preferences: LearningPreferences = Field(default_factory=LearningPreferences)

    # Emotional Patterns
    emotional_patterns: EmotionalPatterns = Field(default_factory=EmotionalPatterns)

    # Question Patterns
    question_patterns: Dict[str, QuestionPattern] = Field(default_factory=dict)

    # Meta Learning
    meta_learning: MetaLearning = Field(default_factory=MetaLearning)

    def get_trait(self, trait_name: str) -> Optional[PersonalityTrait]:
        """Get a specific personality trait"""
        return self.personality_traits.get(trait_name)

    def add_trait(self, name: str, initial_weight: float = 0.5, evidence: str = ""):
        """Add a new personality trait"""
        self.personality_traits[name] = PersonalityTrait(
            name=name,
            weight=initial_weight,
            evidence_count=1,
            recent_evidence=[evidence] if evidence else []
        )

    def add_emotional_snapshot(self, state: str, trigger: str, intensity: float):
        """Add an emotional state snapshot"""
        snapshot = EmotionalSnapshot(
            state=state,
            trigger=trigger,
            intensity=intensity
        )
        self.emotional_patterns.recent_states.append(snapshot)

        # Keep only last 20
        if len(self.emotional_patterns.recent_states) > 20:
            self.emotional_patterns.recent_states = self.emotional_patterns.recent_states[-20:]

    def increment_question_pattern(self, topic: str, is_aligned_with_one_thing: bool):
        """Track question patterns"""
        if topic not in self.question_patterns:
            self.question_patterns[topic] = QuestionPattern(topic=topic)

        pattern = self.question_patterns[topic]
        pattern.count += 1
        pattern.last_asked = datetime.now()

        if not is_aligned_with_one_thing:
            pattern.flagged_as_distraction = True

    def get_top_traits(self, top_n: int = 5) -> List[PersonalityTrait]:
        """Get top N personality traits by weight"""
        sorted_traits = sorted(
            self.personality_traits.values(),
            key=lambda t: t.weight,
            reverse=True
        )
        return sorted_traits[:top_n]

    def to_context_string(self) -> str:
        """Convert profile to context string for LLM prompts"""
        lines = []

        if self.core_identity:
            lines.append(f"[Core Identity]: {self.core_identity.value} (confidence: {self.core_identity.confidence:.2f})")

        if self.core_motivation:
            lines.append(f"[Core Motivation]: {self.core_motivation.value}")

        if self.one_thing:
            lines.append(f"[One Thing]: {self.one_thing.value}")

        if self.core_pitfall:
            lines.append(f"[Core Pitfall]: {self.core_pitfall.value}")
            if self.core_pitfall.triggers:
                lines.append(f"  Triggers: {', '.join(self.core_pitfall.triggers)}")

        # Top traits
        top_traits = self.get_top_traits(5)
        if top_traits:
            lines.append("\n[Top Personality Traits]:")
            for trait in top_traits:
                lines.append(f"  - {trait.name}: {trait.weight:.2f}")

        return "\n".join(lines)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
