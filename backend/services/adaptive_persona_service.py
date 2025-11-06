"""
Adaptive Persona Service - Manages persona evolution (Mentor → Supporter → Friend)
Unified system where Adam/Eve differ only in voice, not personality
"""
from datetime import datetime
from typing import Dict, List, Optional
from models.user_profile import UserProfile
from services.llm_gemini_v2 import GeminiService
from prompts.onboarding_v3_prompts import ADAPTIVE_PERSONA_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)


class AdaptivePersonaService:
    """
    Manages adaptive persona evolution based on user interaction patterns

    Both Adam and Eve use the same adaptive persona system:
    - Mentor: Socratic, challenging, goal-focused (initial state)
    - Supporter: Encouraging, validating, celebrating progress
    - Friend: Casual, relatable, mutual growth

    Voice difference only: Adam = male voice, Eve = female voice
    """

    def __init__(self, llm_service: GeminiService):
        self.llm = llm_service
        self.config = ADAPTIVE_PERSONA_CONFIG
        logger.info("Adaptive Persona Service initialized")

    async def check_persona_evolution(
        self,
        profile: UserProfile,
        current_message: str,
        conversation_context: List[Dict[str, str]]
    ) -> Optional[str]:
        """
        Check if persona should evolve based on interaction patterns

        Args:
            profile: User's profile with interaction history
            current_message: Latest user message
            conversation_context: Recent conversation turns

        Returns:
            New persona mode if evolution should occur, None otherwise
        """
        current_mode = profile.current_persona_mode
        interaction_count = profile.meta_learning.total_conversations

        # Check evolution triggers
        triggers = self.config["evolution_triggers"]

        # Mentor → Supporter evolution
        if current_mode == "mentor":
            mentor_to_supporter = triggers["mentor_to_supporter"]

            if interaction_count >= mentor_to_supporter["interaction_count_min"]:
                conditions_met = await self._check_conditions(
                    profile,
                    current_message,
                    mentor_to_supporter["conditions"]
                )

                if conditions_met:
                    logger.info(f"User {profile.user_id}: Evolving Mentor → Supporter")
                    return "supporter"

        # Supporter → Friend evolution
        elif current_mode == "supporter":
            supporter_to_friend = triggers["supporter_to_friend"]

            if interaction_count >= supporter_to_friend["interaction_count_min"]:
                conditions_met = await self._check_conditions(
                    profile,
                    current_message,
                    supporter_to_friend["conditions"]
                )

                if conditions_met:
                    logger.info(f"User {profile.user_id}: Evolving Supporter → Friend")
                    return "friend"

        # Friend → Mentor evolution (back to directive when needed)
        elif current_mode == "friend":
            friend_to_mentor = triggers["friend_to_mentor"]

            if interaction_count >= friend_to_mentor["interaction_count_min"]:
                conditions_met = await self._check_conditions(
                    profile,
                    current_message,
                    friend_to_mentor["conditions"]
                )

                if conditions_met:
                    logger.info(f"User {profile.user_id}: Returning Friend → Mentor")
                    return "mentor"

        return None

    async def _check_conditions(
        self,
        profile: UserProfile,
        current_message: str,
        conditions: List[str]
    ) -> bool:
        """
        Check if evolution conditions are met

        Args:
            profile: User profile
            current_message: Current message
            conditions: List of condition strings to check

        Returns:
            True if conditions are met
        """
        for condition in conditions:
            if condition == "user_shows_vulnerability":
                if await self._detect_vulnerability(current_message):
                    profile.vulnerability_count += 1
                    return True

            elif condition == "user_expresses_frustration":
                if await self._detect_frustration(current_message):
                    return True

            elif condition == "user_shares_failure":
                if "실패" in current_message or "못했" in current_message or "안 됐" in current_message:
                    return True

            elif condition == "consecutive_setbacks >= 2":
                # Check meta learning for setbacks
                if profile.meta_learning.pitfall_warnings_given >= 2:
                    return True

            elif condition == "user_shares_personal_story":
                if len(current_message) > 100 and any(word in current_message for word in ["어렸을 때", "예전에", "저는", "경험"]):
                    return True

            elif condition == "user_asks_about_ai_opinion":
                if any(word in current_message for word in ["너는 어떻게 생각해", "네 의견", "어떻게 봐"]):
                    return True

            elif condition == "positive_interaction_streak >= 5":
                if profile.positive_interaction_streak >= 5:
                    return True

            elif condition == "trust_score >= 0.7":
                if profile.trust_score >= 0.7:
                    return True

            elif condition == "user_asks_for_direction":
                if any(word in current_message for word in ["어떻게 해야", "뭘 해야", "조언", "도와줘"]):
                    return True

            elif condition == "user_is_off_track":
                # This would be checked by pitfall detection
                pass

            elif condition == "pitfall_detected":
                # This would be set by pitfall detection service
                pass

            elif condition == "goal_progress_stagnant":
                # This would be checked by goal progress service
                pass

        return False

    async def _detect_vulnerability(self, message: str) -> bool:
        """Detect if user is showing vulnerability"""
        vulnerability_indicators = [
            "힘들어", "어려워", "모르겠어", "불안해", "걱정",
            "자신 없어", "두려워", "무서워", "슬퍼"
        ]
        return any(indicator in message for indicator in vulnerability_indicators)

    async def _detect_frustration(self, message: str) -> bool:
        """Detect frustration in message"""
        frustration_indicators = [
            "짜증", "답답", "막막", "안 돼", "왜 안", "계속 실패"
        ]
        return any(indicator in message for indicator in frustration_indicators)

    def get_persona_prompt_modifier(
        self,
        persona_mode: str,
        voice_type: str
    ) -> str:
        """
        Get prompt modifier for current persona mode and voice

        Args:
            persona_mode: Current mode (mentor/supporter/friend)
            voice_type: adam or eve

        Returns:
            Prompt text to inject into master directive
        """
        mode_config = self.config["persona_modes"].get(persona_mode, self.config["persona_modes"]["mentor"])
        voice_config = self.config["voice_differences"].get(voice_type, self.config["voice_differences"]["adam"])

        characteristics = mode_config["characteristics"]

        prompt = f"""
=== ADAPTIVE PERSONA MODE: {mode_config['name_en']} ({mode_config['name_kr']}) ===

Voice: {voice_config['voice_type']} ({voice_config['tone']})
Personality hint: {voice_config['personality_hints']}

Current Mode Characteristics:
- Description: {mode_config['description']}
- Questioning ratio: {characteristics['questioning_ratio']:.1f} (use questions {int(characteristics['questioning_ratio']*100)}% of the time)
- Directness level: {characteristics['directness']:.1f}/1.0
- Empathy level: {characteristics['empathy']:.1f}/1.0
- Challenge level: {characteristics['challenge_level']:.1f}/1.0

When to use this mode: {mode_config['when_to_use']}

IMPORTANT: Your personality adapts based on user needs, but your voice ({voice_config['voice_type']}) stays consistent.
"""
        return prompt

    def log_persona_evolution(
        self,
        profile: UserProfile,
        new_mode: str,
        trigger: str
    ):
        """
        Log persona evolution event

        Args:
            profile: User profile to update
            new_mode: New persona mode
            trigger: What triggered the evolution
        """
        evolution_event = {
            "mode": new_mode,
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger,
            "previous_mode": profile.current_persona_mode
        }

        profile.persona_mode_history.append(evolution_event)
        profile.current_persona_mode = new_mode
        profile.persona_evolution_readiness = 0.3  # Reset readiness

        logger.info(
            f"Persona evolved for user {profile.user_id}: "
            f"{evolution_event['previous_mode']} → {new_mode} "
            f"(trigger: {trigger})"
        )

    def update_interaction_metrics(
        self,
        profile: UserProfile,
        interaction_positive: bool,
        user_showed_vulnerability: bool = False
    ):
        """
        Update interaction metrics that influence persona evolution

        Args:
            profile: User profile to update
            interaction_positive: Whether interaction was positive
            user_showed_vulnerability: Whether user showed vulnerability
        """
        # Update positive interaction streak
        if interaction_positive:
            profile.positive_interaction_streak += 1
        else:
            profile.positive_interaction_streak = 0

        # Update vulnerability count
        if user_showed_vulnerability:
            profile.vulnerability_count += 1

        # Update trust score (slowly increases with positive interactions)
        if interaction_positive:
            profile.trust_score = min(1.0, profile.trust_score + 0.02)
        else:
            profile.trust_score = max(0.0, profile.trust_score - 0.01)

        # Update persona evolution readiness
        # Readiness increases with interaction count and positive interactions
        if interaction_positive:
            profile.persona_evolution_readiness = min(
                1.0,
                profile.persona_evolution_readiness + 0.05
            )
