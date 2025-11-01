"""
API Request/Response Schemas for Project Eden V2
"""
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from utils.constants import PersonaType


# ============== Request Schemas ==============

class ChatRequest(BaseModel):
    """Request schema for /api/v2/chat endpoint"""
    user_id: str
    message: str
    voice_type: PersonaType
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class ProfileUpdateRequest(BaseModel):
    """Request schema for updating user profile"""
    one_thing: Optional[str] = None
    core_identity: Optional[str] = None
    core_motivation: Optional[str] = None
    manual_context: Optional[Dict[str, str]] = None


# ============== Response Schemas ==============

class ChatResponse(BaseModel):
    """Response schema for /api/v2/chat endpoint"""
    conversation_id: str
    response_text: str
    response_audio_url: Optional[str] = None
    response_audio_base64: Optional[str] = None
    pitfall_warning_triggered: bool = False
    emotional_support_mode: bool = False
    profile_updated: bool = False
    profile_version: int
    processing_time_ms: int
    tokens_used: Optional[Dict[str, int]] = None


class PersonalityTraitSummary(BaseModel):
    """Summary of a personality trait"""
    name: str
    weight: float


class ProfileResponse(BaseModel):
    """Response schema for /api/v2/profile/{user_id}"""
    user_id: str
    profile_version: int
    one_thing: Optional[str] = None
    core_pitfall: Optional[str] = None
    personality_summary: Dict[str, List[PersonalityTraitSummary]]
    recent_emotional_state: Optional[str] = None
    total_conversations: int
    profile_maturity: str
    last_updated: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LearningEventResponse(BaseModel):
    """Response schema for learning events"""
    event_id: str
    timestamp: datetime
    event_type: str
    description: str
    profile_version: int

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LearningEventsResponse(BaseModel):
    """Response schema for /api/v2/learning/events/{user_id}"""
    events: List[LearningEventResponse]


class HealthResponse(BaseModel):
    """Response schema for /health endpoint"""
    status: str
    version: str
    services: Dict[str, bool]
    uptime_seconds: int


# ============== Internal Analysis Schemas ==============

class DiscoveredTrait(BaseModel):
    """Trait discovered during conversation analysis"""
    name: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)


class ReinforcedTrait(BaseModel):
    """Existing trait reinforced during conversation"""
    name: str
    evidence: str


class EmotionalStateAnalysis(BaseModel):
    """Emotional state detected in conversation"""
    state: str
    trigger: str
    intensity: float = Field(ge=0.0, le=1.0)


class ConversationAnalysis(BaseModel):
    """Complete analysis of a conversation for learning"""
    discovered_traits: List[DiscoveredTrait] = Field(default_factory=list)
    reinforced_traits: List[ReinforcedTrait] = Field(default_factory=list)
    emotional_state: Optional[EmotionalStateAnalysis] = None
    main_topic: Optional[str] = None
    topic_alignment: float = Field(ge=0.0, le=1.0, default=0.0)
    goal_modification_detected: bool = False
    new_goal_hint: Optional[str] = None


class PitfallCheckResult(BaseModel):
    """Result of pitfall detection check"""
    warning_needed: bool
    reason: str
    detected_topic: Optional[str] = None
    alignment_score: float = 0.0
    warning_message: Optional[str] = None
