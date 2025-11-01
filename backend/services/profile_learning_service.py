"""
Profile Learning Service for Project Eden V2
Implements the Am-muk-ji (implicit knowledge) learning system
Inspired by neural network weight updates
"""
from datetime import datetime, timedelta
from typing import Optional

from models.user_profile import UserProfile, PersonalityTrait
from models.conversation import Conversation
from models.api_schemas import ConversationAnalysis
from services.llm_gemini_v2 import GeminiService
from services.dynamodb_service_v2 import DynamoDBService
from utils.logger import get_logger
from utils.constants import (
    LEARNING_RATE,
    DECAY_RATE,
    TIME_THRESHOLD_DAYS,
    MIN_TRAIT_WEIGHT,
    MAX_TRAIT_WEIGHT,
    LearningEventType
)

logger = get_logger(__name__)


class ProfileLearningService:
    """
    Service for learning from conversations and updating user profiles
    Core of the Am-muk-ji system
    """

    def __init__(self, llm_service: GeminiService, db_service: DynamoDBService):
        """Initialize learning service"""
        self.llm = llm_service
        self.db = db_service

        logger.info("Profile Learning Service initialized")

    async def learn_from_conversation(
        self,
        user_id: str,
        conversation: Conversation
    ) -> UserProfile:
        """
        Main learning pipeline - runs after every conversation
        Analyzes conversation and updates profile with new insights

        Args:
            user_id: User ID
            conversation: The conversation to learn from

        Returns:
            Updated user profile
        """
        try:
            logger.info(f"Starting learning pipeline for user {user_id}")

            # 1. Load current profile
            profile = await self.db.get_user_profile(user_id)
            if not profile:
                logger.error(f"Profile not found for user {user_id}")
                return None

            # 2. Extract user message and AI response from conversation
            user_message = ""
            ai_response = ""

            for msg in conversation.messages:
                if msg.role == "user":
                    user_message = msg.content
                elif msg.role == "assistant":
                    ai_response = msg.content

            if not user_message or not ai_response:
                logger.warning("Conversation missing user/AI messages, skipping learning")
                return profile

            # 3. Use Gemini to analyze conversation for insights
            analysis = await self.llm.analyze_for_learning(
                user_message=user_message,
                ai_response=ai_response,
                current_profile=profile
            )

            if not analysis:
                logger.warning("Learning analysis failed, profile not updated")
                return profile

            # 4. Process discovered traits
            for new_trait in analysis.discovered_traits:
                if new_trait.confidence > 0.6:
                    self._add_new_trait(profile, new_trait, conversation.conversation_id)

            # 5. Update existing trait weights
            for trait_update in analysis.reinforced_traits:
                self._update_trait_weight(profile, trait_update, conversation.conversation_id)

            # 6. Detect emotional state changes
            if analysis.emotional_state:
                profile.add_emotional_snapshot(
                    state=analysis.emotional_state.state,
                    trigger=analysis.emotional_state.trigger,
                    intensity=analysis.emotional_state.intensity
                )

                await self.db.log_learning_event(
                    user_id=user_id,
                    event_type=LearningEventType.EMOTIONAL_STATE_DETECTED,
                    description=f"Emotional state: {analysis.emotional_state.state} (intensity: {analysis.emotional_state.intensity:.2f})",
                    profile_version=profile.profile_version,
                    conversation_id=conversation.conversation_id
                )

            # 7. Update question patterns
            if analysis.main_topic:
                is_aligned = analysis.topic_alignment > 0.7
                profile.increment_question_pattern(
                    topic=analysis.main_topic,
                    is_aligned_with_one_thing=is_aligned
                )

            # 8. Check for goal evolution
            if analysis.goal_modification_detected:
                logger.warning(f"Goal modification detected: {analysis.new_goal_hint}")

                await self.db.log_learning_event(
                    user_id=user_id,
                    event_type=LearningEventType.GOAL_MODIFIED,
                    description=f"Possible goal change: {analysis.new_goal_hint}",
                    profile_version=profile.profile_version,
                    conversation_id=conversation.conversation_id
                )

            # 9. Apply time decay to all traits
            self._apply_time_decay(profile)

            # 10. Update metadata
            profile.profile_version += 1
            profile.last_updated = datetime.now()
            profile.meta_learning.total_conversations += 1
            profile.meta_learning.profile_updates += 1

            # 11. Save updated profile
            await self.db.save_user_profile(profile)

            # 12. Log learning event
            changes_summary = f"Discovered {len(analysis.discovered_traits)} new traits, reinforced {len(analysis.reinforced_traits)} traits"

            await self.db.log_learning_event(
                user_id=user_id,
                event_type=LearningEventType.PROFILE_UPDATED,
                description=changes_summary,
                profile_version=profile.profile_version,
                conversation_id=conversation.conversation_id,
                changes={
                    "discovered_traits": len(analysis.discovered_traits),
                    "reinforced_traits": len(analysis.reinforced_traits),
                    "emotional_state": analysis.emotional_state.state if analysis.emotional_state else None
                }
            )

            logger.info(f"Learning complete. Profile updated to v{profile.profile_version}")
            return profile

        except Exception as e:
            logger.error(f"Error in learning pipeline: {e}")
            return profile

    def _add_new_trait(
        self,
        profile: UserProfile,
        new_trait,
        conversation_id: str
    ):
        """Add a newly discovered personality trait"""
        trait_name = new_trait.name

        if trait_name not in profile.personality_traits:
            profile.add_trait(
                name=trait_name,
                initial_weight=new_trait.confidence,
                evidence=new_trait.evidence
            )

            logger.info(f"New trait discovered: {trait_name} (confidence: {new_trait.confidence:.2f})")

            # This would be logged separately in learn_from_conversation

    def _update_trait_weight(
        self,
        profile: UserProfile,
        trait_update,
        conversation_id: str
    ):
        """Update weight of an existing personality trait"""
        trait_name = trait_update.name
        current_trait = profile.get_trait(trait_name)

        if current_trait:
            old_weight = current_trait.weight

            # Calculate new weight using neural network-inspired update
            new_weight = self._calculate_new_weight(
                current_weight=current_trait.weight,
                evidence_strength=0.8,  # Could be calculated from evidence
                time_since_last_update=current_trait.days_since_update
            )

            current_trait.weight = new_weight
            current_trait.evidence_count += 1
            current_trait.last_updated = datetime.now()

            # Add recent evidence (keep only last 5)
            current_trait.recent_evidence.append(trait_update.evidence)
            if len(current_trait.recent_evidence) > 5:
                current_trait.recent_evidence = current_trait.recent_evidence[-5:]

            logger.debug(f"Updated {trait_name}: {old_weight:.2f} → {new_weight:.2f}")

    def _calculate_new_weight(
        self,
        current_weight: float,
        evidence_strength: float,
        time_since_last_update: int
    ) -> float:
        """
        Calculate new trait weight (neural network style)

        Args:
            current_weight: Current weight (0.0-1.0)
            evidence_strength: Strength of new evidence (0.0-1.0)
            time_since_last_update: Days since last update

        Returns:
            New weight (0.0-1.0)
        """
        # Apply time decay if trait hasn't been reinforced recently
        weight = current_weight

        if time_since_last_update > TIME_THRESHOLD_DAYS:
            decay_days = time_since_last_update - TIME_THRESHOLD_DAYS
            decay = DECAY_RATE * decay_days
            weight = max(MIN_TRAIT_WEIGHT, weight - decay)

        # Apply learning (positive reinforcement)
        delta = LEARNING_RATE * evidence_strength
        new_weight = min(MAX_TRAIT_WEIGHT, weight + delta)

        return new_weight

    def _apply_time_decay(self, profile: UserProfile):
        """
        Apply time decay to all personality traits
        Traits not reinforced recently should gradually decrease in weight
        """
        now = datetime.now()

        for trait_name, trait in profile.personality_traits.items():
            days_since = trait.days_since_update

            if days_since > TIME_THRESHOLD_DAYS:
                decay_days = days_since - TIME_THRESHOLD_DAYS
                decay = DECAY_RATE * decay_days

                old_weight = trait.weight
                trait.weight = max(MIN_TRAIT_WEIGHT, trait.weight - decay)

                if abs(old_weight - trait.weight) > 0.01:
                    logger.debug(f"Applied decay to {trait_name}: {old_weight:.2f} → {trait.weight:.2f} ({days_since} days)")
