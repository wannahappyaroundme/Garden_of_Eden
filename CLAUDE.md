# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project Eden V2** is a J.A.R.V.I.S.-like AI companion that learns deeply about users through an "Am-muk-ji" (implicit knowledge) learning system. It's a voice-first mobile app with camera integration that helps users stay focused on their "One Thing" goal while providing emotional support and benevolent dissent when they stray.

**Technology Stack:**
- **Backend:** FastAPI (Python 3.12), DynamoDB/In-memory DB, ChromaDB (RAG)
- **Frontend:** Flutter 3.35.7+, Riverpod 3.0
- **AI Services:** Google Gemini 2.5 Flash (LLM), Groq Whisper v3 (STT), Google TTS
- **Key Features:** RAG semantic search, WebSearch integration, dual personas (Adam/Eve)
- **Deployment:** AWS EC2 (Seoul ap-northeast-2) - **http://3.39.177.218:8000**

## Common Development Commands

### Backend

**Initial Setup (First Time Only):**
```bash
cd backend
./setup_local.sh    # Creates venv, installs dependencies, generates .env
```

**Start Backend Server:**
```bash
cd backend
./start_local.sh    # Activates venv and starts server on http://localhost:8000
```

**Alternative: Direct Python Run:**
```bash
cd backend
source venv/bin/activate  # Activate venv first
python main.py            # Or: uvicorn main:app --reload
```

**Run Tests:**
```bash
cd backend
source venv/bin/activate
pytest tests/
```

**Access API Docs:**
- Interactive docs (Local): http://localhost:8000/docs
- Interactive docs (AWS EC2): http://3.39.177.218:8000/docs
- Health check (Local): http://localhost:8000/health
- Health check (AWS EC2): http://3.39.177.218:8000/health

### Frontend

**IMPORTANT: Backend is deployed on AWS EC2**
The frontend is configured to connect to AWS EC2 backend at `http://3.39.177.218:8000`
- No need to run local backend for testing on real devices
- See `frontend/lib/utils/constants.dart` for API configuration

**Install Dependencies:**
```bash
cd frontend
flutter pub get
```

**Run on Device:**
```bash
cd frontend
flutter run  # Ensure phone connected via USB
```

**Run Specific Device:**
```bash
flutter devices          # List available devices
flutter run -d <device-id>
```

**Build Release:**
```bash
cd frontend
./build_release.sh  # Runs analyze, test, and builds APK/iOS
```

**Run Tests:**
```bash
cd frontend
flutter test                              # Unit tests
flutter test integration_test/app_test.dart  # Integration tests
```

**Code Analysis:**
```bash
cd frontend
flutter analyze  # Must return 0 errors, 0 warnings
```

**Clean Build:**
```bash
cd frontend
flutter clean
flutter pub get
flutter run
```

## Architecture Overview

### Master Directive System (Backend Core)

The backend orchestrates all AI interactions through `MasterDirectiveProcessor` ([backend/services/master_directive_processor.py](backend/services/master_directive_processor.py)), which coordinates a pipeline of services:

**Conversation Processing Flow:**
1. **Load User Profile** - Retrieve One Thing, Core Pitfall, personality traits
2. **Recent Memory** - Last 10 conversations for context
3. **RAG Semantic Search** - Top 5 similar past conversations from ChromaDB
4. **WebSearch** (if WiFi available) - Current information via Tavily/DuckDuckGo
5. **Pitfall Detection** - Check if user is straying from goals
6. **Emotional State Detection** - Detect if user needs support
7. **Persona-Aware Response** - Generate Adam (logical) or Eve (energetic) response
8. **TTS Generation** - Convert response to speech
9. **Profile Learning** - Update user traits based on conversation
10. **RAG Embedding** - Store conversation in vector DB for future retrieval

**Key Services:**
- `master_directive_processor.py` - Main orchestrator
- `profile_learning_service.py` - Am-muk-ji learning algorithm (trait weights)
- `pitfall_detection_service.py` - Benevolent dissent when user strays
- `retrieval_augmented_generation_service.py` - ChromaDB RAG system
- `web_search_service.py` - Tavily API + DuckDuckGo fallback
- `llm_gemini_v2.py` - Gemini 2.5 Flash with vision support
- `stt_service.py` - Groq Whisper Large v3
- `tts_service.py` - Google TTS (gTTS)
- `dynamodb_service_v2.py` - DynamoDB operations
- `memory_db_service.py` - In-memory DB for local testing

### Frontend Architecture (Flutter + Riverpod)

**State Management Pattern:**
- **Riverpod providers** in [frontend/lib/providers/](frontend/lib/providers/) manage global state
- **Service layer** in [frontend/lib/services/](frontend/lib/services/) handles API, audio, camera, caching
- **Widget layer** in [frontend/lib/widgets/](frontend/lib/widgets/) are reusable UI components
- **Screens** in [frontend/lib/screens/](frontend/lib/screens/) are top-level pages

**Key Services:**
- `api_service.dart` - HTTP client with retry logic, exponential backoff
- `audio_service.dart` - Recording (record package) + playback (just_audio)
- `camera_service.dart` - 1 FPS capture with keyframe selection
- `cache_service.dart` - SharedPreferences for offline support

**Main Screen Flow** ([voice_first_screen.dart](frontend/lib/screens/voice_first_screen.dart)):
1. User presses push-to-talk button → Start recording + camera capture
2. User releases → Stop recording, send audio + frames to backend `/api/v2/stt`
3. Get transcription → Send to `/api/v2/chat` with message, persona, camera frames
4. Receive response → Display text overlay, play TTS audio
5. Show pitfall warning banner if triggered

### Data Models

**Backend Models** ([backend/models/](backend/models/)):
- `user_profile.py` - UserProfile, OneThing, CorePitfall, Trait (with weights)
- `conversation.py` - Conversation, ConversationMessage
- `api_schemas.py` - ChatResponse, ProfileResponse, etc.
- `rag_models.py` - RAGQuery, RAGResult for semantic search
- `search_models.py` - SearchQuery, SearchResult for web search

**Frontend Models** ([frontend/lib/models/](frontend/lib/models/)):
- Mirror backend schemas for API compatibility
- Additional UI-specific models (loading states, error types)

### Master Directive Prompts

Located in [backend/prompts/](backend/prompts/):
- `master_directive.py` - Main system prompt template
- `learning_analysis.py` - Trait extraction and learning prompts

These prompts are critical to the AI's personality and behavior. They define:
- How Adam (logical, father-like) vs Eve (energetic, uplifting) respond
- When to trigger benevolent dissent
- How to detect emotional states
- Trait extraction from conversations

## Environment Configuration

### Backend Environment Variables (AWS EC2)

**PRODUCTION BACKEND IS DEPLOYED ON AWS EC2**
- Server IP: **3.39.177.218:8000**
- Region: Seoul (ap-northeast-2)
- No local backend setup required for mobile app testing

EC2 backend already has `.env` configured with:
```bash
GEMINI_API_KEY=configured          # Google Gemini 2.5 Flash
GROQ_API_KEY=configured            # Groq Whisper v3
TAVILY_API_KEY=not_set            # Optional - DuckDuckGo used as fallback
USE_LOCAL_DYNAMODB=true            # Using in-memory DB
HOST=0.0.0.0
PORT=8000
```

### Frontend Configuration

**ALREADY CONFIGURED FOR AWS EC2:**
[frontend/lib/utils/constants.dart](frontend/lib/utils/constants.dart) is set to:
```dart
static const String baseUrl = 'http://3.39.177.218:8000';  // AWS EC2 Seoul
```

**No changes needed** - App will connect to AWS EC2 backend automatically.

### Local Development (Optional)

If you want to run backend locally for development:

Create `backend/.env`:
```bash
GEMINI_API_KEY=your_key_here          # Get from https://ai.google.dev/
GROQ_API_KEY=your_key_here            # Get from https://console.groq.com/
TAVILY_API_KEY=your_key_here          # Optional (1000 free/month)
USE_LOCAL_DYNAMODB=true               # true=in-memory
```

Update `frontend/lib/utils/constants.dart` to local IP:
```dart
static const String baseUrl = 'http://YOUR_LOCAL_IP:8000';
```
Get local IP: `ipconfig getifaddr en0` (macOS)

## Critical Development Guidelines

### Backend Development

**When modifying the Master Directive flow:**
1. Always test the full conversation pipeline end-to-end
2. Check that profile learning updates traits correctly (weights 0.0-1.0)
3. Verify pitfall detection triggers appropriately (alignment_score < 0.3)
4. Test RAG retrieval returns relevant past conversations
5. Ensure WebSearch only triggers when WiFi available and query needs current info

**Adding new services:**
1. Create service in `backend/services/`
2. Initialize in `MasterDirectiveProcessor.__init__()`
3. Call in `process_conversation()` pipeline
4. Add corresponding API endpoint in `main.py` if needed

**Database switching:**
- Local development: `USE_LOCAL_DYNAMODB=true` (default) → uses `MemoryDBService`
- Production: `USE_LOCAL_DYNAMODB=false` → uses `DynamoDBService` with AWS

**Testing changes:**
```bash
# Test health (AWS EC2)
curl http://3.39.177.218:8000/health

# Test STT (AWS EC2)
curl -X POST http://3.39.177.218:8000/api/v2/stt \
  -F "audio_file=@test.wav" \
  -F "language=ko"

# Test chat (AWS EC2)
curl -X POST http://3.39.177.218:8000/api/v2/chat \
  -F "user_id=test_user" \
  -F "message=안녕하세요" \
  -F "voice_type=adam" \
  -F "wifi_available=true"

# If testing locally:
# cd backend && ./start_local.sh
# curl http://localhost:8000/health
```

### Frontend Development

**When modifying UI:**
1. Maintain glassmorphism design aesthetic (see [theme/app_theme.dart](frontend/lib/theme/app_theme.dart))
2. Ensure all widgets handle loading and error states
3. Test on both iOS and Android if possible
4. Run `flutter analyze` - must have 0 errors, 0 warnings

**State management pattern:**
1. Define provider in `frontend/lib/providers/`
2. Use `ref.watch()` for reactive UI updates
3. Use `ref.read()` for one-time actions
4. Keep business logic in services, not widgets

**Adding new features:**
1. Create widget in `frontend/lib/widgets/` if reusable
2. Add to appropriate screen in `frontend/lib/screens/`
3. Update providers if state management needed
4. Test error handling (network failures, timeouts)

**Error handling pattern:**
```dart
try {
  final result = await apiService.sendMessage(...);
  // Handle success
} catch (e) {
  // Show user-friendly error
  _showError('Failed to send message');
  logger.error('API error: $e');
}
```

### Persona Behavior

**Adam (아담):**
- Male voice, logical, father-like mentor
- Uses Socratic questioning to guide thinking
- Direct but caring tone
- Example: "잠깐만요. [Goal]이 목표 아닌가요? 이게 당신의 '[Pitfall]' 패턴으로 보여요."

**Eve (이브):**
- Female voice, energetic, uplifting coach
- Celebrates progress warmly
- Validates emotions naturally
- Example: "와! 정말 잘하고 계세요! 계속 이렇게 가면 [Goal] 꼭 이룰 수 있어요!"

Both personas use the same Master Directive system, but tone differs based on `voice_type` parameter.

## RAG and WebSearch Implementation

### RAG (Retrieval-Augmented Generation)

**How it works:**
1. Every conversation is embedded using `sentence-transformers/all-MiniLM-L6-v2` (384-dim vectors)
2. Stored in ChromaDB with user_id, conversation_id, timestamp metadata
3. On new query, retrieve top 5 similar conversations via cosine similarity
4. Provide as context to LLM in Master Directive prompt

**Files:**
- `backend/services/retrieval_augmented_generation_service.py`
- `backend/models/rag_models.py`
- ChromaDB persisted in `backend/chroma_db/` (gitignored)

**Usage:**
```python
rag_result = await self.rag_service.query_similar_conversations(
    user_id=user_id,
    query_text=message,
    top_k=5
)
```

### WebSearch Integration

**How it works:**
1. Check if WiFi available (from mobile app)
2. Detect if query needs current info (keywords: "최신", "2024", "현재", "뉴스", etc.)
3. Primary: Tavily API (high-quality, 1000 free/month)
4. Fallback: DuckDuckGo (always free, lower quality)
5. Return top 3 results with title, snippet, URL
6. Provide as context to LLM

**Files:**
- `backend/services/web_search_service.py`
- `backend/models/search_models.py`

**Usage:**
```python
search_result = await self.web_search_service.search(
    query=message,
    max_results=3
)
```

## Testing and Quality Assurance

### Backend Testing
```bash
cd backend
source venv/bin/activate
pytest tests/ -v                    # All tests
pytest tests/test_profile.py -v    # Specific test
```

### Frontend Testing
```bash
cd frontend
flutter test                       # Unit tests
flutter analyze                    # Static analysis (must be clean)
flutter test integration_test/     # Integration tests
```

### Manual Testing Checklist
- [ ] Voice recording and transcription (Korean)
- [ ] Persona switching (Adam ↔ Eve)
- [ ] Profile viewing with traits
- [ ] Pitfall warning triggers
- [ ] Offline mode (cached profile)
- [ ] Error recovery (network failure → retry)
- [ ] Camera capture (1 FPS)
- [ ] RAG retrieves relevant past conversations
- [ ] WebSearch triggers for current info queries

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive AWS deployment guide.

**Quick local deployment:**
1. Backend: `cd backend && ./start_local.sh`
2. Frontend: `cd frontend && flutter run`

**Production deployment:**
- Backend: Docker + AWS ECS/Fargate (see [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md))
- Frontend: Build release APK/iOS → Distribute

## Important Files to Know

**Backend:**
- [backend/main.py](backend/main.py) - FastAPI app entry point, all endpoints
- [backend/services/master_directive_processor.py](backend/services/master_directive_processor.py) - Core orchestration
- [backend/prompts/master_directive.py](backend/prompts/master_directive.py) - AI personality definition
- [backend/setup_local.sh](backend/setup_local.sh) - Local setup automation
- [backend/requirements.txt](backend/requirements.txt) - Python dependencies

**Frontend:**
- [frontend/lib/main.dart](frontend/lib/main.dart) - App entry point, permissions
- [frontend/lib/screens/voice_first_screen.dart](frontend/lib/screens/voice_first_screen.dart) - Main screen
- [frontend/lib/services/api_service.dart](frontend/lib/services/api_service.dart) - Backend communication
- [frontend/lib/utils/constants.dart](frontend/lib/utils/constants.dart) - Configuration (UPDATE IP HERE)
- [frontend/pubspec.yaml](frontend/pubspec.yaml) - Flutter dependencies

**Documentation:**
- [README.md](README.md) - Project overview and quick start
- [PROJECT_EDEN_V2_MASTER_SPEC.md](PROJECT_EDEN_V2_MASTER_SPEC.md) - Complete specification
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - RAG & WebSearch details
- [DEPLOYMENT.md](DEPLOYMENT.md) - AWS deployment guide

## Troubleshooting

**Backend won't start:**
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill
cd backend && ./start_local.sh
```

**Frontend can't connect to backend:**
1. Verify AWS EC2 backend is running: `curl http://3.39.177.218:8000/health`
2. Check WiFi/mobile data connection on device
3. Verify `frontend/lib/utils/constants.dart` has EC2 IP: `http://3.39.177.218:8000`
4. Check if EC2 security group allows inbound port 8000
5. If testing locally: Ensure phone and computer on same WiFi network

**ChromaDB errors:**
```bash
# Delete and reinitialize ChromaDB
rm -rf backend/chroma_db/
# Restart backend - will recreate ChromaDB
cd backend && ./start_local.sh
```

**Flutter build errors:**
```bash
cd frontend
flutter clean
rm -rf .dart_tool/
flutter pub get
flutter run
```

## Key Concepts

**One Thing:** The user's single most important goal. AI keeps user focused on this.

**Core Pitfall:** User's primary distraction pattern (e.g., "Capability Trap" - spreading too thin).

**Benevolent Dissent:** AI warns when user asks about things that conflict with their One Thing.

**Am-muk-ji (암묵지):** Korean term for implicit knowledge. System learns user traits through observation, not explicit declaration.

**Trait Weights:** Personality traits (0.0-1.0 scale) that increase with reinforcement and decay without it.

**Profile Maturity:** Calculated from conversation count and trait confidence (Early → Growing → Established → Mature).
