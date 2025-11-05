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

            # 9.5. NEW: Adjust learning preferences based on conversation effectiveness
            # This is backpropagation-style learning: input (user Q) → output (AI A) → feedback signal
            self._adjust_learning_preferences(
                profile=profile,
                user_message=user_message,
                ai_response=ai_response,
                analysis=analysis
            )

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

    def _adjust_learning_preferences(
        self,
        profile: UserProfile,
        user_message: str,
        ai_response: str,
        analysis: ConversationAnalysis
    ):
        """
        Adjust learning preferences based on conversation effectiveness (backpropagation-style)

        This analyzes the input→output interaction to determine if the mentor's approach
        is working well for this user. Adjusts weights accordingly.

        Signals of POSITIVE mentor effectiveness:
        - User asks deeper follow-up questions (shows engagement)
        - User shows self-reflection in responses
        - User proposes own solutions
        - User demonstrates growth mindset language

        Signals of NEGATIVE mentor effectiveness:
        - User asks same question again (didn't understand)
        - User shows frustration or disengagement
        - User changes topic abruptly (wasn't helpful)
        - User gives very short responses (not engaged)

        Args:
            profile: User profile to update
            user_message: User's input
            ai_response: AI's response
            analysis: Conversation analysis results
        """
        # Learning rate for preference adjustments (smaller than trait learning rate)
        PREF_LEARNING_RATE = 0.05

        # Calculate feedback signals based on conversation analysis
        feedback_signals = self._calculate_feedback_signals(
            user_message=user_message,
            analysis=analysis
        )

        prefs = profile.learning_preferences

        # Adjust: prefers_questions_over_answers
        # Positive signal: User asks deeper questions, shows reflection
        # Negative signal: User seems confused, asks for direct answers
        if feedback_signals.get("shows_deep_thinking", False):
            prefs.prefers_questions_over_answers = min(1.0, prefs.prefers_questions_over_answers + PREF_LEARNING_RATE)
            logger.debug(f"Increased question preference: {prefs.prefers_questions_over_answers:.2f}")
        elif feedback_signals.get("seems_confused", False):
            prefs.prefers_questions_over_answers = max(0.0, prefs.prefers_questions_over_answers - PREF_LEARNING_RATE)
            logger.debug(f"Decreased question preference: {prefs.prefers_questions_over_answers:.2f}")

        # Adjust: responds_to_encouragement
        # Positive signal: User shows increased motivation after encouragement
        # Negative signal: User ignores encouragement, stays focused on logic
        if feedback_signals.get("motivated_by_encouragement", False):
            prefs.responds_to_encouragement = min(1.0, prefs.responds_to_encouragement + PREF_LEARNING_RATE)
            logger.debug(f"Increased encouragement response: {prefs.responds_to_encouragement:.2f}")
        elif feedback_signals.get("ignores_encouragement", False):
            prefs.responds_to_encouragement = max(0.0, prefs.responds_to_encouragement - PREF_LEARNING_RATE)

        # Adjust: needs_logical_structure
        # Positive signal: User follows structured approaches well
        # Negative signal: User prefers intuitive, flexible thinking
        if feedback_signals.get("follows_structure_well", False):
            prefs.needs_logical_structure = min(1.0, prefs.needs_logical_structure + PREF_LEARNING_RATE)
        elif feedback_signals.get("prefers_intuitive_flow", False):
            prefs.needs_logical_structure = max(0.0, prefs.needs_logical_structure - PREF_LEARNING_RATE)

        # Adjust: values_autonomy
        # Positive signal: User proposes own solutions, takes initiative
        # Negative signal: User asks for more guidance, wants direction
        if feedback_signals.get("proposes_own_solutions", False):
            prefs.values_autonomy = min(1.0, prefs.values_autonomy + PREF_LEARNING_RATE)
            logger.debug(f"Increased autonomy value: {prefs.values_autonomy:.2f}")
        elif feedback_signals.get("asks_for_direction", False):
            prefs.values_autonomy = max(0.0, prefs.values_autonomy - PREF_LEARNING_RATE)

        # Adjust: growth_mindset_strength
        # Positive signal: User frames challenges as learning opportunities
        # Negative signal: User shows fixed mindset language ("I can't", "I'm not good at")
        if feedback_signals.get("growth_mindset_language", False):
            prefs.growth_mindset_strength = min(1.0, prefs.growth_mindset_strength + PREF_LEARNING_RATE)
        elif feedback_signals.get("fixed_mindset_language", False):
            prefs.growth_mindset_strength = max(0.0, prefs.growth_mindset_strength - PREF_LEARNING_RATE)

        logger.info(f"Adjusted learning preferences for user (backpropagation-style)")

    def _calculate_feedback_signals(
        self,
        user_message: str,
        analysis: ConversationAnalysis
    ) -> dict:
        """
        Calculate feedback signals from user's message and conversation analysis

        These signals indicate how well the current mentor approach is working

        Returns:
            Dictionary of boolean signals
        """
        signals = {}
        msg_lower = user_message.lower()

        # Positive signals
        signals["shows_deep_thinking"] = any([
            "왜" in msg_lower and len(user_message) > 50,  # Asks "why" with detail
            "어떻게" in msg_lower and len(user_message) > 50,  # Asks "how" with detail
            "생각해보니" in msg_lower,  # "Now that I think about it"
            "깨달았" in msg_lower,  # "I realized"
            "패턴" in msg_lower,  # "pattern"
        ])

        signals["proposes_own_solutions"] = any([
            "시도해볼게요" in msg_lower,  # "I'll try"
            "해보겠습니다" in msg_lower,  # "I will do it"
            "이렇게 하면" in msg_lower,  # "If I do this"
            "방법은" in msg_lower and "?" not in msg_lower,  # States a method without asking
        ])

        signals["growth_mindset_language"] = any([
            "배우" in msg_lower,  # "learn"
            "성장" in msg_lower,  # "growth"
            "발전" in msg_lower,  # "development"
            "아직" in msg_lower and "못" in msg_lower,  # "not yet" (growth mindset)
        ])

        signals["motivated_by_encouragement"] = any([
            "감사합니다" in msg_lower and len(user_message) > 30,  # Thanks with detail
            "힘이 됩니다" in msg_lower,  # "That's encouraging"
            "해볼게요" in msg_lower,  # "I'll try" (after encouragement)
        ])

        signals["follows_structure_well"] = any([
            "단계" in msg_lower,  # "step"
            "순서" in msg_lower,  # "order"
            "먼저" in msg_lower and "그다음" in msg_lower,  # "first" and "then"
        ])

        # Negative signals
        signals["seems_confused"] = any([
            "무슨 말" in msg_lower,  # "What do you mean"
            "이해가 안" in msg_lower,  # "Don't understand"
            "다시 설명" in msg_lower,  # "Explain again"
            len(user_message) < 10,  # Very short response (disengaged)
        ])

        signals["asks_for_direction"] = any([
            "어떻게 해야" in msg_lower,  # "What should I do"
            "알려주" in msg_lower,  # "Tell me"
            "방법을 모르" in msg_lower,  # "Don't know how"
        ])

        signals["fixed_mindset_language"] = any([
            "못해" in msg_lower and "아직" not in msg_lower,  # "Can't" without "yet"
            "안 돼" in msg_lower,  # "Won't work"
            "원래" in msg_lower and ("이래" in msg_lower or "그래" in msg_lower),  # "I'm just like this"
        ])

        # Default False for signals not triggered
        for key in [
            "shows_deep_thinking", "proposes_own_solutions", "growth_mindset_language",
            "motivated_by_encouragement", "follows_structure_well", "seems_confused",
            "asks_for_direction", "fixed_mindset_language", "ignores_encouragement",
            "prefers_intuitive_flow"
        ]:
            signals.setdefault(key, False)

        return signals
