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
from models.api_schemas import (
    ChatResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    LearningEventsResponse,
    LearningEventResponse,
    HealthResponse
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    global db_service, llm_service, stt_service, tts_service, master_processor

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

        master_processor = MasterDirectiveProcessor(
            db_service=db_service,
            llm_service=llm_service,
            stt_service=stt_service,
            tts_service=tts_service
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
