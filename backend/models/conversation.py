"""
Conversation Models for Project Eden V2
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """Single message in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    audio_url: Optional[str] = None
    camera_frames: List[str] = Field(default_factory=list)  # S3 URLs


class Conversation(BaseModel):
    """Complete conversation record"""
    conversation_id: str
    user_id: str
    session_id: Optional[str] = None
    persona: str  # "adam" or "eve"
    messages: List[ConversationMessage] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Analysis Results
    pitfall_warning_triggered: bool = False
    pitfall_reason: Optional[str] = None
    emotional_support_mode: bool = False
    detected_emotional_state: Optional[str] = None
    main_topic: Optional[str] = None
    topic_alignment_score: float = 0.0

    # Performance Metrics
    processing_time_ms: Optional[int] = None
    tokens_used: Optional[dict] = None

    @property
    def full_text(self) -> str:
        """Get full conversation as text"""
        lines = []
        for msg in self.messages:
            role = "User" if msg.role == "user" else "AI"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LearningEvent(BaseModel):
    """Event logged when profile is updated through learning"""
    event_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str
    description: str
    profile_version: int
    conversation_id: Optional[str] = None
    changes: dict = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
