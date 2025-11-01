"""
Master Directive Processor for Project Eden V2
Main orchestrator that coordinates all services to process conversations
"""
import uuid
from datetime import datetime
from typing import List, Optional
from PIL import Image

from models.user_profile import UserProfile
from models.conversation import Conversation, ConversationMessage
from models.api_schemas import ChatResponse
from services.dynamodb_service_v2 import DynamoDBService
from services.llm_gemini_v2 import GeminiService
from services.stt_service import STTService
from services.tts_service import TTSService
from services.profile_learning_service import ProfileLearningService
from services.pitfall_detection_service import PitfallDetectionService
from utils.logger import get_logger
from utils.constants import PersonaType, LearningEventType

logger = get_logger(__name__)


class MasterDirectiveProcessor:
    """
    Main service that orchestrates the entire conversation flow
    Implements the Master Directive system
    """

    def __init__(
        self,
        db_service: DynamoDBService,
        llm_service: GeminiService,
        stt_service: STTService,
        tts_service: TTSService
    ):
        """Initialize Master Directive Processor"""
        self.db = db_service
        self.llm = llm_service
        self.stt = stt_service
        self.tts = tts_service

        # Initialize sub-services
        self.learning_service = ProfileLearningService(llm_service, db_service)
        self.pitfall_service = PitfallDetectionService(llm_service)

        logger.info("Master Directive Processor initialized")

    async def process_conversation(
        self,
        user_id: str,
        message: str,
        voice_type: PersonaType,
        session_id: Optional[str] = None,
        camera_frames: Optional[List[Image.Image]] = None,
        audio_file_path: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a complete conversation through the Master Directive system

        Flow:
        1. Load user profile
        2. Check for pitfall (benevolent dissent)
        3. Detect emotional state
        4. Generate persona-aware response
        5. Generate TTS audio
        6. Learn from conversation (async)
        7. Return response

        Args:
            user_id: User ID
            message: User's message (text)
            voice_type: Adam or Eve
            session_id: Optional session ID for multi-turn
            camera_frames: Optional camera images
            audio_file_path: Optional audio file for voice tone analysis

        Returns:
            ChatResponse with AI response and metadata
        """
        start_time = datetime.now()

        try:
            logger.info(f"Processing conversation for user {user_id} with persona {voice_type.value}")

            # 1. Load user profile
            profile = await self.db.get_or_create_profile(user_id)

            # 2. Load recent conversations for context
            recent_conversations = await self.db.get_recent_conversations(user_id, limit=10)

            # 3. Check for pitfall (benevolent dissent)
            pitfall_check = await self.pitfall_service.check_for_pitfall(
                user_message=message,
                user_profile=profile
            )

            pitfall_warning_triggered = pitfall_check.warning_needed
            pitfall_details = None

            if pitfall_warning_triggered:
                pitfall_details = {
                    "detected_topic": pitfall_check.detected_topic,
                    "alignment_score": pitfall_check.alignment_score,
                    "reason": pitfall_check.reason
                }

                logger.warning(f"Pitfall warning triggered: {pitfall_check.reason}")

                # Log pitfall event
                await self.db.log_learning_event(
                    user_id=user_id,
                    event_type=LearningEventType.PITFALL_DETECTED,
                    description=f"Pitfall detected: {pitfall_check.detected_topic} (alignment: {pitfall_check.alignment_score:.2f})",
                    profile_version=profile.profile_version
                )

                # Track pitfall warning in profile
                profile.meta_learning.pitfall_warnings_given += 1

            # 4. Detect emotional state (simple heuristic for now)
            emotional_support_mode, emotional_details = self._detect_emotional_need(
                message=message,
                profile=profile
            )

            if emotional_support_mode:
                logger.info("Emotional support mode activated")

                # Track emotional support session
                profile.meta_learning.emotional_support_sessions += 1

            # 5. Generate AI response using Master Directive
            ai_response = await self.llm.generate_response(
                user_message=message,
                user_profile=profile,
                persona=voice_type,
                recent_conversations=recent_conversations,
                camera_frames=camera_frames,
                pitfall_warning_mode=pitfall_warning_triggered,
                pitfall_details=pitfall_details,
                emotional_support_mode=emotional_support_mode,
                emotional_details=emotional_details
            )

            # 6. Generate TTS audio
            logger.info("Generating TTS audio...")
            audio_base64 = await self.tts.generate_speech_base64(
                text=ai_response,
                persona=voice_type
            )

            # 7. Create conversation record
            conversation = Conversation(
                conversation_id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                persona=voice_type.value,
                messages=[
                    ConversationMessage(
                        role="user",
                        content=message,
                        timestamp=datetime.now()
                    ),
                    ConversationMessage(
                        role="assistant",
                        content=ai_response,
                        timestamp=datetime.now()
                    )
                ],
                pitfall_warning_triggered=pitfall_warning_triggered,
                pitfall_reason=pitfall_check.reason if pitfall_warning_triggered else None,
                emotional_support_mode=emotional_support_mode,
                detected_emotional_state=emotional_details.get('state') if emotional_details else None,
                main_topic=pitfall_check.detected_topic,
                topic_alignment_score=pitfall_check.alignment_score
            )

            # 8. Save conversation
            await self.db.save_conversation(conversation)

            # 9. Learn from conversation (async - don't wait)
            # In production, this would be a background task
            logger.info("Starting learning pipeline...")
            updated_profile = await self.learning_service.learn_from_conversation(
                user_id=user_id,
                conversation=conversation
            )

            profile_updated = updated_profile is not None
            new_version = updated_profile.profile_version if updated_profile else profile.profile_version

            # 10. Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000  # ms

            conversation.processing_time_ms = int(processing_time)

            # 11. Build response
            response = ChatResponse(
                conversation_id=conversation.conversation_id,
                response_text=ai_response,
                response_audio_base64=audio_base64,
                pitfall_warning_triggered=pitfall_warning_triggered,
                emotional_support_mode=emotional_support_mode,
                profile_updated=profile_updated,
                profile_version=new_version,
                processing_time_ms=int(processing_time),
                tokens_used=None  # Could track this if needed
            )

            logger.info(f"Conversation processed in {processing_time:.0f}ms")
            return response

        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            raise

    def _detect_emotional_need(
        self,
        message: str,
        profile: UserProfile
    ) -> tuple[bool, Optional[dict]]:
        """
        Detect if user is struggling emotionally (simple heuristic)

        In production, this would use more sophisticated NLP analysis

        Args:
            message: User's message
            profile: User profile

        Returns:
            (needs_support, emotional_details)
        """
        # Emotional keywords (Korean and English)
        stress_keywords = [
            "힘들", "어려워", "불안", "걱정", "두려", "무서",
            "tired", "anxious", "worried", "scared", "difficult",
            "지쳤", "포기", "못하겠", "안돼", "실패"
        ]

        message_lower = message.lower()

        for keyword in stress_keywords:
            if keyword in message_lower:
                logger.info(f"Emotional keyword detected: {keyword}")

                # Determine emotional state
                if any(k in message_lower for k in ["불안", "anxious", "worried", "걱정"]):
                    state = "anxious"
                elif any(k in message_lower for k in ["힘들", "tired", "지쳤"]):
                    state = "exhausted"
                elif any(k in message_lower for k in ["포기", "실패", "안돼", "못하겠"]):
                    state = "frustrated"
                else:
                    state = "stressed"

                return True, {
                    "state": state,
                    "trigger": "Expressed in message",
                    "intensity": 0.7
                }

        return False, None
