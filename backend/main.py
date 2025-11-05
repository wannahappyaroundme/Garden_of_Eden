"""
Project Eden V2 - Backend API
FastAPI application with Master Directive system
"""
import os
import time
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from services.session_manager import SessionManager
from services.goal_progress_service import GoalProgressService
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
stt_service: Optional[STTService] = None
tts_service: Optional[TTSService] = None
master_processor: Optional[MasterDirectiveProcessor] = None
onboarding_service: Optional[OnboardingService] = None
session_manager: Optional[SessionManager] = None
goal_progress_service: Optional[GoalProgressService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    global db_service, llm_service, stt_service, tts_service, master_processor, onboarding_service, session_manager, goal_progress_service

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
        session_manager = SessionManager()

        # Initialize goal progress service
        goal_progress_service = GoalProgressService(
            db_service=db_service,
            gemini_service=llm_service
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

@app.post("/api/v2/onboarding/start", tags=["Onboarding"])
async def start_onboarding(
    user_id: str = Form(...),
    persona: str = Form("adam"),
    onboarding: OnboardingService = Depends(get_onboarding_service)
):
    """
    Start a new onboarding session

    Args:
        user_id: User ID
        persona: Persona type (adam or eve)

    Returns:
        session_id and first question
    """
    try:
        # Validate persona
        try:
            persona_type = PersonaType(persona)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid persona: {persona}. Must be 'adam' or 'eve'")

        # Start session
        session = await onboarding.start_onboarding(user_id=user_id, persona=persona_type)

        # Get first question
        first_question = await onboarding.get_first_question(session.session_id)

        return {
            "session_id": session.session_id,
            "question": first_question,
            "step": 1,
            "total_steps": 6
        }

    except Exception as e:
        logger.error(f"Error starting onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/onboarding/respond", tags=["Onboarding"])
async def respond_to_onboarding(
    session_id: str = Form(...),
    user_response: str = Form(...),
    onboarding: OnboardingService = Depends(get_onboarding_service)
):
    """
    Process user response to onboarding question

    Args:
        session_id: Onboarding session ID
        user_response: User's response text

    Returns:
        Next question or completion result
    """
    try:
        # Process response
        result = await onboarding.process_response(
            session_id=session_id,
            user_response=user_response
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing onboarding response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/onboarding/status/{session_id}", tags=["Onboarding"])
async def get_onboarding_status(
    session_id: str,
    onboarding: OnboardingService = Depends(get_onboarding_service)
):
    """Get onboarding session status"""
    try:
        session = await onboarding.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "persona": session.persona.value,
            "current_step": session.current_step,
            "completed": session.completed,
            "one_thing_identified": session.one_thing_identified,
            "turn_count": len(session.turns)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding status: {e}")
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
        log_level="info"
    )
