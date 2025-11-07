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
from models.rag_models import RAGQuery
from models.search_models import SearchQuery
from services.dynamodb_service_v2 import DynamoDBService
from services.llm_gemini_v2 import GeminiService
from services.stt_service import STTService
from services.tts_service import TTSService
from services.profile_learning_service import ProfileLearningService
from services.pitfall_detection_service import PitfallDetectionService
from services.retrieval_augmented_generation_service import RAGService
from services.web_search_service import WebSearchService
from services.session_manager import SessionManager
from services.goal_progress_service import GoalProgressService
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
        tts_service: TTSService,
        session_manager: Optional[SessionManager] = None,
        goal_progress_service: Optional[GoalProgressService] = None
    ):
        """Initialize Master Directive Processor with RAG, WebSearch, and Goal Tracking"""
        self.db = db_service
        self.llm = llm_service
        self.stt = stt_service
        self.tts = tts_service
        self.session_manager = session_manager
        self.goal_service = goal_progress_service

        # Initialize sub-services
        self.learning_service = ProfileLearningService(llm_service, db_service)
        self.pitfall_service = PitfallDetectionService(llm_service)

        # Initialize RAG service for semantic memory
        try:
            self.rag_service = RAGService(persist_directory="./chroma_db")
            logger.info("✅ RAG service initialized")
        except Exception as e:
            logger.warning(f"⚠️ RAG service initialization failed: {e}. Continuing without RAG.")
            self.rag_service = None

        # Initialize WebSearch service
        try:
            self.web_search_service = WebSearchService()
            logger.info("✅ WebSearch service initialized")
        except Exception as e:
            logger.warning(f"⚠️ WebSearch service initialization failed: {e}. Continuing without WebSearch.")
            self.web_search_service = None

        logger.info("Master Directive Processor initialized")

    async def process_conversation(
        self,
        user_id: str,
        message: str,
        voice_type: PersonaType,
        session_id: Optional[str] = None,
        camera_frames: Optional[List[Image.Image]] = None,
        audio_file_path: Optional[str] = None,
        wifi_available: bool = False
    ) -> ChatResponse:
        """
        Process a complete conversation through the Master Directive system with RAG and WebSearch

        Flow:
        1. Load user profile
        2. Load recent conversations
        3. RAG semantic search for similar past conversations
        4. WebSearch if WiFi available and query needs current info
        5. Check for pitfall (benevolent dissent)
        6. Detect emotional state
        7. Generate persona-aware response with full context
        8. Generate TTS audio
        9. Learn from conversation and embed for RAG
        10. Return response

        Args:
            user_id: User ID
            message: User's message (text)
            voice_type: Adam or Eve
            session_id: Optional session ID for multi-turn
            camera_frames: Optional camera images
            audio_file_path: Optional audio file for voice tone analysis
            wifi_available: Whether WiFi is connected (enables WebSearch)

        Returns:
            ChatResponse with AI response and metadata
        """
        start_time = datetime.now()

        try:
            logger.info(f"Processing conversation for user {user_id} with persona {voice_type.value}")

            # 1 & 2. Load user profile and conversation context IN PARALLEL
            import asyncio

            # Prepare tasks for parallel execution
            profile_task = self.db.get_or_create_profile(user_id)

            # Handle session logic
            active_session = None
            if self.session_manager and session_id:
                # Try to get existing session
                active_session = await self.session_manager.get_session(session_id)
                if active_session and not active_session.is_expired():
                    logger.info(f"Using active session {session_id} with {len(active_session.turns)} turns")
                    # Build recent conversations from session turns (synchronous)
                    recent_conversations_task = asyncio.create_task(asyncio.sleep(0))  # No-op task
                    profile = await profile_task
                    recent_conversations = self._build_conversations_from_session(active_session)
                else:
                    # Session expired or not found, load from DB in parallel with profile
                    logger.info("Session expired or not found, loading from database")
                    recent_conversations_task = self.db.get_recent_conversations(user_id, limit=10)
                    profile, recent_conversations = await asyncio.gather(profile_task, recent_conversations_task)
            else:
                # No session manager or session_id, load both from DB in parallel
                recent_conversations_task = self.db.get_recent_conversations(user_id, limit=10)
                profile, recent_conversations = await asyncio.gather(profile_task, recent_conversations_task)

            # 3. RAG: Semantic search for similar past conversations
            rag_context_string = "No semantic memory retrieved."
            if self.rag_service:
                try:
                    rag_query = RAGQuery(
                        query_text=message,
                        user_id=user_id,
                        k=5,  # Top 5 similar conversations
                        min_similarity=0.5
                    )
                    rag_results = await self.rag_service.search_similar_conversations(rag_query)

                    if rag_results.retrieved_conversations:
                        # Format RAG results for prompt
                        rag_lines = [f"Found {rag_results.total_results} semantically similar past conversations:"]
                        for i, conv in enumerate(rag_results.retrieved_conversations, 1):
                            rag_lines.append(f"\n{i}. (Similarity: {conv.similarity_score:.2f}) {conv.created_at.strftime('%Y-%m-%d')}")
                            rag_lines.append(f"   User: {conv.user_message[:100]}...")
                            rag_lines.append(f"   AI: {conv.ai_response[:100]}...")

                        rag_context_string = "\n".join(rag_lines)
                        logger.info(f"🔍 RAG retrieved {rag_results.total_results} similar conversations")
                except Exception as e:
                    logger.warning(f"RAG search failed: {e}")

            # 4. WebSearch: If WiFi available and query needs current info
            web_context_string = "No web search performed."
            if wifi_available and self.web_search_service:
                try:
                    # Check if search is needed
                    search_decision = self.web_search_service.should_trigger_search(message)

                    if search_decision.should_search:
                        logger.info(f"🌐 Triggering web search: {search_decision.reason}")

                        search_query = SearchQuery(
                            query_text=message,
                            max_results=3,
                            search_depth="basic"
                        )
                        search_results = await self.web_search_service.search(search_query)

                        if search_results.results:
                            web_context_string = self.web_search_service.format_search_results_for_prompt(search_results)
                            logger.info(f"🔍 WebSearch retrieved {search_results.total_results} results")
                        else:
                            web_context_string = "Web search performed but no results found."
                    else:
                        web_context_string = f"Web search not needed: {search_decision.reason}"
                except Exception as e:
                    logger.warning(f"WebSearch failed: {e}")

            # 5. Check for pitfall (benevolent dissent)
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

            # 6. Check goal progress and generate context
            goal_context_string = "No goal tracking info available."
            goal_progress_context = await self._check_goal_progress_context(user_id, profile)
            if goal_progress_context:
                goal_context_string = goal_progress_context
                logger.info("🎯 Goal progress context added to conversation")

            # 7. Generate AI response using Master Directive with full context
            ai_response = await self.llm.generate_response(
                user_message=message,
                user_profile=profile,
                persona=voice_type,
                recent_conversations=recent_conversations,
                camera_frames=camera_frames,
                pitfall_warning_mode=pitfall_warning_triggered,
                pitfall_details=pitfall_details,
                emotional_support_mode=emotional_support_mode,
                emotional_details=emotional_details,
                rag_context=rag_context_string,
                web_context=web_context_string,
                goal_context=goal_context_string
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

            # 8.5. Add turn to session if active
            if active_session:
                await self.session_manager.add_turn(
                    session_id=active_session.session_id,
                    user_message=message,
                    ai_response=ai_response,
                    processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
                logger.info(f"Added turn to session {active_session.session_id}")

            # 8.6 & 9. RAG embedding and learning in background (fire-and-forget)
            logger.info("Starting background tasks (RAG embedding + learning)...")
            import asyncio

            # RAG embedding in background
            if self.rag_service:
                async def embed_in_background():
                    try:
                        await self.rag_service.embed_and_store_conversation(conversation)
                        logger.info("✅ Conversation embedded for RAG")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to embed conversation for RAG: {e}")

                asyncio.create_task(embed_in_background())

            # Learning in background
            asyncio.create_task(self.learning_service.learn_from_conversation(
                user_id=user_id,
                conversation=conversation
            ))

            # Don't wait for learning - respond immediately
            profile_updated = False  # Will be updated in background
            new_version = profile.profile_version

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

    def _build_conversations_from_session(self, session) -> List[Conversation]:
        """
        Convert session turns into Conversation objects for context

        Args:
            session: ConversationSession

        Returns:
            List of Conversation objects
        """
        conversations = []
        for turn in session.turns:
            conversation = Conversation(
                conversation_id=f"session_{session.session_id}_{turn.timestamp.isoformat()}",
                user_id=session.user_id,
                session_id=session.session_id,
                persona=session.persona.value,
                messages=[
                    ConversationMessage(
                        role="user",
                        content=turn.user_message,
                        timestamp=turn.timestamp
                    ),
                    ConversationMessage(
                        role="assistant",
                        content=turn.ai_response,
                        timestamp=turn.timestamp
                    )
                ],
                processing_time_ms=turn.processing_time_ms
            )
            conversations.append(conversation)
        return conversations

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

    async def _check_goal_progress_context(self, user_id: str, profile: UserProfile) -> Optional[str]:
        """
        Check goal progress and generate context for AI if relevant

        Returns context string with goal progress info and reminders
        """
        if not self.goal_service:
            return None

        try:
            # Get goal tracker
            tracker = await self.db.get_goal_progress(user_id)

            if not tracker:
                # No goal set yet, suggest creating one if they have a One Thing
                if profile.one_thing and profile.one_thing.value:
                    return f"💡 Goal Context: User has a 'One Thing' ({profile.one_thing.value}) but hasn't created a goal tracker yet. Consider gently suggesting they track their progress."
                return None

            # Get stagnation alert
            stagnation_insight = await self.goal_service.detect_stagnation(user_id)

            # Build context
            context_parts = []

            # Basic progress info
            completion = tracker.get_completion_percentage()
            days_active = tracker.days_since_start()
            context_parts.append(f"🎯 Goal Progress: {tracker.one_thing}")
            context_parts.append(f"   - {completion:.1f}% complete")
            context_parts.append(f"   - {days_active} days active")

            # Days remaining
            days_remaining = tracker.days_until_target()
            if days_remaining is not None:
                if days_remaining < 0:
                    context_parts.append(f"   - ⚠️ {-days_remaining} days overdue!")
                elif days_remaining <= 7:
                    context_parts.append(f"   - ⏰ Only {days_remaining} days remaining!")
                else:
                    context_parts.append(f"   - {days_remaining} days remaining")

            # Trend info
            if tracker.current_trend:
                trend = tracker.current_trend
                context_parts.append(f"   - Trend: {trend.direction.upper()}")
                context_parts.append(f"   - Current streak: {trend.current_streak} days")

                if trend.current_streak == 0:
                    context_parts.append("   - ⚠️ Streak broken! Encourage them to restart.")
                elif trend.current_streak >= 7:
                    context_parts.append("   - 🔥 Great consistency! Celebrate this!")

            # Stagnation warning
            if stagnation_insight:
                context_parts.append(f"   - 🚨 {stagnation_insight.title}: {stagnation_insight.description}")

            # Upcoming milestones
            upcoming = tracker.upcomingMilestones()
            if upcoming:
                next_milestone = upcoming[0]
                context_parts.append(f"   - Next milestone: {next_milestone.description}")
                days_until = next_milestone.days_until_target()
                if days_until is not None and days_until <= 3:
                    context_parts.append(f"     ⏰ Due in {days_until} days!")

            # Recent snapshot
            recent = tracker.most_recent_snapshot()
            if recent:
                days_since = (datetime.now().date() - recent.date).days
                if days_since == 0:
                    context_parts.append("   - ✅ Logged progress today!")
                elif days_since == 1:
                    context_parts.append("   - Last logged: yesterday")
                else:
                    context_parts.append(f"   - Last logged: {days_since} days ago")
            else:
                context_parts.append("   - ℹ️ No progress entries yet. Encourage first entry!")

            # Proactive suggestions
            context_parts.append("\n📌 Proactive Goal Support:")

            if stagnation_insight:
                context_parts.append("   - Gently ask about their goal and offer to help record progress")
            elif days_active % 7 == 0 and days_active > 0:
                context_parts.append("   - It's been a week! Good time to reflect on progress")

            if tracker.current_trend and tracker.current_trend.direction == "declining":
                context_parts.append("   - Progress declining. Offer encouragement and help identify blockers")
            elif tracker.current_trend and tracker.current_trend.direction == "improving":
                context_parts.append("   - Progress improving! Celebrate wins and reinforce momentum")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error checking goal progress context: {e}")
            return None
