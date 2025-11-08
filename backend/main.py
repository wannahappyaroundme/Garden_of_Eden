"""
Project Eden V2 - Backend API
FastAPI application with Master Directive system
"""
import os
import time
import json
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from dotenv import load_dotenv
from PIL import Image
import io

from services.dynamodb_service_v2 import DynamoDBService
from services.memory_db_service import MemoryDBService
from services.llm_gemini_v2 import GeminiService
from services.stt_service import STTService
from services.tts_service import TTSService
from services.master_directive_processor import MasterDirectiveProcessor
from services.onboarding_service import OnboardingService
from services.onboarding_v3_service import OnboardingV3Service
from services.session_manager import SessionManager
from services.goal_progress_service import GoalProgressService
from services.analytics_service import AnalyticsService
from services.voice_customization_service import VoiceCustomizationService
from services.notification_service import NotificationService
from models.api_schemas import (
    ChatResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    LearningEventsResponse,
    LearningEventResponse,
    HealthResponse
)
from exceptions.goal_exceptions import (
    GoalProgressException,
    GoalNotFoundException,
    MilestoneNotFoundException,
    OneThingNotSetException,
    InvalidMetricsConfigException,
    InvalidMoodRatingException,
    InvalidDateFormatException,
    AIServiceException,
    DatabaseOperationException,
    InsufficientDataException
)
from utils.logger import get_logger
from utils.constants import PersonaType, get_profile_maturity

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

# App start time for uptime tracking
app_start_time = time.time()

# Global service instances
db_service: Optional[DynamoDBService] = None
llm_service: Optional[GeminiService] = None
analytics_service: Optional[AnalyticsService] = None
voice_customization_service: Optional[VoiceCustomizationService] = None
notification_service: Optional[NotificationService] = None
stt_service: Optional[STTService] = None
tts_service: Optional[TTSService] = None
master_processor: Optional[MasterDirectiveProcessor] = None
onboarding_service: Optional[OnboardingService] = None
onboarding_v3_service: Optional[OnboardingV3Service] = None
session_manager: Optional[SessionManager] = None
goal_progress_service: Optional[GoalProgressService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    global db_service, llm_service, stt_service, tts_service, master_processor, onboarding_service, onboarding_v3_service, session_manager, goal_progress_service, analytics_service, voice_customization_service, notification_service

    logger.info("Starting Project Eden V2 Backend...")

    try:
        # Initialize services - Use memory DB for local testing
        use_local = os.getenv("USE_LOCAL_DYNAMODB", "true").lower() == "true"
        if use_local:
            db_service = MemoryDBService()
        else:
            db_service = DynamoDBService(
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                profiles_table_name=os.getenv("DYNAMODB_PROFILES_TABLE", "eden_user_profiles_v2"),
                conversations_table_name=os.getenv("DYNAMODB_CONVERSATIONS_TABLE", "eden_conversations_raw"),
                learning_events_table_name=os.getenv("DYNAMODB_LEARNING_EVENTS_TABLE", "eden_learning_events")
            )

        llm_service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
        stt_service = STTService(api_key=os.getenv("GROQ_API_KEY"))
        tts_service = TTSService()

        # Initialize onboarding and session services
        onboarding_service = OnboardingService(
            llm_service=llm_service,
            db_service=db_service
        )
        onboarding_v3_service = OnboardingV3Service(
            llm_service=llm_service,
            db_service=db_service
        )
        session_manager = SessionManager()

        # Initialize goal progress service
        goal_progress_service = GoalProgressService(
            db_service=db_service,
            gemini_service=llm_service
        )

        # Initialize analytics service
        analytics_service = AnalyticsService(db_service=db_service)

        # Initialize voice customization service
        voice_customization_service = VoiceCustomizationService(db_service=db_service)

        # Initialize notification service
        notification_service = NotificationService(
            db_service=db_service,
            goal_progress_service=goal_progress_service
        )

        # Initialize master processor with session manager
        master_processor = MasterDirectiveProcessor(
            db_service=db_service,
            llm_service=llm_service,
            stt_service=stt_service,
            tts_service=tts_service,
            session_manager=session_manager,
            goal_progress_service=goal_progress_service
        )

        logger.info("✅ All services initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Project Eden V2 Backend...")


# Create FastAPI app
app = FastAPI(
    title="Project Eden V2 API",
    description="J.A.R.V.I.S.-like AI Partner with Master Directive System",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Global Exception Handlers ====================

@app.exception_handler(GoalNotFoundException)
async def goal_not_found_handler(request: Request, exc: GoalNotFoundException):
    """Handle goal not found errors with user-friendly messages"""
    logger.warning(f"Goal not found: {exc.message}", extra={"user_id": exc.user_id})
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message,
            "error_type": "goal_not_found",
            "user_id": exc.user_id
        }
    )


@app.exception_handler(OneThingNotSetException)
async def one_thing_not_set_handler(request: Request, exc: OneThingNotSetException):
    """Handle One Thing not set errors"""
    logger.warning(f"One Thing not set: {exc.message}", extra={"user_id": exc.user_id})
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_type": "one_thing_not_set",
            "user_id": exc.user_id,
            "action_required": "complete_onboarding"
        }
    )


@app.exception_handler(MilestoneNotFoundException)
async def milestone_not_found_handler(request: Request, exc: MilestoneNotFoundException):
    """Handle milestone not found errors"""
    logger.warning(f"Milestone not found: {exc.message}", extra={"user_id": exc.user_id})
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message,
            "error_type": "milestone_not_found",
            "user_id": exc.user_id
        }
    )


@app.exception_handler(InvalidMetricsConfigException)
async def invalid_metrics_handler(request: Request, exc: InvalidMetricsConfigException):
    """Handle invalid metrics configuration errors"""
    logger.warning(f"Invalid metrics config: {exc.message}", extra={"user_id": exc.user_id})
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_type": "invalid_metrics_config",
            "user_id": exc.user_id,
            "reason": exc.reason
        }
    )


@app.exception_handler(InvalidMoodRatingException)
async def invalid_mood_handler(request: Request, exc: InvalidMoodRatingException):
    """Handle invalid mood rating errors"""
    logger.warning(f"Invalid mood rating: {exc.message}", extra={"user_id": exc.user_id})
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_type": "invalid_mood_rating",
            "user_id": exc.user_id,
            "provided_value": exc.mood_value
        }
    )


@app.exception_handler(InvalidDateFormatException)
async def invalid_date_handler(request: Request, exc: InvalidDateFormatException):
    """Handle invalid date format errors"""
    logger.warning(f"Invalid date format: {exc.message}", extra={"user_id": exc.user_id})
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_type": "invalid_date_format",
            "user_id": exc.user_id,
            "provided_value": exc.date_value
        }
    )


@app.exception_handler(AIServiceException)
async def ai_service_handler(request: Request, exc: AIServiceException):
    """Handle AI service errors (non-critical, fallback used)"""
    logger.error(
        f"AI service error: {exc.message}",
        extra={
            "user_id": exc.user_id,
            "operation": exc.operation,
            "original_error": str(exc.original_error) if exc.original_error else None
        }
    )
    return JSONResponse(
        status_code=200,  # Return 200 since we use fallback
        content={
            "detail": exc.message,
            "error_type": "ai_service_degraded",
            "status": "success_with_fallback",
            "user_id": exc.user_id
        }
    )


@app.exception_handler(DatabaseOperationException)
async def database_operation_handler(request: Request, exc: DatabaseOperationException):
    """Handle database operation errors"""
    logger.error(
        f"Database error: {exc.message}",
        extra={
            "user_id": exc.user_id,
            "operation": exc.operation,
            "original_error": str(exc.original_error) if exc.original_error else None
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": exc.message,
            "error_type": "database_error",
            "user_id": exc.user_id,
            "operation": exc.operation
        }
    )


@app.exception_handler(InsufficientDataException)
async def insufficient_data_handler(request: Request, exc: InsufficientDataException):
    """Handle insufficient data for analysis errors"""
    logger.info(f"Insufficient data: {exc.message}", extra={"user_id": exc.user_id})
    return JSONResponse(
        status_code=200,  # Return 200 with informational message
        content={
            "detail": exc.message,
            "error_type": "insufficient_data",
            "user_id": exc.user_id,
            "required_count": exc.required_count,
            "actual_count": exc.actual_count,
            "status": "success_with_limitation"
        }
    )


# ==================== Dependencies ====================

def get_master_processor() -> MasterDirectiveProcessor:
    """Dependency to get master processor"""
    if master_processor is None:
        raise HTTPException(status_code=500, detail="Services not initialized")
    return master_processor


def get_db_service() -> DynamoDBService:
    """Dependency to get DB service"""
    if db_service is None:
        raise HTTPException(status_code=500, detail="Database service not initialized")
    return db_service


def get_onboarding_service() -> OnboardingService:
    """Dependency to get onboarding service"""
    if onboarding_service is None:
        raise HTTPException(status_code=500, detail="Onboarding service not initialized")
    return onboarding_service


def get_onboarding_v3_service() -> OnboardingV3Service:
    """Dependency to get onboarding V3 service"""
    if onboarding_v3_service is None:
        raise HTTPException(status_code=500, detail="Onboarding V3 service not initialized")
    return onboarding_v3_service


def get_session_manager() -> SessionManager:
    """Dependency to get session manager"""
    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    return session_manager


def get_goal_progress_service() -> GoalProgressService:
    """Dependency to get goal progress service"""
    if goal_progress_service is None:
        raise HTTPException(status_code=500, detail="Goal progress service not initialized")
    return goal_progress_service


def get_analytics_service() -> AnalyticsService:
    """Dependency to get analytics service"""
    if analytics_service is None:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    return analytics_service


def get_voice_customization_service() -> VoiceCustomizationService:
    """Dependency to get voice customization service"""
    if voice_customization_service is None:
        raise HTTPException(status_code=500, detail="Voice customization service not initialized")
    return voice_customization_service


def get_notification_service() -> NotificationService:
    """Dependency to get notification service"""
    if notification_service is None:
        raise HTTPException(status_code=500, detail="Notification service not initialized")
    return notification_service


# ==================== API Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Project Eden V2 API",
        "version": "2.0.0",
        "description": "J.A.R.V.I.S.-like AI Partner",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    uptime = int(time.time() - app_start_time)

    services_status = {
        "groq_stt": stt_service is not None,
        "gemini_llm": llm_service is not None,
        "edge_tts": tts_service is not None,
        "dynamodb": db_service is not None,
        "master_processor": master_processor is not None
    }

    all_healthy = all(services_status.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        version="2.0.0",
        services=services_status,
        uptime_seconds=uptime
    )


@app.post("/api/v2/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    user_id: str = Form(...),
    message: str = Form(""),
    voice_type: str = Form(...),
    session_id: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    camera_frames: List[UploadFile] = File(default=[]),
    wifi_available: bool = Form(default=False),
    processor: MasterDirectiveProcessor = Depends(get_master_processor)
):
    """
    Main chat endpoint - processes conversation through Master Directive system with RAG and WebSearch

    Args:
        user_id: User ID
        message: User's message text (from STT or typed)
        voice_type: "adam" or "eve"
        session_id: Optional session ID for multi-turn
        audio_file: Optional audio file for voice tone analysis
        camera_frames: Optional camera frames (up to 8)
        wifi_available: Whether WiFi is connected (enables WebSearch)

    Returns:
        ChatResponse with AI response, TTS audio, and metadata
    """
    try:
        logger.info(f"Chat request from user {user_id}")

        # Validate persona
        try:
            persona = PersonaType(voice_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid voice_type: {voice_type}. Must be 'adam' or 'eve'")

        # Validate message is not empty
        if not message or message.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty. Please ensure STT transcription result is passed to this endpoint."
            )

        # Process camera frames if provided
        images = []
        if camera_frames and len(camera_frames) > 0:
            for frame in camera_frames[:8]:  # Max 8 frames
                try:
                    image_bytes = await frame.read()
                    image = Image.open(io.BytesIO(image_bytes))
                    images.append(image)
                except Exception as e:
                    logger.warning(f"Failed to process camera frame: {e}")

        # Process conversation with RAG and WebSearch
        response = await processor.process_conversation(
            user_id=user_id,
            message=message,
            voice_type=persona,
            session_id=session_id,
            camera_frames=images if images else None,
            audio_file_path=None,  # TODO: Save uploaded audio file
            wifi_available=wifi_available
        )

        return response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/chat/stream", tags=["Chat"])
async def chat_stream(
    user_id: str = Form(...),
    message: str = Form(""),
    voice_type: str = Form(...),
    session_id: Optional[str] = Form(None),
    camera_frames: List[UploadFile] = File(default=[]),
    wifi_available: bool = Form(default=False),
    processor: MasterDirectiveProcessor = Depends(get_master_processor)
):
    """
    Streaming chat endpoint - returns AI response text as SSE stream for faster perceived speed
    TTS audio is generated and sent at the end of the stream

    Args:
        user_id: User ID
        message: User's message text (from STT or typed)
        voice_type: "adam" or "eve"
        session_id: Optional session ID for multi-turn
        camera_frames: Optional camera frames (up to 8)
        wifi_available: Whether WiFi is connected (enables WebSearch)

    Returns:
        Server-Sent Events stream with text chunks and final metadata
    """
    async def event_generator():
        try:
            logger.info(f"Streaming chat request from user {user_id}")

            # Validate persona
            try:
                persona = PersonaType(voice_type)
            except ValueError:
                yield f"data: {json.dumps({'error': f'Invalid voice_type: {voice_type}. Must be adam or eve'})}\n\n"
                return

            # Validate message
            if not message or message.strip() == "":
                yield f"data: {json.dumps({'error': 'Message cannot be empty'})}\n\n"
                return

            # Process camera frames
            images = []
            if camera_frames and len(camera_frames) > 0:
                for frame in camera_frames[:8]:
                    try:
                        image_bytes = await frame.read()
                        image = Image.open(io.BytesIO(image_bytes))
                        images.append(image)
                    except Exception as e:
                        logger.warning(f"Failed to process camera frame: {e}")

            # Get all context (profile, RAG, web search, pitfall check) - same as non-streaming
            import asyncio
            start_time = datetime.now()

            # Load user profile and recent conversations
            profile_task = processor.db.get_or_create_profile(user_id)

            # Handle session logic
            active_session = None
            if processor.session_manager and session_id:
                active_session = await processor.session_manager.get_session(session_id)
                if active_session and not active_session.is_expired():
                    profile = await profile_task
                    recent_conversations = processor._build_conversations_from_session(active_session)
                else:
                    recent_conversations_task = processor.db.get_recent_conversations(user_id, limit=10)
                    profile, recent_conversations = await asyncio.gather(profile_task, recent_conversations_task)
            else:
                recent_conversations_task = processor.db.get_recent_conversations(user_id, limit=10)
                profile, recent_conversations = await asyncio.gather(profile_task, recent_conversations_task)

            # RAG semantic search
            rag_context_string = "No semantic memory retrieved."
            if processor.rag_service:
                try:
                    from models.rag_models import RAGQuery
                    rag_query = RAGQuery(query_text=message, user_id=user_id, k=5, min_similarity=0.5)
                    rag_results = await processor.rag_service.search_similar_conversations(rag_query)
                    if rag_results.retrieved_conversations:
                        rag_lines = [f"Found {rag_results.total_results} semantically similar past conversations:"]
                        for i, conv in enumerate(rag_results.retrieved_conversations, 1):
                            rag_lines.append(f"\n{i}. (Similarity: {conv.similarity_score:.2f}) {conv.created_at.strftime('%Y-%m-%d')}")
                            rag_lines.append(f"   User: {conv.user_message[:100]}...")
                            rag_lines.append(f"   AI: {conv.ai_response[:100]}...")
                        rag_context_string = "\n".join(rag_lines)
                except Exception as e:
                    logger.warning(f"RAG search failed: {e}")

            # Web search
            web_context_string = "No web search performed."
            if wifi_available and processor.web_search_service:
                try:
                    search_decision = processor.web_search_service.should_trigger_search(message)
                    if search_decision.should_search:
                        from models.search_models import SearchQuery
                        search_query = SearchQuery(query_text=message, max_results=3, search_depth="basic")
                        search_results = await processor.web_search_service.search(search_query)
                        if search_results.results:
                            web_context_string = processor.web_search_service.format_search_results_for_prompt(search_results)
                except Exception as e:
                    logger.warning(f"WebSearch failed: {e}")

            # Pitfall detection
            pitfall_check = await processor.pitfall_service.check_for_pitfall(
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

            # Emotional support detection
            emotional_support_mode, emotional_details = processor._detect_emotional_need(
                message=message,
                profile=profile
            )

            # Goal progress context
            goal_context_string = "No goal tracking info available."
            goal_progress_context = await processor._check_goal_progress_context(user_id, profile)
            if goal_progress_context:
                goal_context_string = goal_progress_context

            # Log timing for each stage
            context_load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⏱️ Context loading time: {context_load_time:.2f}s")

            # Stream AI response
            llm_start_time = datetime.now()
            logger.info("🌊 Starting streaming AI response generation...")
            full_response = ""

            async for text_chunk in processor.llm.generate_response_stream(
                user_message=message,
                user_profile=profile,
                persona=persona,
                recent_conversations=recent_conversations,
                camera_frames=images if images else None,
                pitfall_warning_mode=pitfall_warning_triggered,
                pitfall_details=pitfall_details,
                emotional_support_mode=emotional_support_mode,
                emotional_details=emotional_details,
                rag_context=rag_context_string,
                web_context=web_context_string,
                goal_context=goal_context_string
            ):
                full_response += text_chunk
                # Send text chunk as SSE event
                yield f"data: {json.dumps({'type': 'text_chunk', 'content': text_chunk})}\n\n"

            # Log LLM completion time
            llm_time = (datetime.now() - llm_start_time).total_seconds()
            logger.info(f"✅ Streaming response completed: {full_response[:100]}...")
            logger.info(f"⏱️ LLM generation time: {llm_time:.2f}s")

            # Generate TTS audio after streaming text is complete
            tts_start_time = datetime.now()
            logger.info("🎙️ Generating TTS audio...")
            audio_base64 = await processor.tts.generate_speech_base64(
                text=full_response,
                persona=persona
            )
            tts_time = (datetime.now() - tts_start_time).total_seconds()
            logger.info(f"⏱️ TTS generation time: {tts_time:.2f}s")

            # Save conversation to database
            from models.conversation import Conversation, ConversationMessage
            import uuid
            conversation = Conversation(
                conversation_id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                persona=persona.value,
                messages=[
                    ConversationMessage(role="user", content=message, timestamp=datetime.now()),
                    ConversationMessage(role="assistant", content=full_response, timestamp=datetime.now())
                ],
                pitfall_warning_triggered=pitfall_warning_triggered,
                pitfall_reason=pitfall_check.reason if pitfall_warning_triggered else None,
                emotional_support_mode=emotional_support_mode,
                detected_emotional_state=emotional_details.get('state') if emotional_details else None,
                main_topic=pitfall_check.detected_topic,
                topic_alignment_score=pitfall_check.alignment_score
            )
            await processor.db.save_conversation(conversation)

            # Add turn to session if active
            if active_session:
                await processor.session_manager.add_turn(
                    session_id=active_session.session_id,
                    user_message=message,
                    ai_response=full_response,
                    processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )

            # Background tasks: RAG embedding + learning
            if processor.rag_service:
                asyncio.create_task(processor.rag_service.embed_and_store_conversation(conversation))
            asyncio.create_task(processor.learning_service.learn_from_conversation(
                user_id=user_id,
                conversation=conversation
            ))

            # Send final event with metadata and audio
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⏱️ TOTAL processing time: {total_time:.2f}s (Context: {context_load_time:.2f}s, LLM: {llm_time:.2f}s, TTS: {tts_time:.2f}s)")

            final_event = {
                'type': 'complete',
                'conversation_id': conversation.conversation_id,
                'audio_base64': audio_base64,
                'pitfall_warning_triggered': pitfall_warning_triggered,
                'emotional_support_mode': emotional_support_mode,
                'processing_time_ms': processing_time
            }
            yield f"data: {json.dumps(final_event)}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming chat endpoint: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/v2/profile/{user_id}", response_model=ProfileResponse, tags=["Profile"])
async def get_profile(
    user_id: str,
    db: DynamoDBService = Depends(get_db_service)
):
    """Get user profile"""
    try:
        profile = await db.get_user_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")

        # Format response
        summary = db.format_profile_summary(profile)

        return ProfileResponse(**summary)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v2/profile/{user_id}", response_model=ProfileResponse, tags=["Profile"])
async def update_profile(
    user_id: str,
    update: ProfileUpdateRequest,
    db: DynamoDBService = Depends(get_db_service)
):
    """Update user profile manually"""
    try:
        profile = await db.get_user_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")

        # Update fields
        if update.one_thing:
            from models.user_profile import OneThing
            profile.one_thing = OneThing(
                value=update.one_thing,
                confidence=0.9,
                sub_goals=[]
            )

        if update.core_identity:
            from models.user_profile import CoreElement
            profile.core_identity = CoreElement(
                value=update.core_identity,
                confidence=0.9,
                evidence=["Manually set by user"]
            )

        if update.core_motivation:
            from models.user_profile import CoreElement
            profile.core_motivation = CoreElement(
                value=update.core_motivation,
                confidence=0.9,
                evidence=["Manually set by user"]
            )

        # Save updated profile
        profile.profile_version += 1
        profile.last_updated = datetime.now()

        await db.save_user_profile(profile)

        # Return updated summary
        summary = db.format_profile_summary(profile)
        return ProfileResponse(**summary)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/learning/events/{user_id}", response_model=LearningEventsResponse, tags=["Learning"])
async def get_learning_events(
    user_id: str,
    limit: int = 50,
    db: DynamoDBService = Depends(get_db_service)
):
    """Get learning events for a user"""
    try:
        events = await db.get_learning_events(user_id, limit=limit)

        event_responses = [
            LearningEventResponse(
                event_id=event.event_id,
                timestamp=event.timestamp,
                event_type=event.event_type,
                description=event.description,
                profile_version=event.profile_version
            )
            for event in events
        ]

        return LearningEventsResponse(events=event_responses)

    except Exception as e:
        logger.error(f"Error getting learning events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/stt", tags=["Services"])
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("ko")
):
    """Transcribe audio file to text (STT)"""
    try:
        if not stt_service:
            raise HTTPException(status_code=500, detail="STT service not initialized")

        # Read audio bytes
        audio_bytes = await audio_file.read()

        # Transcribe
        text = await stt_service.transcribe_audio_bytes(
            audio_bytes=audio_bytes,
            filename=audio_file.filename,
            language=language
        )

        if not text:
            raise HTTPException(status_code=500, detail="Transcription failed")

        return {"text": text}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in STT endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Onboarding Endpoints ====================

class OnboardingStartRequest(BaseModel):
    user_id: str
    persona: str = "adam"


@app.post("/api/v2/onboarding/start", tags=["Onboarding"])
async def start_onboarding(
    request: OnboardingStartRequest,
    onboarding_v3: OnboardingV3Service = Depends(get_onboarding_v3_service)
):
    """
    Start a new onboarding V3 session with personality profiling

    Args:
        request: Onboarding start request with user_id and persona

    Returns:
        session_id, first question, and metadata
    """
    try:
        # Validate persona
        try:
            persona_type = PersonaType(request.persona)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid persona: {request.persona}. Must be 'adam' or 'eve'")

        # Start V3 session
        result = await onboarding_v3.start_onboarding(user_id=request.user_id, persona=persona_type)

        return result

    except Exception as e:
        logger.error(f"Error starting onboarding V3: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class OnboardingRespondRequest(BaseModel):
    session_id: str
    user_response: str
    selected_option: Optional[str] = None  # For multiple choice questions


@app.post("/api/v2/onboarding/respond", tags=["Onboarding"])
async def respond_to_onboarding(
    request: OnboardingRespondRequest,
    onboarding_v3: OnboardingV3Service = Depends(get_onboarding_v3_service)
):
    """
    Process user response to onboarding V3 question

    Args:
        request: Onboarding response request with session_id, user_response, and optional selected_option

    Returns:
        Next question or completion result
    """
    try:
        # Process V3 response
        result = await onboarding_v3.process_response(
            session_id=request.session_id,
            user_response=request.user_response,
            selected_option=request.selected_option
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing onboarding V3 response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/onboarding/status/{session_id}", tags=["Onboarding"])
async def get_onboarding_status(
    session_id: str,
    onboarding_v3: OnboardingV3Service = Depends(get_onboarding_v3_service)
):
    """Get onboarding V3 session status"""
    try:
        session = await onboarding_v3.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return {
            "session_id": session.get("session_id"),
            "user_id": session.get("user_id"),
            "persona": session.get("persona", "adam"),
            "current_step": session.get("current_step", 1),
            "total_steps": session.get("total_steps", 6),
            "completed": session.get("completed", False)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding V3 status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class OnboardingBackRequest(BaseModel):
    session_id: str


@app.post("/api/v2/onboarding/back", tags=["Onboarding"])
async def go_back_onboarding(
    request: OnboardingBackRequest,
    onboarding_v3: OnboardingV3Service = Depends(get_onboarding_v3_service)
):
    """
    Go back one step in onboarding

    Args:
        request: OnboardingBackRequest with session_id

    Returns:
        Previous question data

    Raises:
        404: Session not found
        400: Already at first question
    """
    try:
        result = await onboarding_v3.go_back_one_step(request.session_id)
        return result

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "first question" in error_msg or "cannot go back" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error going back in onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Session Management Endpoints ====================

@app.post("/api/v2/session/create", tags=["Session"])
async def create_session(
    user_id: str = Form(...),
    persona: str = Form("adam"),
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Create a new conversation session

    Args:
        user_id: User ID
        persona: Persona type (adam or eve)

    Returns:
        Session information
    """
    try:
        # Validate persona
        try:
            persona_type = PersonaType(persona)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid persona: {persona}. Must be 'adam' or 'eve'")

        # Create session
        session = await session_mgr.create_session(user_id=user_id, persona=persona_type)

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "persona": session.persona.value,
            "created_at": session.created_at.isoformat(),
            "is_active": session.is_active
        }

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/session/{session_id}", tags=["Session"])
async def get_session_info(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Get session information"""
    try:
        session_info = await session_mgr.get_session_info(session_id)

        if not session_info:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return {
            "session_id": session_info.session_id,
            "user_id": session_info.user_id,
            "persona": session_info.persona.value,
            "turn_count": session_info.turn_count,
            "created_at": session_info.created_at.isoformat(),
            "last_activity": session_info.last_activity.isoformat(),
            "is_active": session_info.is_active,
            "is_expired": session_info.is_expired
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/session/{session_id}/close", tags=["Session"])
async def close_session(
    session_id: str,
    reason: str = Form(default="user_request"),
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Close a conversation session"""
    try:
        await session_mgr.close_session(session_id, reason=reason)

        return {
            "session_id": session_id,
            "status": "closed",
            "reason": reason
        }

    except Exception as e:
        logger.error(f"Error closing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/session/user/{user_id}", tags=["Session"])
async def get_user_active_session(
    user_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Get user's active session if exists"""
    try:
        session = await session_mgr.get_user_active_session(user_id)

        if not session:
            return {"active_session": None}

        return {
            "active_session": {
                "session_id": session.session_id,
                "persona": session.persona.value,
                "turn_count": len(session.turns),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting user active session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/session/stats", tags=["Session"])
async def get_session_stats(
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Get session statistics"""
    try:
        stats = session_mgr.get_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Goal Progress Endpoints ====================

@app.post("/api/v2/goals/create", tags=["Goals"])
async def create_goal(
    user_id: str = Form(...),
    target_date: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: DynamoDBService = Depends(get_db_service),
    goal_service: GoalProgressService = Depends(get_goal_progress_service)
):
    """
    Create a goal tracker from user's One Thing

    Args:
        user_id: User ID
        target_date: Optional target completion date (ISO format: YYYY-MM-DD)
        description: Optional detailed description

    Returns:
        Goal tracker information
    """
    # Get user profile
    profile = await db.get_user_profile(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail=f"프로필을 찾을 수 없습니다 (User: {user_id})")

    # Parse target date if provided
    target = None
    if target_date:
        try:
            from datetime import date as date_cls
            target = date_cls.fromisoformat(target_date)
        except ValueError:
            raise InvalidDateFormatException(user_id, target_date)

    # Create goal tracker (this will raise custom exceptions if errors occur)
    tracker = await goal_service.create_goal_from_one_thing(
        user_profile=profile,
        target_date=target,
        description=description
    )

    return {
        "goal_id": tracker.goal_id,
        "one_thing": tracker.one_thing,
        "description": tracker.description,
        "start_date": tracker.start_date.isoformat(),
        "target_date": tracker.target_date.isoformat() if tracker.target_date else None,
        "milestones_count": len(tracker.milestones),
        "created": True
    }


@app.get("/api/v2/goals/{user_id}", tags=["Goals"])
async def get_goal_summary(
    user_id: str,
    goal_service: GoalProgressService = Depends(get_goal_progress_service)
):
    """Get comprehensive goal summary with insights"""
    try:
        summary = await goal_service.get_goal_summary(user_id)

        if not summary:
            raise HTTPException(status_code=404, detail=f"No goal found for user {user_id}")

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting goal summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/goals/{user_id}/progress", tags=["Goals"])
async def record_progress(
    user_id: str,
    reflection: Optional[str] = Form(None),
    mood_rating: Optional[int] = Form(None),
    metrics: Optional[str] = Form(None),  # JSON string of metrics
    photo_url: Optional[str] = Form(None),
    goal_service: GoalProgressService = Depends(get_goal_progress_service)
):
    """
    Record daily/weekly progress snapshot

    Args:
        user_id: User ID
        reflection: User's reflection on progress
        mood_rating: Mood rating 1-5
        metrics: JSON array of metrics [{"name": "Study Hours", "value": 2.5, "unit": "hours"}]
        photo_url: Optional URL to progress photo

    Returns:
        Success status
    """
    try:
        # Parse metrics if provided
        from models.goal_progress import GoalMetric, MoodRating
        import json

        metric_objects = []
        if metrics:
            try:
                metrics_data = json.loads(metrics)
                for m in metrics_data:
                    metric_objects.append(GoalMetric(
                        name=m["name"],
                        value=float(m["value"]),
                        unit=m["unit"],
                        metric_type=m.get("metric_type", "count")
                    ))
            except (json.JSONDecodeError, KeyError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid metrics format: {e}")

        # Validate mood rating
        mood = None
        if mood_rating is not None:
            if mood_rating not in [1, 2, 3, 4, 5]:
                raise HTTPException(status_code=400, detail="Mood rating must be 1-5")
            mood = MoodRating(mood_rating)

        # Record progress
        success = await goal_service.record_progress(
            user_id=user_id,
            metrics=metric_objects if metric_objects else None,
            reflection=reflection,
            mood_rating=mood,
            photo_url=photo_url
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to record progress")

        return {
            "success": True,
            "message": "Progress recorded successfully",
            "recorded_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/goals/{user_id}/milestones", tags=["Goals"])
async def add_milestone(
    user_id: str,
    description: str = Form(...),
    target_date: Optional[str] = Form(None),
    reward: Optional[str] = Form(None),
    goal_service: GoalProgressService = Depends(get_goal_progress_service)
):
    """Add a custom milestone to the goal"""
    try:
        # Parse target date if provided
        target = None
        if target_date:
            try:
                from datetime import date as date_cls
                target = date_cls.fromisoformat(target_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        success = await goal_service.add_custom_milestone(
            user_id=user_id,
            description=description,
            target_date=target,
            reward=reward
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to add milestone")

        return {
            "success": True,
            "message": "Milestone added successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding milestone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v2/goals/{user_id}/milestones/{milestone_id}", tags=["Goals"])
async def update_milestone_status(
    user_id: str,
    milestone_id: str,
    is_completed: bool = Form(...),
    goal_service: GoalProgressService = Depends(get_goal_progress_service)
):
    """Mark milestone as completed or uncompleted"""
    try:
        success = await goal_service.db.update_milestone(
            user_id=user_id,
            milestone_id=milestone_id,
            is_completed=is_completed
        )

        if not success:
            raise HTTPException(status_code=404, detail="Milestone not found or update failed")

        return {
            "success": True,
            "milestone_id": milestone_id,
            "is_completed": is_completed
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating milestone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/goals/{user_id}/setup-metrics", tags=["Goals"])
async def setup_tracked_metrics(
    user_id: str,
    metrics_config: str = Form(...),  # JSON: {"metrics": ["Study Hours", "Pages Read"], "units": {"Study Hours": "hours", "Pages Read": "pages"}}
    goal_service: GoalProgressService = Depends(get_goal_progress_service)
):
    """Configure which metrics to track for the goal"""
    try:
        import json

        try:
            config = json.loads(metrics_config)
            metric_names = config["metrics"]
            metric_units = config["units"]
        except (json.JSONDecodeError, KeyError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid metrics config format: {e}")

        success = await goal_service.setup_tracked_metrics(
            user_id=user_id,
            metric_names=metric_names,
            metric_units=metric_units
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to setup metrics")

        return {
            "success": True,
            "tracked_metrics": metric_names,
            "message": "Metrics configured successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/goals/{user_id}/history", tags=["Goals"])
async def get_progress_history(
    user_id: str,
    days: int = 30,
    db: DynamoDBService = Depends(get_db_service)
):
    """Get progress history for last N days"""
    try:
        snapshots = await db.get_progress_history(user_id=user_id, days=days)

        return {
            "user_id": user_id,
            "days": days,
            "total_snapshots": len(snapshots),
            "snapshots": [
                {
                    "snapshot_id": s.snapshot_id,
                    "date": s.date.isoformat(),
                    "reflection": s.reflection,
                    "mood_rating": s.mood_rating,
                    "metrics": [
                        {
                            "name": m.name,
                            "value": m.value,
                            "unit": m.unit,
                            "metric_type": m.metric_type
                        }
                        for m in s.metrics
                    ],
                    "photo_url": s.photo_url,
                    "created_at": s.created_at.isoformat()
                }
                for s in sorted(snapshots, key=lambda x: x.date, reverse=True)
            ]
        }

    except Exception as e:
        logger.error(f"Error getting progress history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/goals/{user_id}/insights", tags=["Goals"])
async def generate_insights(
    user_id: str,
    db: DynamoDBService = Depends(get_db_service),
    goal_service: GoalProgressService = Depends(get_goal_progress_service)
):
    """Generate AI-powered insights about user's progress"""
    try:
        tracker = await db.get_goal_progress(user_id)

        if not tracker:
            raise HTTPException(status_code=404, detail=f"No goal found for user {user_id}")

        # Get user profile for context
        profile = await db.get_user_profile(user_id)

        # Generate insights
        insights = await goal_service.generate_progress_insights(tracker, profile)

        return {
            "user_id": user_id,
            "total_insights": len(insights),
            "insights": [
                {
                    "type": i.insight_type,
                    "title": i.title,
                    "description": i.description,
                    "actionable": i.actionable,
                    "priority": i.priority,
                    "generated_at": i.generated_at.isoformat()
                }
                for i in sorted(insights, key=lambda x: x.priority, reverse=True)
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Analytics Endpoints ====================

@app.get("/api/v2/analytics/{user_id}/timeline", tags=["Analytics"])
async def get_progress_timeline(
    user_id: str,
    days: int = 30,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get time series data for progress visualization

    Returns dates, completion trend, mood trend, metrics over time, and daily streaks
    """
    timeline = await analytics_service.get_progress_timeline(user_id, days)
    return timeline


@app.get("/api/v2/analytics/{user_id}/statistics", tags=["Analytics"])
async def get_progress_statistics(
    user_id: str,
    days: int = 30,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get statistical analysis of progress data

    Returns mood stats, consistency score, velocity, productivity patterns, and metric stats
    """
    statistics_data = await analytics_service.get_progress_statistics(user_id, days)
    return statistics_data


@app.get("/api/v2/analytics/{user_id}/patterns", tags=["Analytics"])
async def detect_patterns(
    user_id: str,
    days: int = 30,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Detect behavioral patterns in progress data

    Returns streak patterns, mood patterns, productivity by weekday, and insights
    """
    patterns = await analytics_service.detect_patterns(user_id, days)
    return patterns


@app.get("/api/v2/analytics/{user_id}/comparison", tags=["Analytics"])
async def get_period_comparison(
    user_id: str,
    period1_days: int = 7,
    period2_days: int = 14,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Compare two time periods (e.g., this week vs last two weeks)

    Returns comparison of mood, entries, and overall trend between periods
    """
    comparison = await analytics_service.get_period_comparison(
        user_id,
        period1_days,
        period2_days
    )
    return comparison


# ==================== Voice Customization Endpoints ====================

@app.get("/api/v2/voice/{user_id}/settings", tags=["Voice"])
async def get_voice_settings(
    user_id: str,
    voice_service: VoiceCustomizationService = Depends(get_voice_customization_service)
):
    """Get user's voice customization settings"""
    settings = await voice_service.get_voice_settings(user_id)
    return settings


@app.put("/api/v2/voice/{user_id}/settings", tags=["Voice"])
async def update_voice_settings(
    user_id: str,
    voice_id: Optional[str] = Form(None),
    speed: Optional[float] = Form(None),
    pitch: Optional[float] = Form(None),
    volume: Optional[float] = Form(None),
    persona_empathy: Optional[int] = Form(None),
    persona_directness: Optional[int] = Form(None),
    persona_formality: Optional[int] = Form(None),
    persona_encouragement: Optional[int] = Form(None),
    voice_service: VoiceCustomizationService = Depends(get_voice_customization_service)
):
    """
    Update user's voice customization settings

    Args:
        voice_id: Voice identifier (default, female_gentle, male_confident, neutral_calm)
        speed: Speech speed (0.5 - 2.0)
        pitch: Voice pitch (0.5 - 2.0)
        volume: Volume level (0.5 - 2.0)
        persona_empathy: Empathy level (1-5)
        persona_directness: Directness level (1-5)
        persona_formality: Formality level (1-5)
        persona_encouragement: Encouragement level (1-5)
    """
    # Build persona_traits dict
    persona_traits = {}
    if persona_empathy is not None:
        persona_traits["empathy_level"] = persona_empathy
    if persona_directness is not None:
        persona_traits["directness"] = persona_directness
    if persona_formality is not None:
        persona_traits["formality"] = persona_formality
    if persona_encouragement is not None:
        persona_traits["encouragement"] = persona_encouragement

    settings = await voice_service.update_voice_settings(
        user_id=user_id,
        voice_id=voice_id,
        speed=speed,
        pitch=pitch,
        volume=volume,
        persona_traits=persona_traits if persona_traits else None
    )

    return {
        "success": True,
        "settings": settings
    }


@app.get("/api/v2/voice/available-voices", tags=["Voice"])
async def get_available_voices(
    voice_service: VoiceCustomizationService = Depends(get_voice_customization_service)
):
    """Get list of available voice options"""
    return voice_service.get_available_voices()


@app.get("/api/v2/voice/persona-traits", tags=["Voice"])
async def get_persona_traits(
    voice_service: VoiceCustomizationService = Depends(get_voice_customization_service)
):
    """Get persona trait configuration"""
    return voice_service.get_persona_trait_configs()


# ==================== Interaction Mode Endpoints ====================

@app.get("/api/v2/settings/{user_id}/interaction-mode", tags=["Settings"])
async def get_interaction_mode(
    user_id: str,
    db: MemoryDBService = Depends(get_db_service)
):
    """
    Get user's interaction mode

    Returns:
        mode: "ai_led" or "user_led"
    """
    try:
        profile = await db.get_user_profile(user_id)
        return {
            "mode": profile.interaction_mode,
            "description": "AI asks questions" if profile.interaction_mode == "ai_led" else "User asks questions"
        }
    except Exception as e:
        logger.error(f"Error getting interaction mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class InteractionModeRequest(BaseModel):
    mode: str  # "ai_led" or "user_led"


@app.put("/api/v2/settings/{user_id}/interaction-mode", tags=["Settings"])
async def update_interaction_mode(
    user_id: str,
    request: InteractionModeRequest,
    db: MemoryDBService = Depends(get_db_service)
):
    """
    Update user's interaction mode

    Args:
        mode: "ai_led" (AI asks questions, user answers) or "user_led" (User asks questions, AI answers)
    """
    try:
        # Validate mode
        if request.mode not in ["ai_led", "user_led"]:
            raise HTTPException(status_code=400, detail="Mode must be 'ai_led' or 'user_led'")

        # Get profile
        profile = await db.get_user_profile(user_id)

        # Update interaction mode
        profile.interaction_mode = request.mode

        # Save profile
        await db.update_user_profile(user_id, profile)

        logger.info(f"Updated interaction mode for user {user_id} to {request.mode}")

        return {
            "success": True,
            "mode": request.mode,
            "message": f"Interaction mode updated to {request.mode}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interaction mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Notification Endpoints ====================

class FCMTokenRequest(BaseModel):
    """Request model for FCM token registration"""
    fcm_token: str
    device_info: Optional[dict] = None


class NotificationPreferencesUpdate(BaseModel):
    """Request model for notification preferences update"""
    enabled: Optional[bool] = None
    goal_reminders: Optional[bool] = None
    stagnation_alerts: Optional[bool] = None
    milestone_notifications: Optional[bool] = None
    encouragement_messages: Optional[bool] = None
    weekly_summaries: Optional[bool] = None
    reminder_time: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None


@app.post("/api/v2/notifications/{user_id}/subscribe", tags=["Notifications"])
async def subscribe_to_notifications(
    user_id: str,
    request: FCMTokenRequest,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Register FCM token for push notifications

    Args:
        user_id: User ID
        request: FCM token and optional device info

    Returns:
        Registration status
    """
    try:
        result = await notification_service.register_fcm_token(
            user_id=user_id,
            fcm_token=request.fcm_token,
            device_info=request.device_info
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error subscribing to notifications for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to register FCM token")


@app.delete("/api/v2/notifications/{user_id}/unsubscribe", tags=["Notifications"])
async def unsubscribe_from_notifications(
    user_id: str,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Remove FCM token (e.g., on logout)

    Args:
        user_id: User ID

    Returns:
        Unregistration status
    """
    try:
        result = await notification_service.unregister_fcm_token(user_id)
        return result
    except Exception as e:
        logger.error(f"Error unsubscribing from notifications for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to unregister FCM token")


@app.get("/api/v2/notifications/{user_id}/preferences", tags=["Notifications"])
async def get_notification_preferences(
    user_id: str,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get user's notification preferences

    Args:
        user_id: User ID

    Returns:
        Notification preferences including reminder times and quiet hours
    """
    try:
        preferences = await notification_service.get_notification_preferences(user_id)
        return preferences
    except Exception as e:
        logger.error(f"Error getting notification preferences for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification preferences")


@app.put("/api/v2/notifications/{user_id}/preferences", tags=["Notifications"])
async def update_notification_preferences(
    user_id: str,
    preferences: NotificationPreferencesUpdate,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Update user's notification preferences

    Args:
        user_id: User ID
        preferences: Preferences to update

    Returns:
        Updated preferences
    """
    try:
        # Convert to dict, excluding None values
        prefs_dict = {k: v for k, v in preferences.dict().items() if v is not None}

        updated = await notification_service.update_notification_preferences(
            user_id=user_id,
            preferences=prefs_dict
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating notification preferences for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@app.post("/api/v2/notifications/{user_id}/test", tags=["Notifications"])
async def send_test_notification(
    user_id: str,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Send a test notification to verify FCM setup

    Args:
        user_id: User ID

    Returns:
        Test notification payload (in production, this would trigger actual push)
    """
    try:
        notification_payload = await notification_service.send_test_notification(user_id)
        return {
            "message": "Test notification generated (FCM integration pending)",
            "payload": notification_payload
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending test notification for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test notification")


@app.get("/api/v2/notifications/{user_id}/pending", tags=["Notifications"])
async def get_pending_notifications(
    user_id: str,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get pending notifications for user (reminders, alerts, encouragement)

    Args:
        user_id: User ID

    Returns:
        List of pending notifications
    """
    try:
        notifications = []

        # Generate goal reminder if applicable
        goal_reminder = await notification_service.generate_goal_reminder(user_id)
        if goal_reminder:
            notifications.append(goal_reminder)

        # Check for stagnation alert
        stagnation_alert = await notification_service.generate_stagnation_alert(user_id)
        if stagnation_alert:
            notifications.append(stagnation_alert)

        # Generate encouragement message
        encouragement = await notification_service.generate_encouragement_message(user_id)
        if encouragement:
            notifications.append(encouragement)

        return {
            "user_id": user_id,
            "count": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        logger.error(f"Error getting pending notifications for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pending notifications")


# ==================== Error Handlers ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    logger.error(f"Validation error on {request.method} {request.url}")
    logger.error(f"Errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        loop="asyncio"  # Use asyncio instead of uvloop to avoid nest_asyncio conflict
    )
