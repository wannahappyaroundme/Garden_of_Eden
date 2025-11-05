"""
Session Manager for Project Eden V2
Manages active conversation sessions for continuous dialogue
"""
import uuid
from typing import Dict, Optional
from datetime import datetime

from models.session import ConversationSession, ConversationTurn, SessionInfo
from utils.constants import PersonaType
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages active conversation sessions"""

    def __init__(self):
        # In-memory storage for active sessions
        # In production, use Redis for scalability
        self.sessions: Dict[str, ConversationSession] = {}

    async def create_session(
        self,
        user_id: str,
        persona: PersonaType
    ) -> ConversationSession:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())

        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            persona=persona
        )

        self.sessions[session_id] = session

        logger.info(f"Created session {session_id} for user {user_id} with persona {persona}")
        return session

    async def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get active session by ID"""
        session = self.sessions.get(session_id)

        if session:
            # Check if expired
            if session.is_expired():
                logger.info(f"Session {session_id} has expired")
                session.close()
                return None

        return session

    async def get_or_create_session(
        self,
        user_id: str,
        persona: PersonaType,
        session_id: Optional[str] = None
    ) -> ConversationSession:
        """Get existing session or create new one"""
        if session_id:
            session = await self.get_session(session_id)
            if session and session.is_active:
                logger.info(f"Using existing session {session_id}")
                return session

        # Create new session
        logger.info(f"Creating new session for user {user_id}")
        return await self.create_session(user_id, persona)

    async def add_turn(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        processing_time_ms: int = 0
    ):
        """Add a conversation turn to session"""
        session = self.sessions.get(session_id)

        if not session:
            logger.warning(f"Attempted to add turn to non-existent session {session_id}")
            return

        session.add_turn(user_message, ai_response, processing_time_ms)
        logger.info(f"Added turn to session {session_id} (total turns: {len(session.turns)})")

    async def extend_timeout(self, session_id: str):
        """Extend session timeout (reset last_activity)"""
        session = self.sessions.get(session_id)

        if session:
            session.last_activity = datetime.now()
            logger.info(f"Extended timeout for session {session_id}")

    async def close_session(self, session_id: str, reason: str = "user_request"):
        """Close a session"""
        session = self.sessions.get(session_id)

        if session:
            session.close()
            logger.info(f"Closed session {session_id}, reason: {reason}")

    async def cleanup_expired_sessions(self):
        """Remove expired sessions from memory"""
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if session.is_expired() or not session.is_active:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    async def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get public session information"""
        session = self.sessions.get(session_id)

        if not session:
            return None

        return SessionInfo(
            session_id=session.session_id,
            user_id=session.user_id,
            persona=session.persona,
            turn_count=len(session.turns),
            created_at=session.created_at,
            last_activity=session.last_activity,
            is_active=session.is_active,
            is_expired=session.is_expired()
        )

    async def get_user_active_session(
        self,
        user_id: str
    ) -> Optional[ConversationSession]:
        """Get user's active session if exists"""
        for session in self.sessions.values():
            if session.user_id == user_id and session.is_active and not session.is_expired():
                return session

        return None

    def get_stats(self) -> dict:
        """Get session statistics"""
        total_sessions = len(self.sessions)
        active_sessions = sum(1 for s in self.sessions.values() if s.is_active and not s.is_expired())
        expired_sessions = sum(1 for s in self.sessions.values() if s.is_expired())

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions
        }
