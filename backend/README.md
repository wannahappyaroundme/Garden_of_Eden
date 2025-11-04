# Project Eden V2 - Backend

**J.A.R.V.I.S.-like AI Partner with Master Directive System**

Version: 2.0.0

---

## Overview

Project Eden V2 backend implements the **Master Directive System** - an AI companion that deeply learns who you are over time (Am-muk-ji / 암묵지) and keeps you focused on your "One Thing" goal through benevolent dissent.

### Key Features

- **Am-muk-ji Learning System**: AI learns personality traits with neural network-style weight updates
- **Master Directive**: Every response filtered through user's profile, goals, and pitfalls
- **Benevolent Dissent**: Warns when user strays from their One Thing
- **Dual Personas**: Adam (logical, father-like) and Eve (energetic, uplifting)
- **Multimodal**: Voice (STT) + Camera (vision) + Text
- **100% Free APIs**: Groq Whisper (STT), Gemini 1.5 Flash (LLM), Edge TTS

---

## Architecture

```
┌─────────────────────────────────────────┐
│     MasterDirectiveProcessor            │
│  (Main Orchestration)                   │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Profile      │  │ Pitfall         │ │
│  │ Learning     │  │ Detection       │ │
│  │ Service      │  │ Service         │ │
│  └──────────────┘  └─────────────────┘ │
│                                         │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Gemini LLM   │  │ DynamoDB        │ │
│  │ Service      │  │ Service         │ │
│  └──────────────┘  └─────────────────┘ │
│                                         │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ STT Service  │  │ TTS Service     │ │
│  │ (Groq)       │  │ (Edge TTS)      │ │
│  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
```

---

## Setup

### Prerequisites

- Python 3.12+
- AWS Account (for DynamoDB)
- API Keys:
  - Google Gemini API Key (FREE)
  - Groq API Key (FREE)

### Installation

1. **Clone the repository**

```bash
cd backend
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key

# Table names (can keep defaults)
DYNAMODB_PROFILES_TABLE=eden_user_profiles_v2
DYNAMODB_CONVERSATIONS_TABLE=eden_conversations_raw
DYNAMODB_LEARNING_EVENTS_TABLE=eden_learning_events
```

5. **Create DynamoDB tables**

```bash
python -m services.dynamodb_service_v2
```

This creates 3 tables:

- `eden_user_profiles_v2` (user profiles)
- `eden_conversations_raw` (conversation logs)
- `eden_learning_events` (learning history)

6. **Run the server**

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at `http://localhost:8000`

---

## API Documentation

### Interactive Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### 1. Chat (Main Endpoint)

**POST** `/api/v2/chat`

Process conversation through Master Directive system.

**Request** (multipart/form-data):

```
user_id: string (required)
message: string (required)
voice_type: "adam" | "eve" (required)
session_id: string (optional)
audio_file: file (optional)
camera_frames[]: file[] (optional, max 8)
```

**Response**:

```json
{
  "conversation_id": "uuid",
  "response_text": "AI response in Korean",
  "response_audio_base64": "base64_mp3",
  "pitfall_warning_triggered": false,
  "emotional_support_mode": false,
  "profile_updated": true,
  "profile_version": 9,
  "processing_time_ms": 1847
}
```

#### 2. Get Profile

**GET** `/api/v2/profile/{user_id}`

Get user profile summary.

**Response**:

```json
{
  "user_id": "user_123",
  "profile_version": 9,
  "one_thing": "SNU HCI Lab admission",
  "core_pitfall": "Competency Trap",
  "personality_summary": {
    "top_traits": [
      { "name": "night_owl", "weight": 0.93 },
      { "name": "perfectionist", "weight": 0.87 }
    ]
  },
  "recent_emotional_state": "anxious (0.7)",
  "total_conversations": 156,
  "profile_maturity": "high",
  "last_updated": "2025-01-15T14:30:00Z"
}
```

#### 3. Update Profile

**PATCH** `/api/v2/profile/{user_id}`

Manually update profile.

**Request**:

```json
{
  "one_thing": "New goal if changed",
  "core_identity": "Updated identity",
  "core_motivation": "Updated motivation"
}
```

#### 4. Learning Events

**GET** `/api/v2/learning/events/{user_id}?limit=50`

Get profile learning history.

#### 5. STT (Speech-to-Text)

**POST** `/api/v2/stt`

Transcribe audio to text.

**Request** (multipart/form-data):

```
audio_file: file (required)
language: string (default: "ko")
```

#### 6. Health Check

**GET** `/health`

Check service health.

---

## Core Services

### 1. MasterDirectiveProcessor

Main orchestrator. Coordinates all services to process conversations.

**Flow**:

1. Load user profile
2. Check for pitfall (benevolent dissent)
3. Detect emotional state
4. Generate persona-aware response
5. Generate TTS audio
6. Learn from conversation
7. Return response

### 2. ProfileLearningService

Implements Am-muk-ji (implicit knowledge) learning.

**Weight Update Algorithm**:

```python
def update_weight(current, evidence_strength, days_since_update):
    # Time decay
    if days_since_update > 7:
        decay = 0.02 * (days_since_update - 7)
        current = max(0.3, current - decay)

    # Positive reinforcement
    delta = 0.1 * evidence_strength
    new_weight = min(1.0, current + delta)

    return new_weight
```

### 3. PitfallDetectionService

Detects when user strays from their "One Thing".

**Alignment Scoring**:

- 1.0: Directly helps goal
- 0.7-0.9: Indirectly related
- 0.4-0.6: Tangentially related
- 0.1-0.3: Unrelated but possibly relevant
- 0.0: Completely unrelated

If alignment < 0.3 → Benevolent dissent activated

### 4. GeminiService

Handles all LLM interactions.

- **Master Directive responses**: Persona-aware, profile-based
- **Learning analysis**: Extract traits from conversations
- **Topic extraction**: For pitfall detection

### 5. DynamoDBService

Manages all database operations.

**Tables**:

- User profiles (complex nested structure)
- Conversations (full message history)
- Learning events (profile update logs)

---

## Master Directive System

Every AI response goes through the Master Directive prompt:

```
🌟 [Project Eden: Master Directive] 🌟

[1. USER PROFILE - Am-muk-ji]
- Core Identity
- Core Motivation
- One Thing
- Core Pitfall
- Personality Traits (weighted)
- Emotional Patterns

[2. CONVERSATION PERSONA]
- Adam or Eve

[3. RECENT MEMORY]
- Last 10 conversations

[4. CURRENT INPUT]
- User's message
- Visual context (camera frames)

[5. MISSION - Critical Rules]
✓ Holistic Analysis
✓ Persona Adherence
✓ Core Pitfall Detection ⚠️
✓ Emotional State Detection
✓ Korean Response (concise, in-character)
```

---

## Personas

### Adam (아담)

- Voice: `ko-KR-InJoonNeural` (male)
- Style: Logical, structured, father-like
- Approach: Uses questions to guide thinking
- Example: "먼저 생각해봅시다. 이 선택이 목표와 어떻게 연결되나요?"

### Eve (이브)

- Voice: `ko-KR-SunHiNeural` (female)
- Style: Energetic, uplifting, enthusiastic
- Approach: Positive reactions and celebrations
- Example: "오! 정말 멋진데요! 당신은 이미 충분히 잘하고 있어요!"

---

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t eden-backend .

# Run container
docker run -d \
  --name eden_backend \
  -p 8000:8000 \
  --env-file .env \
  eden-backend
```

### Using Docker Compose

```bash
docker-compose up -d
```

### AWS ECS Deployment

1. Push image to ECR
2. Create ECS task definition
3. Configure Fargate service
4. Setup ALB with HTTPS
5. Configure auto-scaling

Estimated cost: $15-30/month (1 vCPU, 2GB RAM)

---

## Testing

### Unit Tests

```bash
pytest tests/
```

### Test Individual Services

```python
# Test STT
from services.stt_service import STTService

stt = STTService()
text = await stt.transcribe_audio("audio.mp3")
print(text)
```

```python
# Test TTS
from services.tts_service import TTSService
from utils.constants import PersonaType

tts = TTSService()
audio_path = await tts.generate_speech(
    text="안녕하세요!",
    persona=PersonaType.ADAM
)
print(f"Audio saved: {audio_path}")
```

```python
# Test Profile Learning
from services.profile_learning_service import ProfileLearningService

service = ProfileLearningService(llm_service, db_service)
updated_profile = await service.learn_from_conversation(
    user_id="test_user",
    conversation=conversation
)
```

---

## Monitoring & Logs

Logs are written to:

- Console (INFO level)
- `logs/eden_errors.log` (ERROR level, rotated at 10MB)
- `logs/eden_all.log` (DEBUG level, rotated at 50MB)

View logs:

```bash
tail -f logs/eden_all.log
```

---

## Performance

**Target Latency**:

- STT: < 2 seconds
- LLM: < 3 seconds
- TTS: < 1 second
- Total: < 6 seconds

**Scalability**:

- 100 concurrent users per server
- Auto-scales with ECS

---

## Troubleshooting

### DynamoDB Connection Issues

```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify tables exist
aws dynamodb list-tables --region us-east-1
```

### API Key Issues

```bash
# Test Gemini
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('✓ Gemini OK')"

# Test Groq
python -c "from groq import Groq; client = Groq(api_key='YOUR_KEY'); print('✓ Groq OK')"
```

### Import Errors

Make sure you're in the backend directory and virtual environment is activated:

```bash
pwd  # Should be .../Garden_of_Eden/backend
which python  # Should show venv path
```

---

## Next Steps

1. ✅ Backend Core (Phase 1) - **COMPLETE**
2. ⏳ Flutter Mobile App (Phase 2)
3. ⏳ Multimodal Integration (Phase 3)
4. ⏳ Advanced Learning (Phase 4)

---

## Contributing

This is a personal project for now, but suggestions are welcome!

---

## License

Private - Not for distribution

---

## Contact

For questions about Project Eden V2, please refer to the master specification:
`PROJECT_EDEN_V2_MASTER_SPEC.md`
