# 🌟 Project Eden V2

**A J.A.R.V.I.S.-like AI Partner That Deeply Understands You**

Version: 2.0.0 | Status: Phases 1-3 Complete ✅ | Ready for Testing 🚀

---

## 🎉 Latest Update: Phase 4 Ready!

**All preparation complete - ready to test!**

- ✅ **Phase 1**: Backend Core - Complete
- ✅ **Phase 2**: Flutter Mobile App - Complete
- ✅ **Phase 3**: Platform Configuration - Complete
- 🚀 **Phase 4**: Testing documentation + scripts ready!

**Start Testing**: See [PHASE_4_START_HERE.md](./PHASE_4_START_HERE.md) for setup!
**Backend Scripts**: `./setup_local.sh` and `./start_local.sh` created

---

## What is Project Eden?

Project Eden is NOT a chatbot. It's a **deeply personalized AI partner** that:

- 🧠 **Learns who you are** over time (Am-muk-ji / 암묵지 - implicit knowledge)
- 🎯 **Keeps you focused** on your "One Thing" (singular most important goal)
- ⚠️ **Warns when you stray** through "Benevolent Dissent"
- 💚 **Supports you emotionally** when you struggle
- 🎭 **Adapts its personality** (Adam: logical/father-like, Eve: energetic/uplifting)
- 📹 **Sees what you see** through camera integration
- 🎤 **Listens to you** through voice-first interaction

**This is J.A.R.V.I.S., not Siri.**

---

## Core Innovation: Am-muk-ji Learning System

Traditional AI: Stores conversations
**Eden V2**: **Learns you like a human mentor would**

The AI builds a living profile with **weighted personality traits** (inspired by neural networks):
- Traits observed frequently → weight increases (0.5 → 0.9)
- Traits not reinforced recently → weight decays (0.8 → 0.6)
- AI gets "smarter" about you over time

Example traits tracked:
- `perfectionist` (weight: 0.87)
- `night_owl` (weight: 0.93)
- `visual_learner` (weight: 0.76)
- `stress_prone_when_uncertain` (weight: 0.69)

---

## Key Features

### 1. Master Directive System

Every AI response is filtered through:
- ✅ Your user profile (Core Identity, One Thing, Core Pitfall)
- ✅ Recent memory (last 10 conversations)
- ✅ Current input (voice + camera + text)
- ✅ Pitfall detection (alignment check)
- ✅ Emotional state detection

### 2. Benevolent Dissent

When you ask about something that triggers your **Core Pitfall**, AI intervenes:

**Example:**
```
User: "Should I learn SLAM algorithms?"
AI (Adam): "잠깐만요. SLAM은 흥미로운 분야지만,
           지금 당신의 One Thing인 SNU HCI Lab과 어떤 연결고리가 있나요?
           이건 당신의 '능력 함정' 패턴으로 보입니다.
           에너지가 분산되면 HCI 연구 준비에서 멀어질 수 있어요."
```

### 3. Dual Personas

**Adam (아담)**
- Male voice, logical, father-like
- Uses questions to guide thinking
- Direct but caring
- Example: "먼저 생각해봅시다. 이 선택이 목표와 어떻게 연결되나요?"

**Eve (이브)**
- Female voice, energetic, uplifting
- Celebrates and validates warmly
- Makes you feel good naturally
- Example: "와! 정말 대단한데요! 당신은 이미 충분히 잘하고 있어요!"

### 4. Profile Evolution

**Week 1**: Basic profile, AI asks questions
**Week 4**: Patterns emerge, 5-7 traits discovered
**Week 12**: Mature profile, AI "knows" you deeply
**Month 6+**: J.A.R.V.I.S.-level partnership - predicts needs, intervenes proactively

---

## Technical Stack

### Backend (✅ Phase 1 Complete)
- **Framework**: FastAPI 0.109.2 (Python 3.12)
- **Database**: AWS DynamoDB (NoSQL, free tier)
- **LLM**: Google Gemini 1.5 Flash (FREE, vision support)
- **STT**: Groq Whisper Large v3 (FREE, 14,400 req/day)
- **TTS**: Edge TTS (FREE unlimited, Korean voices)
- **Search**: DuckDuckGo (FREE)

### Frontend (✅ Phase 2 Complete)
- **Framework**: Flutter 3.35.7+
- **State**: Riverpod 3.0
- **Platform**: iOS & Android (mobile-first)
- **UI**: Voice-first with full-screen camera
- **Audio**: Record (recording) + Just Audio (playback)
- **Camera**: 1 FPS capture with keyframe selection

### Infrastructure
- **Deployment**: Docker + AWS ECS/Fargate
- **Storage**: AWS S3 for camera frames
- **Monitoring**: CloudWatch
- **Cost**: ~$15-45/month total

---

## Project Structure

```
myai/
├── PROJECT_EDEN_V2_MASTER_SPEC.md    # Complete specification
├── README.md                          # This file
├── PHASE_1_COMPLETE.md                # ✅ Backend completion report
├── PHASE_2_COMPLETE.md                # ✅ Frontend completion report
├── PHASE_3_COMPLETE.md                # ✅ Configuration completion report
├── PHASE_3_DEPLOYMENT_GUIDE.md        # 📖 Full deployment guide
├── PHASE_3_QUICK_TEST.md              # ⚡ 5-minute quick start
├── backend/                           # ✅ Phase 1 Complete
│   ├── main.py                        # FastAPI app
│   ├── services/                      # Core services
│   │   ├── master_directive_processor.py
│   │   ├── profile_learning_service.py
│   │   ├── pitfall_detection_service.py
│   │   ├── llm_gemini_v2.py
│   │   ├── stt_service.py
│   │   ├── tts_service.py
│   │   └── dynamodb_service_v2.py
│   ├── models/                        # Data models
│   │   ├── user_profile.py
│   │   ├── conversation.py
│   │   └── api_schemas.py
│   ├── prompts/                       # Master Directive prompts
│   │   ├── master_directive.py
│   │   └── learning_analysis.py
│   ├── utils/                         # Utilities
│   │   ├── logger.py
│   │   └── constants.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── README.md
└── frontend/                          # ✅ Phase 2 Complete
    ├── lib/
    │   ├── main.dart                  # App entry + permissions
    │   ├── models/                    # Data models
    │   │   └── chat_models.dart
    │   ├── services/                  # Core services
    │   │   ├── api_service.dart       # Backend HTTP client
    │   │   ├── audio_service.dart     # Record + playback
    │   │   └── camera_service.dart    # 1 FPS capture
    │   ├── providers/                 # Riverpod state
    │   │   ├── app_state_provider.dart
    │   │   ├── service_providers.dart
    │   │   └── profile_provider.dart
    │   ├── widgets/                   # UI components
    │   │   ├── persona_toggle.dart
    │   │   ├── push_to_talk_button.dart
    │   │   ├── camera_view.dart
    │   │   └── response_overlay.dart
    │   ├── screens/                   # Screens
    │   │   └── voice_first_screen.dart
    │   ├── theme/                     # Theming
    │   │   └── app_theme.dart
    │   └── utils/                     # Constants
    │       └── constants.dart
    ├── ios/Runner/Info.plist          # ✅ Permissions configured
    ├── android/app/src/main/
    │   └── AndroidManifest.xml        # ✅ Permissions configured
    └── pubspec.yaml                   # Dependencies
```

---

## 🚀 Quick Start

### ⚡ Super Quick Start (5 minutes)

**Want to test immediately?** See [PHASE_3_QUICK_TEST.md](./PHASE_3_QUICK_TEST.md)

### 📖 Full Setup Guide

**For detailed instructions**, see [PHASE_3_DEPLOYMENT_GUIDE.md](./PHASE_3_DEPLOYMENT_GUIDE.md)

### Basic Setup

**1. Start Backend**
```bash
cd backend
docker-compose up -d
curl http://localhost:8000/health  # Verify
```

**2. Configure Mobile App**
```bash
# Get your local IP
ipconfig getifaddr en0  # macOS

# Edit frontend/lib/utils/constants.dart
# Change baseUrl to: http://YOUR_IP:8000
```

**3. Run on Device**
```bash
cd frontend
flutter pub get
flutter run  # Connect device first via USB
```

**4. Test!**
- Grant permissions when prompted
- Press and hold mic button
- Say something in Korean
- Release and wait for AI response

Server runs at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### Get API Keys (All FREE)

1. **Google Gemini**: https://ai.google.dev/
2. **Groq (Whisper)**: https://console.groq.com/
3. **AWS**: https://aws.amazon.com/ (Free tier: 25GB DynamoDB)

---

## API Example

### Chat with AI

```bash
curl -X POST "http://localhost:8000/api/v2/chat" \
  -F "user_id=user_123" \
  -F "message=SNU HCI Lab에 가고 싶어요" \
  -F "voice_type=adam"
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "response_text": "SNU HCI Lab 진학이 목표시군요! 정말 멋진 목표예요...",
  "response_audio_base64": "base64_mp3_data",
  "pitfall_warning_triggered": false,
  "emotional_support_mode": false,
  "profile_updated": true,
  "profile_version": 2,
  "processing_time_ms": 1847
}
```

---

## Implementation Phases

### ✅ Phase 1: Backend Core (Week 1) - **COMPLETE**
- FastAPI with Master Directive system
- DynamoDB service (3 tables)
- Gemini LLM integration (vision support)
- STT (Groq Whisper) + TTS (Edge TTS)
- Profile learning with weight updates
- Pitfall detection
- Docker deployment

### ✅ Phase 2: Flutter Mobile App (Week 2) - **COMPLETE**
- Voice-first UI with full-screen camera
- Push-to-talk button with state animations
- Persona toggle (Adam/Eve)
- Response overlay with glassmorphism
- Audio recording and playback
- Camera service (1 FPS capture)
- Riverpod state management
- Permission handling

### ✅ Phase 3: Platform Configuration (Week 3) - **COMPLETE**
- iOS permissions (Info.plist)
- Android permissions (AndroidManifest.xml)
- Deployment documentation
- Testing guides and checklists
- Quick start guide

### ⏸️ Phase 4: Testing & Integration (Week 3-4) - **NEXT**
- Test on physical devices (iOS + Android)
- Backend-frontend integration testing
- Voice + Camera multimodal testing
- Persona switching validation
- Profile learning verification
- Pitfall detection testing

### ⏳ Phase 5: UI/UX Polish (Week 4-5)
- Pitfall warning UI indicator
- Profile viewing screen
- Settings screen
- Retry logic for failed requests
- Loading state improvements
- Animation polish

### ⏳ Phase 6: Advanced Features (Week 5-6)
- Conversation history
- Enhanced trait extraction
- Emotional pattern analysis
- Goal tracking visualization
- Multi-user support

### ⏳ Phase 7: Production Ready (Week 7+)
- Error tracking (Sentry)
- Analytics (Firebase)
- Performance monitoring
- App Store deployment
- AWS production deployment

---

## Core Concept: The "One Thing"

Every user has **ONE primary goal** that matters most.

Examples:
- "Get into SNU HCI Lab"
- "Pass IELTS with 8.0"
- "Launch my startup by June"
- "Lose 15kg in 3 months"

AI's mission: **Keep you focused on this goal** and warn when you're distracted.

---

## Master Directive Prompt (Simplified)

```
🌟 [Project Eden: Master Directive] 🌟

[USER PROFILE]
One Thing: SNU HCI Lab admission
Core Pitfall: Competency Trap - energy scattering
Top Traits: night_owl (0.93), perfectionist (0.87)

[CURRENT INPUT]
User: "Should I learn Rust?"

[PITFALL CHECK]
Topic: "Rust programming"
Alignment with One Thing: 0.2 (WEAK)
→ BENEVOLENT DISSENT ACTIVATED

[RESPONSE]
잠깐만요. Rust는 훌륭한 언어죠. 하지만
지금 SNU HCI Lab 준비 중이시잖아요?
Systems programming이 HCI 연구에 꼭 필요한가요?
혹시 호기심 때문에 에너지가 분산되고 있는 건 아닐까요?
```

---

## Why This Will Work

1. **Personalization at scale**: Every user gets a unique AI that grows with them
2. **Real value**: Helps achieve tangible goals (not just entertainment)
3. **Emotional connection**: AI feels like it "knows" you
4. **Mobile-first**: Voice and camera make it effortless
5. **100% free core**: No API costs for MVP

---

## Current Status

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Backend Core | ✅ Complete | 100% |
| Phase 2: Mobile App | ✅ Complete | 100% |
| Phase 3: Platform Config | ✅ Complete | 100% |
| Phase 4: Testing & Integration | ⏸️ Ready | 0% |
| Phase 5: UI/UX Polish | ⏳ Pending | 0% |
| Phase 6: Advanced Features | ⏳ Pending | 0% |
| Phase 7: Production Ready | ⏳ Pending | 0% |

**MVP Status**: Phases 1-3 complete, ready for device testing!
**Next Step**: Test on physical device (see [PHASE_3_QUICK_TEST.md](./PHASE_3_QUICK_TEST.md))

---

## Documentation

### Core Documentation
- **Master Specification**: [PROJECT_EDEN_V2_MASTER_SPEC.md](PROJECT_EDEN_V2_MASTER_SPEC.md)
- **Backend README**: [backend/README.md](backend/README.md)
- **API Docs**: http://localhost:8000/docs (when running)

### Phase Completion Reports
- **Phase 1 Complete**: [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) - Backend implementation
- **Phase 2 Complete**: [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md) - Flutter mobile app
- **Phase 3 Complete**: [PHASE_3_COMPLETE.md](PHASE_3_COMPLETE.md) - Platform configuration

### Deployment & Testing
- **Quick Start (5 min)**: [PHASE_3_QUICK_TEST.md](PHASE_3_QUICK_TEST.md)
- **Full Deployment Guide**: [PHASE_3_DEPLOYMENT_GUIDE.md](PHASE_3_DEPLOYMENT_GUIDE.md)
- **Testing Checklist**: See Phase 3 Deployment Guide

---

## License

Private project - Not for distribution

---

## Vision

*"Project Eden is not a chatbot. It is a deeply personalized AI partner that understands you, learns from every interaction, and helps you achieve your One Thing while protecting you from distractions."*

**This is just the beginning.** 🚀
