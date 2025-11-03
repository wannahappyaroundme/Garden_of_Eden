"""
In-Memory Database Service for Local Testing
Simple dictionary-based storage to avoid DynamoDB setup
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from models.user_profile import UserProfile
from models.conversation import Conversation, LearningEvent
from utils.logger import get_logger

logger = get_logger(__name__)


class MemoryDBService:
    """In-memory database service for testing"""

    def __init__(self, **kwargs):
        self.profiles: Dict[str, UserProfile] = {}
        self.conversations: Dict[str, List[Conversation]] = {}
        self.learning_events: Dict[str, List[LearningEvent]] = {}
        logger.info("Memory DB service initialized (in-memory storage)")

    # ==================== User Profile Operations ====================

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user_id"""
        profile = self.profiles.get(user_id)
        if profile:
            logger.info(f"Retrieved profile for user {user_id}, version {profile.profile_version}")
        else:
            logger.info(f"Profile not found for user: {user_id}")
        return profile

    async def create_user_profile(self, user_id: str, one_thing: Optional[str] = None) -> UserProfile:
        """Create a new user profile"""
        profile = UserProfile(
            user_id=user_id,
            profile_version=1,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )

        if one_thing:
            profile.one_thing = one_thing

        self.profiles[user_id] = profile
        logger.info(f"Created new profile for user: {user_id}")
        return profile

    async def get_or_create_profile(self, user_id: str, one_thing: Optional[str] = None) -> UserProfile:
        """Get existing profile or create new one"""
        profile = await self.get_user_profile(user_id)
        if profile is None:
            profile = await self.create_user_profile(user_id, one_thing)
        return profile

    async def update_user_profile(self, profile: UserProfile) -> UserProfile:
        """Update an existing user profile"""
        profile.last_updated = datetime.now()
        profile.profile_version += 1
        self.profiles[profile.user_id] = profile
        logger.info(f"Updated profile for user {profile.user_id}, new version: {profile.profile_version}")
        return profile

    # ==================== Conversation Operations ====================

    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """Save a conversation"""
        if conversation.user_id not in self.conversations:
            self.conversations[conversation.user_id] = []
        self.conversations[conversation.user_id].append(conversation)
        logger.info(f"Saved conversation {conversation.conversation_id} for user {conversation.user_id}")
        return conversation

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Conversation]:
        """Get recent conversations for a user"""
        convs = self.conversations.get(user_id, [])
        # Return most recent first
        return sorted(convs, key=lambda x: x.created_at, reverse=True)[:limit]

    async def get_recent_conversations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Conversation]:
        """Get recent conversations for a user (alias for get_user_conversations)"""
        return await self.get_user_conversations(user_id, limit)

    # ==================== Learning Event Operations ====================

    async def save_learning_event(self, event: LearningEvent) -> LearningEvent:
        """Save a learning event"""
        if event.user_id not in self.learning_events:
            self.learning_events[event.user_id] = []
        self.learning_events[event.user_id].append(event)
        logger.info(f"Saved learning event for user {event.user_id}")
        return event

    async def get_learning_events(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[LearningEvent]:
        """Get learning events for a user"""
        events = self.learning_events.get(user_id, [])
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]

    # ==================== Profile Formatting ====================

    def format_profile_summary(self, profile: 'UserProfile') -> dict:
        """Format profile for API response"""
        from utils.constants import get_profile_maturity

        top_traits = profile.get_top_traits(5)

        recent_emotion = None
        if profile.emotional_patterns.recent_states:
            latest = profile.emotional_patterns.recent_states[-1]
            recent_emotion = f"{latest.state} ({latest.intensity:.1f})"

        return {
            "user_id": profile.user_id,
            "profile_version": profile.profile_version,
            "one_thing": profile.one_thing.value if profile.one_thing else None,
            "core_pitfall": profile.core_pitfall.value if profile.core_pitfall else None,
            "personality_summary": {
                "top_traits": [
                    {"name": trait.name, "weight": trait.weight}
                    for trait in top_traits
                ]
            },
            "recent_emotional_state": recent_emotion,
            "total_conversations": profile.meta_learning.total_conversations,
            "profile_maturity": get_profile_maturity(profile.meta_learning.total_conversations).value,
            "last_updated": profile.last_updated.isoformat()
        }
