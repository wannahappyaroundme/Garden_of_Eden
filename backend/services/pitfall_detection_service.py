"""
Pitfall Detection Service for Project Eden V2
Implements "Benevolent Dissent" - detecting when user strays from their "One Thing"
"""
from typing import Optional
from pydantic import BaseModel

from models.user_profile import UserProfile
from services.llm_gemini_v2 import GeminiService
from utils.logger import get_logger

logger = get_logger(__name__)


class PitfallCheck(BaseModel):
    """Result of pitfall detection"""
    warning_needed: bool
    detected_topic: Optional[str] = None
    alignment_score: float = 1.0  # 1.0 = fully aligned, 0.0 = completely off-track
    reason: Optional[str] = None


class PitfallDetectionService:
    """
    Detects when user conversation deviates from their "One Thing" goal
    Implements "Benevolent Dissent" feature
    """

    def __init__(self, llm_service: GeminiService):
        """Initialize pitfall detection service"""
        self.llm = llm_service
        logger.info("Pitfall Detection Service initialized")

    async def check_for_pitfall(
        self,
        user_message: str,
        user_profile: UserProfile
    ) -> PitfallCheck:
        """
        Check if user message deviates from their "One Thing" goal

        Args:
            user_message: Current user message
            user_profile: User's profile with "One Thing" goal

        Returns:
            PitfallCheck with warning status and details
        """
        # If no "One Thing" is set, no pitfall can be detected
        if not user_profile.one_thing:
            return PitfallCheck(
                warning_needed=False,
                alignment_score=1.0
            )

        try:
            # Use LLM to analyze alignment between message and "One Thing"
            prompt = f"""Analyze if the user's message is aligned with their stated goal.

User's Primary Goal ("One Thing"): {user_profile.one_thing}

User's Current Message: {user_message}

Instructions:
1. Calculate alignment score (0.0-1.0) where:
   - 1.0 = Fully aligned with the goal
   - 0.5-0.9 = Partially aligned or related
   - 0.0-0.4 = Off-track or distraction

2. If alignment < 0.3, identify what topic they're discussing instead

3. Provide brief reason for the score

Respond in this exact format:
SCORE: [number between 0.0 and 1.0]
TOPIC: [detected off-track topic or "aligned"]
REASON: [brief explanation]"""

            response = await self.llm.generate_text_only_response(
                prompt=prompt,
                max_tokens=200
            )

            # Parse response
            lines = response.strip().split('\n')
            score = 1.0
            topic = None
            reason = None

            for line in lines:
                if line.startswith("SCORE:"):
                    try:
                        score = float(line.split(":")[1].strip())
                    except (ValueError, IndexError):
                        score = 1.0
                elif line.startswith("TOPIC:"):
                    topic = line.split(":", 1)[1].strip()
                    if topic.lower() == "aligned":
                        topic = None
                elif line.startswith("REASON:"):
                    reason = line.split(":", 1)[1].strip()

            warning_needed = score < 0.3

            if warning_needed:
                logger.warning(f"Pitfall detected! Alignment score: {score:.2f}, Topic: {topic}")
            else:
                logger.info(f"No pitfall detected. Alignment score: {score:.2f}")

            return PitfallCheck(
                warning_needed=warning_needed,
                detected_topic=topic,
                alignment_score=score,
                reason=reason
            )

        except Exception as e:
            logger.error(f"Error in pitfall detection: {e}")
            # On error, don't trigger false warnings
            return PitfallCheck(
                warning_needed=False,
                alignment_score=1.0,
                reason=f"Detection error: {str(e)}"
            )
