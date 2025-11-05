"""
Onboarding Service for Project Eden V2
Manages Socratic dialogue for initial profile setup
"""
import json
import uuid
from typing import Dict, Optional
from datetime import datetime

from models.onboarding import (
    OnboardingSession,
    OnboardingResult,
    OnboardingQuestion
)
from models.user_profile import UserProfile
from services.llm_gemini_v2 import GeminiService
from services.memory_db_service import MemoryDBService
from prompts.onboarding_prompts import (
    ONBOARDING_QUESTIONS,
    ONBOARDING_SYSTEM_PROMPT,
    EXTRACTION_PROMPT,
    generate_follow_up_prompt,
    get_question_by_step
)
from utils.constants import PersonaType
from utils.logger import get_logger

logger = get_logger(__name__)


class OnboardingService:
    """Manages onboarding conversations using Socratic method"""

    def __init__(self, llm_service: GeminiService, db_service: MemoryDBService):
        self.llm = llm_service
        self.db = db_service
        self.active_sessions: Dict[str, OnboardingSession] = {}

    async def start_onboarding(
        self,
        user_id: str,
        persona: PersonaType = PersonaType.ADAM
    ) -> OnboardingSession:
        """Start a new onboarding session"""
        session_id = str(uuid.uuid4())

        session = OnboardingSession(
            session_id=session_id,
            user_id=user_id,
            persona=persona,
            current_step=0
        )

        self.active_sessions[session_id] = session

        logger.info(f"Started onboarding session {session_id} for user {user_id}")
        return session

    async def get_first_question(self, session_id: str) -> str:
        """Get the first onboarding question"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        first_question = ONBOARDING_QUESTIONS[0]["question"]
        return first_question

    async def process_response(
        self,
        session_id: str,
        user_response: str
    ) -> dict:
        """Process user response and generate next question"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.completed:
            return {
                "completed": True,
                "message": "온보딩이 이미 완료되었습니다."
            }

        # Get current question data
        current_question_data = get_question_by_step(session.current_step + 1)
        current_question = current_question_data["question"]

        # Add turn to session
        session.add_turn(
            question=current_question,
            user_response=user_response
        )

        # Build conversation history
        conversation_history = self._build_conversation_history(session)

        # Determine if we need a follow-up or can move to next question
        if session.current_step < len(ONBOARDING_QUESTIONS):
            # Generate follow-up or next question
            next_question = await self._generate_next_question(
                session=session,
                user_response=user_response,
                conversation_history=conversation_history
            )

            return {
                "completed": False,
                "next_question": next_question,
                "step": session.current_step,
                "total_steps": len(ONBOARDING_QUESTIONS)
            }
        else:
            # All questions answered - extract profile
            result = await self._extract_and_save_profile(session)

            session.completed = True
            session.one_thing_identified = True

            return {
                "completed": True,
                "result": result,
                "message": "온보딩이 완료되었습니다! 이제 대화를 시작할 수 있습니다."
            }

    async def _generate_next_question(
        self,
        session: OnboardingSession,
        user_response: str,
        conversation_history: str
    ) -> str:
        """Generate next question using LLM"""
        # Check if response needs clarification
        response_length = len(user_response.strip())

        if response_length < 20:  # Very short response
            # Ask for more detail
            follow_up_prompt = generate_follow_up_prompt(
                step=session.current_step,
                user_response=user_response,
                conversation_history=conversation_history
            )

            next_question = await self.llm.generate_text_only_response(
                prompt=follow_up_prompt,
                max_tokens=300
            )

            return next_question

        # Move to next question
        next_step = session.current_step + 1

        if next_step < len(ONBOARDING_QUESTIONS):
            next_question_data = get_question_by_step(next_step + 1)
            return next_question_data["question"]
        else:
            return "감사합니다! 이제 당신에 대해 잘 알게 되었습니다."

    async def _extract_and_save_profile(
        self,
        session: OnboardingSession
    ) -> OnboardingResult:
        """Extract profile information from conversation and save"""
        conversation_history = self._build_conversation_history(session)

        # Use LLM to extract structured information
        extraction_prompt = EXTRACTION_PROMPT.format(
            conversation_history=conversation_history
        )

        extracted_json = await self.llm.generate_text_only_response(
            prompt=extraction_prompt,
            max_tokens=1000
        )

        # Parse JSON
        try:
            # Remove markdown code blocks if present
            if "```json" in extracted_json:
                extracted_json = extracted_json.split("```json")[1].split("```")[0].strip()
            elif "```" in extracted_json:
                extracted_json = extracted_json.split("```")[1].split("```")[0].strip()

            extracted_data = json.loads(extracted_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction JSON: {e}")
            # Fallback to defaults
            extracted_data = {
                "one_thing": "개인 성장",
                "core_motivation": "더 나은 사람이 되고 싶음",
                "core_pitfall": "불분명",
                "personality_hints": [],
                "summary": conversation_history[:500]
            }

        # Create result
        result = OnboardingResult(
            user_id=session.user_id,
            one_thing=extracted_data.get("one_thing", "개인 성장"),
            core_identity=None,  # Will be learned over time
            core_motivation=extracted_data.get("core_motivation"),
            personality_hints=extracted_data.get("personality_hints", []),
            conversation_summary=extracted_data.get("summary", "")
        )

        # Update user profile in database
        await self.db.update_profile_one_thing(
            user_id=session.user_id,
            one_thing=result.one_thing
        )

        logger.info(f"Onboarding completed for user {session.user_id}: {result.one_thing}")

        return result

    def _build_conversation_history(self, session: OnboardingSession) -> str:
        """Build formatted conversation history"""
        history_parts = []

        for i, turn in enumerate(session.turns, 1):
            history_parts.append(f"Q{i}: {turn.question}")
            history_parts.append(f"A{i}: {turn.user_response}")
            history_parts.append("")

        return "\n".join(history_parts)

    async def get_session(self, session_id: str) -> Optional[OnboardingSession]:
        """Get onboarding session by ID"""
        return self.active_sessions.get(session_id)

    async def delete_session(self, session_id: str):
        """Delete onboarding session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Deleted onboarding session {session_id}")
