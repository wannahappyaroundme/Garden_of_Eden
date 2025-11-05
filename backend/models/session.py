"""
Conversation Session Models for Project Eden V2
"""
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
from utils.constants import PersonaType


class ConversationTurn(BaseModel):
    """A single turn in a conversation"""
    user_message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: int = 0


class ConversationSession(BaseModel):
    """Active conversation session"""
    session_id: str
    user_id: str
    persona: PersonaType
    turns: List[ConversationTurn] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    timeout_minutes: int = 10
    is_active: bool = True

    def is_expired(self) -> bool:
        """Check if session has expired"""
        timeout = timedelta(minutes=self.timeout_minutes)
        return datetime.now() - self.last_activity > timeout

    def add_turn(self, user_message: str, ai_response: str, processing_time_ms: int = 0):
        """Add a conversation turn"""
        self.turns.append(ConversationTurn(
            user_message=user_message,
            ai_response=ai_response,
            processing_time_ms=processing_time_ms
        ))
        self.last_activity = datetime.now()

    def get_recent_turns(self, limit: int = 5) -> List[ConversationTurn]:
        """Get recent conversation turns"""
        return self.turns[-limit:] if len(self.turns) > limit else self.turns

    def get_context_summary(self, limit: int = 5) -> str:
        """Get a summary of recent conversation for context"""
        recent = self.get_recent_turns(limit)
        context_parts = []

        for i, turn in enumerate(recent, 1):
            context_parts.append(f"Turn {i}:")
            context_parts.append(f"User: {turn.user_message}")
            context_parts.append(f"AI: {turn.ai_response[:100]}...")  # Truncate long responses
            context_parts.append("")

        return "\n".join(context_parts)

    def close(self):
        """Close the session"""
        self.is_active = False


class SessionInfo(BaseModel):
    """Public session information"""
    session_id: str
    user_id: str
    persona: PersonaType
    turn_count: int
    created_at: datetime
    last_activity: datetime
    is_active: bool
    is_expired: bool
