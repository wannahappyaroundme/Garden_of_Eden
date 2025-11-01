"""
Pitfall Detection Service for Project Eden V2
Detects when user's requests stray from their "One Thing" goal
Implements the Benevolent Dissent system
"""
from typing import Optional

from models.user_profile import UserProfile
from models.api_schemas import PitfallCheckResult
from services.llm_gemini_v2 import GeminiService
from utils.logger import get_logger
from utils.constants import ALIGNMENT_THRESHOLD, PitfallReason

logger = get_logger(__name__)


class PitfallDetectionService:
    """Service for detecting when user is distracted from their One Thing"""

    def __init__(self, llm_service: GeminiService):
        """Initialize pitfall detection service"""
        self.llm = llm_service
        logger.info("Pitfall Detection Service initialized")

    async def check_for_pitfall(
        self,
        user_message: str,
        user_profile: UserProfile
    ) -> PitfallCheckResult:
        """
        Check if user's request triggers their Core Pitfall
        or has weak alignment with their One Thing

        Args:
            user_message: User's message/request
            user_profile: User's profile with One Thing and Core Pitfall

        Returns:
            PitfallCheckResult with warning details
        """
        try:
            # Check if profile has necessary information
            if not user_profile.one_thing:
                logger.debug("No One Thing set, skipping pitfall check")
                return PitfallCheckResult(
                    warning_needed=False,
                    reason=PitfallReason.ALIGNED,
                    alignment_score=1.0
                )

            one_thing = user_profile.one_thing.value

            # 1. Extract topic from user message
            detected_topic = await self.llm.extract_topic_from_text(user_message)

            # 2. Calculate alignment with One Thing
            alignment_score = await self._calculate_alignment(
                topic=detected_topic,
                one_thing=one_thing,
                user_message=user_message
            )

            logger.info(f"Topic: '{detected_topic}' | One Thing: '{one_thing}' | Alignment: {alignment_score:.2f}")

            # 3. Check if alignment is weak
            if alignment_score < ALIGNMENT_THRESHOLD:
                # Low alignment - potential distraction

                # 4. Check if it matches Core Pitfall pattern
                if user_profile.core_pitfall:
                    matches_pitfall = self._matches_pitfall_triggers(
                        topic=detected_topic,
                        user_message=user_message,
                        pitfall_triggers=user_profile.core_pitfall.triggers
                    )

                    if matches_pitfall:
                        # CORE PITFALL TRIGGERED - Strong warning
                        warning_message = self._generate_warning_message(
                            detected_topic=detected_topic,
                            one_thing=one_thing,
                            core_pitfall=user_profile.core_pitfall.value,
                            severity="high"
                        )

                        return PitfallCheckResult(
                            warning_needed=True,
                            reason=PitfallReason.CORE_PITFALL_TRIGGERED,
                            detected_topic=detected_topic,
                            alignment_score=alignment_score,
                            warning_message=warning_message
                        )

                # Weak alignment but not core pitfall - Gentle nudge
                warning_message = self._generate_warning_message(
                    detected_topic=detected_topic,
                    one_thing=one_thing,
                    core_pitfall=None,
                    severity="low"
                )

                return PitfallCheckResult(
                    warning_needed=True,
                    reason=PitfallReason.WEAK_ALIGNMENT,
                    detected_topic=detected_topic,
                    alignment_score=alignment_score,
                    warning_message=warning_message
                )

            # Good alignment - No warning needed
            return PitfallCheckResult(
                warning_needed=False,
                reason=PitfallReason.ALIGNED,
                detected_topic=detected_topic,
                alignment_score=alignment_score
            )

        except Exception as e:
            logger.error(f"Error in pitfall detection: {e}")
            # Default to no warning if error
            return PitfallCheckResult(
                warning_needed=False,
                reason=PitfallReason.ALIGNED,
                alignment_score=0.5
            )

    async def _calculate_alignment(
        self,
        topic: str,
        one_thing: str,
        user_message: str
    ) -> float:
        """
        Calculate how aligned the topic is with the One Thing
        Uses LLM to determine semantic similarity and relevance

        Args:
            topic: Extracted topic from user message
            one_thing: User's One Thing goal
            user_message: Full user message for context

        Returns:
            Alignment score (0.0 = no alignment, 1.0 = perfect alignment)
        """
        try:
            prompt = f"""
You are analyzing whether a user's request aligns with their primary goal.

User's Primary Goal (One Thing): "{one_thing}"

User's Current Topic/Request: "{topic}"
Full message: "{user_message}"

Task: Rate the alignment between the current topic and the primary goal.

Scoring:
- 1.0: Directly helps achieve the goal (e.g., goal is "SNU HCI Lab", topic is "HCI research methods")
- 0.7-0.9: Indirectly related or supporting skill (e.g., goal is "HCI Lab", topic is "React Native for HCI apps")
- 0.4-0.6: Tangentially related (e.g., goal is "HCI Lab", topic is "general UI design")
- 0.1-0.3: Unrelated but potentially relevant later (e.g., goal is "HCI Lab", topic is "machine learning basics")
- 0.0: Completely unrelated (e.g., goal is "HCI Lab", topic is "SLAM algorithms for robotics")

Return ONLY a number between 0.0 and 1.0, nothing else.
"""

            response = await self.llm.model.generate_content_async(prompt)
            score_text = response.text.strip()

            # Parse score
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))  # Clamp to 0-1
            except:
                logger.warning(f"Failed to parse alignment score: {score_text}")
                score = 0.5  # Default to neutral

            return score

        except Exception as e:
            logger.error(f"Error calculating alignment: {e}")
            return 0.5  # Default to neutral on error

    def _matches_pitfall_triggers(
        self,
        topic: str,
        user_message: str,
        pitfall_triggers: list
    ) -> bool:
        """
        Check if topic/message matches known pitfall triggers

        Args:
            topic: Extracted topic
            user_message: Full message
            pitfall_triggers: List of known trigger keywords

        Returns:
            True if matches a trigger
        """
        if not pitfall_triggers:
            return False

        topic_lower = topic.lower()
        message_lower = user_message.lower()

        for trigger in pitfall_triggers:
            trigger_lower = trigger.lower()

            if trigger_lower in topic_lower or trigger_lower in message_lower:
                logger.info(f"Pitfall trigger matched: '{trigger}' in topic/message")
                return True

        return False

    def _generate_warning_message(
        self,
        detected_topic: str,
        one_thing: str,
        core_pitfall: Optional[str],
        severity: str
    ) -> str:
        """
        Generate warning message text (used as hint for LLM)

        Args:
            detected_topic: What user is asking about
            one_thing: User's goal
            core_pitfall: User's pitfall (if matched)
            severity: "low" or "high"

        Returns:
            Warning message text
        """
        if severity == "high" and core_pitfall:
            return f"⚠️ CORE PITFALL DETECTED: Topic '{detected_topic}' matches your {core_pitfall}. This strays from your goal of '{one_thing}'."
        else:
            return f"Topic '{detected_topic}' has weak alignment with your goal '{one_thing}'. Consider if this is necessary now."
