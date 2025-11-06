"""
Onboarding V3 Service - Personality Profiling + Adaptive Persona
Redesigned onboarding with structured personality assessment
"""
import json
import uuid
from typing import Dict, Optional
from datetime import datetime

from models.onboarding import OnboardingSession, OnboardingResult
from models.user_profile import UserProfile
from services.llm_gemini_v2 import GeminiService
from services.memory_db_service import MemoryDBService
from prompts.onboarding_v3_prompts import (
    ONBOARDING_V3_QUESTIONS,
    EXTRACTION_V3_PROMPT,
    ADAPTIVE_PERSONA_CONFIG,
    get_question_v3,
    calculate_learning_preferences,
    determine_initial_persona_mode
)
from utils.constants import PersonaType
from utils.logger import get_logger

logger = get_logger(__name__)


class OnboardingV3Service:
    """Manages onboarding V3 with personality profiling and adaptive persona"""

    def __init__(self, llm_service: GeminiService, db_service: MemoryDBService):
        self.llm = llm_service
        self.db = db_service
        self.active_sessions: Dict[str, dict] = {}  # session_id -> session data
        logger.info("Onboarding V3 Service initialized")

    async def start_onboarding(
        self,
        user_id: str,
        persona: PersonaType = PersonaType.ADAM
    ) -> dict:
        """
        Start new onboarding V3 session

        Returns:
            dict with session_id, first question, and metadata
        """
        session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "persona": persona,
            "current_step": 1,
            "total_steps": 6,
            "responses": {},  # step -> response data
            "context": {},  # Additional context (like user name)
            "started_at": datetime.now().isoformat(),
            "completed": False
        }

        self.active_sessions[session_id] = session_data

        # Get first question
        first_question = get_question_v3(1)

        logger.info(f"Started onboarding V3 session {session_id} for user {user_id}")

        return {
            "session_id": session_id,
            "question": first_question["question_kr"],
            "question_type": first_question["type"],
            "options": first_question.get("options"),  # For multiple choice
            "step": 1,
            "total_steps": 6
        }

    async def process_response(
        self,
        session_id: str,
        user_response: str,
        selected_option: Optional[str] = None
    ) -> dict:
        """
        Process user response to onboarding question

        Args:
            session_id: Active session ID
            user_response: User's text response
            selected_option: For multiple choice, the selected option value

        Returns:
            dict with next question or completion result
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session["completed"]:
            return {
                "completed": True,
                "message": "온보딩이 이미 완료되었습니다."
            }

        current_step = session["current_step"]
        current_question = get_question_v3(current_step, session["context"])

        # Store response
        response_data = {
            "question": current_question["question_kr"],
            "response": user_response,
            "type": current_question["type"]
        }

        # Handle different question types
        if current_question["type"] == "personal_info":
            # Extract name
            session["context"]["name"] = user_response.strip()
            response_data["extracted"] = {"name": user_response.strip()}

        elif current_question["type"] == "multiple_choice" and selected_option:
            # Find selected option details
            selected = next(
                (opt for opt in current_question["options"] if opt["value"] == selected_option),
                None
            )
            if selected:
                response_data["selected_option"] = selected
                response_data["traits"] = selected.get("traits", [])
                response_data["learning_prefs"] = selected.get("learning_prefs", {})
                response_data["pitfall_tendency"] = selected.get("pitfall_tendency")

        session["responses"][current_step] = response_data

        # Move to next step
        next_step = current_step + 1

        if next_step <= 6:
            # Get next question
            session["current_step"] = next_step
            next_question = get_question_v3(next_step, session["context"])

            return {
                "completed": False,
                "question": next_question["question_kr"],
                "question_type": next_question["type"],
                "options": next_question.get("options"),
                "step": next_step,
                "total_steps": 6
            }
        else:
            # All questions answered - extract profile
            result = await self._extract_and_create_profile(session)

            session["completed"] = True

            return {
                "completed": True,
                "result": result,
                "message": f"{session['context'].get('name', '님')}, 온보딩이 완료되었습니다! 이제 대화를 시작할 수 있습니다."
            }

    async def _extract_and_create_profile(self, session: dict) -> dict:
        """
        Extract profile from V3 onboarding responses

        Args:
            session: Complete session data with all responses

        Returns:
            Profile dict with personality traits, learning prefs, etc.
        """
        responses = session["responses"]

        # Build response summary for LLM
        response_summary = []
        for step, data in responses.items():
            response_summary.append(f"Q{step}: {data['question']}")
            response_summary.append(f"A{step}: {data['response']}")
            if "selected_option" in data:
                response_summary.append(f"   Selected: {data['selected_option']['label_kr']}")
            response_summary.append("")

        response_text = "\n".join(response_summary)

        # Use LLM to extract comprehensive profile
        try:
            extraction_prompt = EXTRACTION_V3_PROMPT.format(responses=response_text)

            extracted_json = await self.llm.generate_text_only_response(
                prompt=extraction_prompt,
                max_tokens=1500
            )

            # Parse JSON
            if "```json" in extracted_json:
                extracted_json = extracted_json.split("```json")[1].split("```")[0].strip()
            elif "```" in extracted_json:
                extracted_json = extracted_json.split("```")[1].split("```")[0].strip()

            profile_data = json.loads(extracted_json)

        except Exception as e:
            logger.error(f"Failed to extract profile via LLM: {e}")
            # Fallback to rule-based extraction
            profile_data = self._fallback_profile_extraction(session)

        # Calculate learning preferences from responses
        learning_prefs = calculate_learning_preferences(responses)
        profile_data["learning_preferences"] = learning_prefs

        # Determine initial persona mode
        initial_mode = determine_initial_persona_mode(responses, learning_prefs)
        profile_data["initial_persona_mode"] = initial_mode

        # Compile traits from multiple choice responses
        all_traits = {}
        for step, data in responses.items():
            if "traits" in data:
                for trait in data["traits"]:
                    # Accumulate trait confidence
                    all_traits[trait] = all_traits.get(trait, 0) + 0.25

        # Merge with LLM extracted traits
        if "personality_traits_weighted" in profile_data:
            for trait, confidence in profile_data["personality_traits_weighted"].items():
                all_traits[trait] = max(all_traits.get(trait, 0), confidence)

        profile_data["personality_traits_weighted"] = all_traits

        # Create/update user profile in database
        await self._update_user_profile(session["user_id"], profile_data)

        logger.info(f"Profile created for user {session['user_id']}: {profile_data.get('one_thing', 'N/A')}")

        return profile_data

    def _fallback_profile_extraction(self, session: dict) -> dict:
        """Fallback rule-based profile extraction if LLM fails"""
        responses = session["responses"]

        # Extract from structured responses
        profile = {
            "personal_info": {
                "name": session["context"].get("name", "User"),
                "preferred_language": "ko"
            },
            "one_thing": responses.get(5, {}).get("response", "개인 성장"),
            "core_pitfall": responses.get(6, {}).get("response", "불명확"),
            "thinking_style": responses.get(2, {}).get("selected_option", {}).get("value", "analytical"),
            "motivation_style": responses.get(3, {}).get("selected_option", {}).get("value", "growth"),
            "resilience_style": responses.get(4, {}).get("selected_option", {}).get("value", "problem_solver"),
            "initial_persona_mode": "mentor",
            "persona_evolution_readiness": 0.3,
            "summary": "Profile created from onboarding V3"
        }

        return profile

    async def _update_user_profile(self, user_id: str, profile_data: dict):
        """Update user profile in database with onboarding V3 data"""
        try:
            # Get or create profile
            try:
                existing_profile = await self.db.get_user_profile(user_id)
            except:
                # Create new profile
                existing_profile = await self.db.create_user_profile(user_id)

            # Update with onboarding data
            personal_info = profile_data.get("personal_info", {})
            if "name" in personal_info:
                existing_profile.name = personal_info["name"]

            existing_profile.one_thing = profile_data.get("one_thing")
            existing_profile.core_identity = profile_data.get("thinking_style")
            existing_profile.core_motivation = profile_data.get("core_motivation")

            # Update weighted traits
            traits = profile_data.get("personality_traits_weighted", {})
            for trait_name, confidence in traits.items():
                existing_profile.add_or_update_trait(
                    trait_name=trait_name,
                    initial_weight=confidence,
                    evidence=f"Onboarding V3: {trait_name}"
                )

            # Update learning preferences
            learning_prefs = profile_data.get("learning_preferences", {})
            if learning_prefs:
                existing_profile.learning_preferences.update(learning_prefs)

            # Store initial persona mode
            existing_profile.current_persona_mode = profile_data.get("initial_persona_mode", "mentor")
            existing_profile.persona_evolution_readiness = profile_data.get("persona_evolution_readiness", 0.3)

            # Save to database
            await self.db.update_user_profile(user_id, existing_profile)

            logger.info(f"Updated profile for user {user_id} with V3 onboarding data")

        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get active session by ID"""
        return self.active_sessions.get(session_id)

    async def delete_session(self, session_id: str):
        """Delete onboarding session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Deleted onboarding V3 session {session_id}")
