# Garden of Eden - AI Growth Mentor System

> An adaptive AI mentor that learns how to teach you better through every conversation

## 📖 Project Overview

**Garden of Eden** is an AI-powered growth mentor system that uses Socratic methodology and neural network-inspired learning to help users achieve their goals. Unlike traditional AI assistants that solve problems for you, Garden of Eden teaches you to think and solve problems yourself.

### Vision & Goals

- **Teach Thinking, Not Solutions**: Use Socratic questioning to develop user's critical thinking capacity
- **Adaptive Personalization**: Learn optimal mentoring style through backpropagation-inspired feedback analysis
- **Voice-First Experience**: Natural conversation through STT/TTS for seamless interaction
- **Growth Mindset Focus**: Encourage self-discovery, autonomy, and continuous learning
- **Goal-Oriented Guidance**: Keep users aligned with their "One Thing" (primary life goal)

### Core Philosophy

The system is built on three principles:
1. **Socratic Method**: Ask questions that make users think, rather than providing direct answers
2. **Growth Mindset**: Frame challenges as learning opportunities, celebrate progress
3. **Adaptive Learning**: Continuously adjust mentoring approach based on what works for each individual

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Flutter)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Onboarding  │→ │  Persona     │→ │ Voice-First  │          │
│  │  Screen      │  │  Selection   │  │   Screen     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         ↓                                    ↓                   │
│  ┌──────────────────────────────────────────────────┐           │
│  │         Riverpod State Management                 │           │
│  │  • OnboardingProvider  • SessionProvider          │           │
│  │  • AppStateProvider    • ProfileProvider          │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI - Python)                   │
│  ┌──────────────────────────────────────────────────┐           │
│  │              API Routes (/api/v2/*)               │           │
│  │  • /onboarding  • /session  • /chat  • /profile  │           │
│  └──────────────────────────────────────────────────┘           │
│         ↓                ↓                ↓                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐            │
│  │ Onboarding  │  │   Session   │  │ Conversation │            │
│  │  Service    │  │   Service   │  │   Service    │            │
│  └─────────────┘  └─────────────┘  └──────────────┘            │
│         ↓                                    ↓                   │
│  ┌─────────────────────────────────────────────────┐            │
│  │      Master Directive Processor Service         │            │
│  │  (Builds dynamic AI prompts with preferences)   │            │
│  └─────────────────────────────────────────────────┘            │
│         ↓                                    ↓                   │
│  ┌──────────────┐                   ┌──────────────┐            │
│  │ Gemini 2.0   │                   │   Profile    │            │
│  │ Flash (LLM)  │                   │   Learning   │            │
│  │   Service    │                   │   Service    │            │
│  └──────────────┘                   └──────────────┘            │
│         ↓                                    ↓                   │
│  ┌─────────────────────────────────────────────────┐            │
│  │         DynamoDB (AWS - Seoul Region)           │            │
│  │  • UserProfiles  • Conversations  • Sessions    │            │
│  └─────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Frontend (Flutter)
- **Screens**: Onboarding (6-step Socratic), Persona Selection, Voice-First Chat, Profile
- **Providers**: State management with Riverpod (onboarding, session, app state, profile)
- **Services**: Camera, Audio (STT recording), API Client
- **UI**: Material Design with custom dark theme, voice-first UX

#### Backend (FastAPI)
- **API Layer**: RESTful endpoints for onboarding, sessions, chat, profiles
- **Services**: Onboarding, Session, Conversation, Profile Learning, LLM (Gemini)
- **Database**: DynamoDB for profiles, conversations, sessions, learning events
- **AI**: Gemini 2.0 Flash for generation, backpropagation-style learning

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1 (Python 3.11)
- **AI/ML**: Google Gemini 2.0 Flash (`gemini-2.0-flash-exp`)
- **Database**: AWS DynamoDB (NoSQL)
- **Cloud Services**:
  - AWS EC2 (ap-northeast-2 - Seoul)
  - Google Cloud AI Platform (Gemini API)
  - Google Cloud Speech-to-Text
  - Google Cloud Text-to-Speech
- **Key Libraries**:
  - `boto3` - AWS SDK for DynamoDB
  - `google-generativeai` - Gemini API
  - `pydantic` - Data validation
  - `uvicorn` - ASGI server

### Frontend
- **Framework**: Flutter 3.x (Dart)
- **State Management**: Riverpod (`flutter_riverpod`)
- **HTTP Client**: Dio (with retry logic)
- **Camera**: `camera` package
- **Audio**: `record` package (STT), `audioplayers` (TTS playback)
- **Permissions**: `permission_handler`
- **Storage**: `shared_preferences` (local cache)

### Infrastructure
- **Deployment**: AWS EC2 t3.medium (Seoul region)
- **Process Manager**: systemd service (`eden-backend.service`)
- **Port**: 8000 (HTTP)
- **Domain**: 3.39.177.218:8000

---

## 🧠 AI/ML Components

### 1. Gemini 2.0 Flash (LLM)
- **Model**: `gemini-2.0-flash-exp`
- **Purpose**: Conversation generation, onboarding analysis, learning extraction
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Max Tokens**: 2048 output

### 2. Backpropagation-Style Learning System

Inspired by neural network training, the system adjusts 5 weighted preferences after each conversation:

```python
# Learning Rate: 0.05 (smaller than trait learning rate 0.1)
PREF_LEARNING_RATE = 0.05

# 5 Weighted Preferences (0.0 - 1.0 scale):
- prefers_questions_over_answers    # Socratic vs direct guidance
- responds_to_encouragement          # Emotional vs logical motivation
- needs_logical_structure            # Structured vs intuitive approach
- values_autonomy                    # Self-direction vs guidance
- growth_mindset_strength            # Growth vs fixed mindset
```

**Feedback Signal Detection** (Korean language patterns):

**Positive Signals** → Increase weight (+0.05):
- Deep thinking: "왜" (why), "어떻게" (how), "생각해보니" (now that I think)
- Proposes solutions: "시도해볼게요" (I'll try), "해보겠습니다" (I will do it)
- Growth mindset: "배우" (learn), "성장" (growth), "아직 못" (not yet)

**Negative Signals** → Decrease weight (-0.05):
- Confusion: "무슨 말" (what do you mean), "이해가 안" (don't understand)
- Fixed mindset: "못해" (can't), "안 돼" (won't work)
- Very short responses: < 10 characters (disengagement)

### 3. Master Directive System

Dynamic prompt construction that injects weighted preferences:

```python
# Example prompt injection based on preferences:
if prefers_questions_over_answers > 0.7:
    "Ask 2-3 Socratic questions instead of direct answers"

if responds_to_encouragement > 0.7:
    "Celebrate small wins and acknowledge progress"

if needs_logical_structure > 0.7:
    "Break down thinking into clear numbered steps"

if values_autonomy > 0.7:
    "Let them propose solutions first, then guide"
```

### 4. Socratic Onboarding (6 Steps)

Extracts user's "One Thing" and initial personality profile:

1. **General focus**: "What's most important to you right now?"
2. **Motivation**: "How will your life be different when you achieve that?"
3. **Obstacles**: "What's the biggest barrier preventing you?"
4. **Ideal state**: "If that barrier didn't exist, what would you be doing?"
5. **Daily actions**: "What's a small action you could do daily?"
6. **Crystallization**: "Express this goal in one sentence"

**Extraction Output**:
- `one_thing`: Primary goal (user's own words)
- `core_motivation`: Deeper "why"
- `core_pitfall`: Main obstacle pattern
- `personality_traits_weighted`: 5-8 traits with confidence scores (0.0-1.0)
- `learning_preferences`: Initial estimates for 5 weighted parameters

---

## ✨ Core Features

### 1. Adaptive Mentor Personas

**Adam (Socratic Questioner)**:
- Asks deep, thought-provoking questions
- Challenges assumptions gently
- Guides toward self-discovery
- Analytical, intellectual approach

**Eve (Encouraging Catalyst)**:
- Nurtures growth with warmth
- Celebrates progress and potential
- Provides emotional support
- Intuitive, empathetic approach

### 2. Session Lifecycle Management

```
Session TTL: 10 minutes (600 seconds)
Auto-Refresh Threshold: 8 minutes (80% of TTL)

Timer checks every 1 minute:
- If lastActivity > 8 min → Auto-refresh session
- If lastActivity > 10 min → Session expired

Benefits:
- Prevents conversation interruption
- Maintains conversation context
- Seamless user experience
```

### 3. Voice-First UX

- **Push-to-Talk**: Hold button to record question
- **STT**: Google Cloud Speech-to-Text (Korean)
- **TTS**: Google Cloud Text-to-Speech (Korean voice)
- **Visual Context**: Camera captures (8 keyframes at 1 FPS)
- **Auto-Hide**: Response overlay disappears after 3 seconds

### 4. Pitfall Detection

Warns user when conversation drifts from "One Thing":

```python
# Topic alignment calculation:
topic_alignment = cosine_similarity(current_topic, one_thing_embedding)

if topic_alignment < 0.7:
    trigger_pitfall_warning = True
    message = "주의: One Thing에서 벗어나고 있습니다!"
```

### 5. Profile Learning & Evolution

After every conversation:
1. Extract insights (traits, emotional state, thinking patterns)
2. Calculate feedback signals from user response
3. Adjust weighted preferences (±0.05)
4. Apply time decay to unused traits
5. Update profile version
6. Log learning event to DynamoDB

**Profile Maturity Stages**:
- **Seed** (0-4 conversations): Initial formation
- **Sprout** (5-9): Early patterns emerging
- **Sapling** (10-19): Stable patterns
- **Young Tree** (20-49): Mature understanding
- **Mature Tree** (50-99): Deep personalization
- **Ancient Tree** (100+): Mastery-level adaptation

---

## 📊 Data Models

### UserProfile
```python
{
    "user_id": str,
    "profile_version": int,
    "one_thing": str,  # Primary goal
    "core_pitfall": str,  # Main obstacle pattern
    "personality_traits": {
        "trait_name": {
            "weight": float (0.0-1.0),
            "evidence_count": int,
            "last_updated": datetime
        }
    },
    "learning_preferences": {
        "prefers_questions_over_answers": float (0.0-1.0),
        "responds_to_encouragement": float (0.0-1.0),
        "needs_logical_structure": float (0.0-1.0),
        "values_autonomy": float (0.0-1.0),
        "growth_mindset_strength": float (0.0-1.0)
    },
    "thinking_patterns": {...},
    "emotional_snapshots": [...],
    "total_conversations": int,
    "last_updated": datetime
}
```

### SessionInfo
```python
{
    "session_id": str (UUID),
    "user_id": str,
    "persona": str ("adam" | "eve"),
    "created_at": datetime,
    "last_activity": datetime,
    "expires_at": datetime,  # created_at + 10 minutes
    "turn_count": int,
    "is_active": bool
}
```

### OnboardingResult
```python
{
    "one_thing": str,
    "core_motivation": str,
    "core_pitfall": str,
    "personality_hints": [str, ...],
    "personality_traits_weighted": {
        "trait_name": float (0.0-1.0)
    },
    "thinking_style": str,
    "learning_preferences": {...},
    "summary": str
}
```

### ConversationAnalysis
```python
{
    "discovered_traits": [NewTrait, ...],
    "reinforced_traits": [TraitUpdate, ...],
    "emotional_state": {
        "state": str,
        "trigger": str,
        "intensity": float (0.0-1.0)
    },
    "main_topic": str,
    "topic_alignment": float (0.0-1.0),
    "goal_modification_detected": bool
}
```

---

## 🔌 API Endpoints

### Onboarding
```
POST /api/v2/onboarding/start
- Body: { user_id, persona }
- Returns: { session_id, step, question, completed }

POST /api/v2/onboarding/respond
- Body: { session_id, user_response }
- Returns: { session_id, step, question, completed, result? }

GET /api/v2/onboarding/status/{session_id}
- Returns: { session_id, step, completed }
```

### Session Management
```
POST /api/v2/session/create
- Body: { user_id, persona }
- Returns: SessionInfo

GET /api/v2/session/{session_id}
- Returns: SessionInfo

GET /api/v2/session/user/{user_id}
- Returns: SessionInfo | null (active session)

POST /api/v2/session/{session_id}/close
- Body: { reason }
- Returns: { success: true }
```

### Conversation
```
POST /api/v2/chat
- Form Data:
  - user_id: str
  - message: str
  - voice_type: "adam" | "eve"
  - session_id: str (optional)
  - audio_file: File (optional)
  - camera_frames: [File] (optional)
- Returns: {
    response_text: str,
    response_audio_base64: str,
    pitfall_warning_triggered: bool,
    session_id: str
  }
```

### Profile
```
GET /api/v2/profile/{user_id}
- Returns: UserProfile

PATCH /api/v2/profile/{user_id}
- Body: { one_thing?, core_identity?, core_motivation? }
- Returns: UserProfile
```

### STT (Speech-to-Text)
```
POST /api/v2/stt
- Form Data:
  - audio_file: File
  - language: str (default "ko")
- Returns: { text: str }
```

---

## 🚀 Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.template .env
# Edit .env with your API keys:
# - GEMINI_API_KEY
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_REGION (ap-northeast-2)

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Required Environment Variables**:
```bash
# Google AI
GEMINI_API_KEY=<your-gemini-api-key>

# AWS DynamoDB
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_REGION=ap-northeast-2

# Optional
LOG_LEVEL=INFO
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
flutter pub get

# Run on device/emulator
flutter run

# Build for production
flutter build apk  # Android
flutter build ios  # iOS
```

**Configure API Endpoint** ([frontend/lib/utils/constants.dart](frontend/lib/utils/constants.dart)):
```dart
class ApiConfig {
  static const String baseUrl = 'http://3.39.177.218:8000';
  // For local development: 'http://localhost:8000'
}
```

---

## 🌐 Deployment

### AWS EC2 Deployment (Production)

**Instance**: t3.medium (Seoul - ap-northeast-2)
**OS**: Ubuntu 22.04 LTS
**Port**: 8000

**Setup Steps**:

```bash
# 1. SSH into EC2
ssh -i ~/.ssh/Eden_Key.pem ubuntu@3.39.177.218

# 2. Clone repository
git clone https://github.com/wannahappyaroundme/Garden_of_Eden.git
cd Garden_of_Eden/backend

# 3. Run automated setup
chmod +x setup_local.sh
./setup_local.sh

# 4. Configure systemd service
sudo nano /etc/systemd/system/eden-backend.service

# 5. Enable and start service
sudo systemctl enable eden-backend
sudo systemctl start eden-backend

# 6. Check status
sudo systemctl status eden-backend
```

**Systemd Service Configuration**:
```ini
[Unit]
Description=Garden of Eden Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Garden_of_Eden/backend
Environment="PATH=/home/ubuntu/Garden_of_Eden/backend/venv/bin"
ExecStart=/home/ubuntu/Garden_of_Eden/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Monitoring**:
```bash
# View logs
sudo journalctl -u eden-backend -f

# Restart service
sudo systemctl restart eden-backend
```

---

## 📱 User Flow

### First-Time User
1. **Permissions**: Grant camera & microphone access
2. **Persona Selection**: Choose Adam (Socratic) or Eve (Encouraging)
3. **Onboarding**: Complete 6-step Socratic dialogue (voice)
   - Questions extract "One Thing" and personality traits
   - Backend creates UserProfile with initial preferences (0.5 default)
4. **Main Chat**: Voice conversation with chosen mentor
   - Session auto-created (10min TTL)
   - Every response triggers learning pipeline
   - Preferences adapt based on feedback signals

### Returning User
1. **Permissions**: Auto-approved (cached)
2. **Direct to Chat**: Skip onboarding (completed flag set)
3. **Session Resume**: Load existing session or create new
4. **Continuous Learning**: Profile evolves with every conversation

### Example Learning Cycle

**Conversation 1**: User gives short, confused responses
- Feedback signal: `seems_confused = True`
- Action: `prefers_questions_over_answers -= 0.05`
- Result: Next response has more direct guidance

**Conversation 5**: User asks deep "why" questions, proposes solutions
- Feedback signals: `shows_deep_thinking = True`, `proposes_own_solutions = True`
- Action: `prefers_questions_over_answers += 0.05`, `values_autonomy += 0.05`
- Result: Next response asks 2-3 Socratic questions instead of giving answers

**Conversation 20**: User responds well to encouragement
- Feedback signal: `motivated_by_encouragement = True`
- Action: `responds_to_encouragement += 0.05`
- Result: AI celebrates wins more frequently

---

## 🎯 Key Differentiators

1. **Teaches Thinking, Not Solutions**: Only AI mentor that uses pure Socratic method
2. **Neural Network-Inspired Learning**: Backpropagation-style adaptation (unprecedented in chatbots)
3. **5-Dimensional Personalization**: Weighted preferences create unique mentor for each user
4. **Voice-First Korean UX**: Optimized for natural Korean conversation patterns
5. **Session Auto-Refresh**: Seamless long conversations without interruption
6. **Growth Mindset Detection**: Identifies and reinforces growth vs fixed mindset language

---

## 📈 Future Enhancements

- [ ] Multi-modal learning (image, video context analysis)
- [ ] Goal progress tracking with metrics
- [ ] Habit formation coaching
- [ ] Community features (mentor matching, shared goals)
- [ ] Advanced RAG (Retrieval-Augmented Generation) for domain knowledge
- [ ] Multi-language support (English, Japanese)
- [ ] Wearable integration (Apple Watch, Galaxy Watch)
- [ ] Emotion recognition from voice tone analysis

---

## 📄 License

Proprietary - All Rights Reserved

---

## 🤝 Contributors

- **Lead Developer**: Built with Claude Code
- **Project Owner**: @wannahappyaroundme

---

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/wannahappyaroundme/Garden_of_Eden/issues
- Email: [Your contact email]

---

**Last Updated**: 2025-01-06
**Version**: 2.0.0
**Status**: Production
