# 🌱 Garden of Eden - AI Personal Mentor System

<div align="center">

**"Teach Thinking, Not Solutions"**

A sophisticated AI mentor that learns your personality through neural network-inspired algorithms and helps you stay focused on your "One Thing" through Socratic dialogue.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Flutter 3.35+](https://img.shields.io/badge/flutter-3.35+-blue.svg)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Installation Guide](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [한국어](README_KR.md)

</div>

---

## 📖 Overview

**Garden of Eden** (Project Eden V2) is a production-ready AI personal mentor system that combines:

- 🧠 **Neural Network-Inspired Learning**: Weighted trait system with time decay
- 🎯 **Goal-Focused Mentorship**: "Benevolent Dissent" to redirect you when distracted
- 🗣️ **Voice-First Experience**: Natural Korean conversation with STT/TTS
- 📚 **RAG + Web Search**: Semantic memory + current information
- 👥 **Dual Personas**: Adam (Socratic questioner) & Eve (encouraging catalyst)
- 📊 **Continuous Adaptation**: Backpropagation-style learning from user feedback

---

## ✨ Key Features

### 1. **Am-muk-ji Learning** (암묵지 - Implicit Knowledge)
- Learns your personality traits implicitly through conversation analysis
- Weighted traits (0.0-1.0) with evidence tracking
- Time decay mechanism (traits fade if not reinforced)
- Profile maturity progression (NEW → EXPERT over 120+ conversations)

### 2. **Pitfall Detection** (선의의 반대)
- Detects when you stray from your "One Thing" goal
- Alignment score calculation (0.0-1.0)
- Triggers gentle warnings when alignment < 0.3
- Custom warning phrases based on your Core Pitfall

### 3. **5D Learning Preference Adaptation**
Adjusts mentoring style across 5 dimensions:
1. Questions vs Answers (Socratic level)
2. Encouragement vs Logic (motivation style)
3. Structure vs Intuition (organization preference)
4. Autonomy vs Guidance (independence level)
5. Growth Mindset Strength

### 4. **RAG (Retrieval-Augmented Generation)**
- 384-dimensional semantic embeddings
- Finds relevant past conversations (weeks/months ago)
- Top-5 similarity search with 0.5 threshold
- ChromaDB vector database

### 5. **Smart Web Search Integration**
- Keyword-triggered web search (confidence >= 0.3)
- Tavily API (high-quality) + DuckDuckGo (fallback)
- Automatic detection of current events/factual queries

### 6. **Goal Progress Tracking**
- Visual milestones and sub-goals
- Progress snapshots with mood tracking
- AI-generated insights and trend analysis
- Weekly summaries and encouragement

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│         Frontend (Flutter Mobile App)              │
│  • Riverpod State Management                       │
│  • Voice/Camera Services                           │
│  • 8 Screens (Onboarding, Chat, Profile, etc.)    │
└──────────────────┬─────────────────────────────────┘
                   │ REST API (JSON + Multipart)
                   ↓
┌────────────────────────────────────────────────────┐
│       Backend (FastAPI - Python 3.12)              │
│  ┌──────────────────────────────────────────────┐  │
│  │   Master Directive Processor                 │  │
│  │  (Orchestrates all AI services)              │  │
│  └──────────────────────────────────────────────┘  │
│      ↓          ↓          ↓           ↓           │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌─────────┐     │
│  │ Gemini │ │Profile │ │  RAG   │ │WebSearch│     │
│  │  LLM   │ │Learning│ │Service │ │ Service │     │
│  └────────┘ └────────┘ └────────┘ └─────────┘     │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│   Data Layer (DynamoDB + ChromaDB)                 │
│  • User Profiles (weighted traits)                 │
│  • Conversations (full history)                    │
│  • Learning Events (profile updates)               │
│  • Goal Progress (milestones, snapshots)           │
│  • Vector Embeddings (semantic search)             │
└────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+** and **Flutter 3.35+**
- **API Keys** (all FREE tier):
  - [Google Gemini](https://aistudio.google.com/app/apikey)
  - [Groq (Whisper STT)](https://console.groq.com/keys)
  - [Tavily (Optional)](https://tavily.com/)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/Garden_of_Eden.git
cd Garden_of_Eden/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:** http://localhost:8000/health

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
flutter pub get

# Run on device
flutter run

# Build APK (Android)
flutter build apk --release

# Build iOS (requires Mac + Xcode)
flutter build ios --release
```

📖 **Full installation guide:** [INSTALL_GUIDE.md](INSTALL_GUIDE.md)

---

## 🤖 AI Models Used

| Service | Model | Purpose | Cost |
|---------|-------|---------|------|
| **LLM** | Gemini 2.5 Flash | Conversation, learning analysis | FREE (1M tokens/day) |
| **STT** | Groq Whisper Large v3 | Voice → Text (Korean) | FREE (14.4K requests/day) |
| **TTS** | Google TTS (gTTS) | Text → Voice (Korean) | FREE unlimited |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | RAG semantic search | FREE (local) |
| **Web Search** | Tavily API + DuckDuckGo | Current information | FREE (1K searches/month) |

**Total cost:** $0/month (plus AWS infrastructure ~$35-50/month)

---

## 📊 Performance

### Response Times (Target)

| Operation | P50 | P95 | Max |
|-----------|-----|-----|-----|
| STT (Groq Whisper) | 1.5s | 2.5s | 5s |
| LLM Response (Gemini) | 2.8s | 5.0s | 8s |
| TTS Generation | 0.8s | 1.5s | 3s |
| RAG Search | 0.15s | 0.3s | 0.5s |
| Web Search | 1.2s | 2.0s | 3s |
| **Total** | **5.2s** | **9.2s** | **15s** |

### Scalability
- **Current deployment** (EC2 t3.medium): 100+ concurrent users
- **Capacity**: ~14,000 conversations/day (limited by free API quotas)
- **Database**: DynamoDB (auto-scales), ChromaDB (~1GB per 10K conversations)

---

## 🎯 User Journey

### Week 1 (7 conversations)
- Profile maturity: **NEW**
- Discovered traits: 2-3
- AI behavior: Generic, asks many questions
- Pitfall detection: Not yet calibrated

### Month 1 (30 conversations)
- Profile maturity: **EMERGING**
- Discovered traits: 5-7 (weight: 0.6-0.7)
- AI behavior: Starts personalizing responses
- Pitfall detection: 60% accuracy

### Month 3 (70 conversations)
- Profile maturity: **HIGH**
- Discovered traits: 10-15 (weight: 0.7-0.9)
- AI behavior: Feels like it "knows" you
- Pitfall detection: 80% accuracy

### Month 6+ (120+ conversations)
- Profile maturity: **EXPERT**
- Discovered traits: 15-20 (weight: 0.8-0.95)
- AI behavior: **J.A.R.V.I.S.-level partnership**
- Pitfall detection: 90%+ accuracy

---

## 🧪 Technology Stack

### Backend
- **Framework**: FastAPI 0.109.2
- **Language**: Python 3.12
- **Database**: AWS DynamoDB (4 tables)
- **Vector DB**: ChromaDB 0.4.22
- **Validation**: Pydantic 2.6.1
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: Flutter 3.35.7
- **Language**: Dart 3.0+
- **State Management**: Riverpod 3.0
- **HTTP Client**: Dio 5.4.0
- **Audio**: record 6.1.2, just_audio 0.9.36
- **Camera**: camera 0.10.5+9

### Infrastructure
- **Hosting**: AWS EC2 (t3.medium, Seoul region)
- **Process Manager**: systemd
- **Monitoring**: journalctl, CloudWatch (optional)
- **Deployment**: Git pull + systemctl restart

---

## 📚 Documentation

- **[Installation Guide](INSTALL_GUIDE.md)**: Complete setup instructions
- **[Project Overview](PROJECT.md)**: Comprehensive technical analysis
- **[Master Specification](PROJECT_EDEN_V2_MASTER_SPEC.md)**: Detailed design document
- **[API Documentation](http://localhost:8000/docs)**: Interactive OpenAPI docs (when running)

---

## 🧬 Core Algorithms

### Neural Network-Inspired Learning

**Weight Update Formula:**
```python
# Time Decay (after 7 days)
if days_since_last_update > 7:
    decay_days = days_since_last_update - 7
    decay_amount = 0.02 × decay_days
    decayed_weight = max(0.3, current_weight - decay_amount)

# Learning (Positive Reinforcement)
delta = 0.1 × evidence_strength  # evidence_strength = 0.8
new_weight = min(1.0, decayed_weight + delta)
```

**Example:**
- Trait "perfectionist": weight 0.8
- Not observed for 17 days → Decay: 0.2 → Weight: 0.6
- New evidence found → Increase: 0.08 → **Final weight: 0.68**

### Pitfall Detection

```python
# Calculate alignment score
alignment_score = llm_analyze_alignment(user_message, one_thing)

# Trigger warning if weak alignment
if alignment_score < 0.3:
    # Check if matches Core Pitfall triggers
    if any(trigger in user_message for trigger in pitfall_triggers):
        generate_warning(pitfall_warning_phrases)
```

---

## 🌟 Innovation Highlights

1. **Backpropagation-Style Mentor Adaptation**
   - Unprecedented in chatbot systems
   - Uses feedback signals to adjust 5 learning preference weights

2. **Weighted Trait System with Time Decay**
   - Inspired by human memory
   - Traits fade if not reinforced, strengthen when observed

3. **Benevolent Dissent**
   - AI that says "no" when necessary
   - Challenges users when they stray from goals

4. **RAG + WebSearch Dual Context**
   - Combines semantic memory (past) + current information (web)
   - Most chatbots use either RAG OR web search, not both

5. **5D Learning Preference Space**
   - Enables unprecedented personalization of mentoring style

---

## 📈 Project Statistics

- **Total Code**: ~500,000 lines (including dependencies)
- **Core Application**: ~5,000 lines
- **Backend Services**: 10 services, ~3,500 lines
- **API Endpoints**: 25+ endpoints
- **Frontend Screens**: 8 screens
- **Database Tables**: 4 DynamoDB tables + ChromaDB
- **Test Coverage**: Unit tests (pytest)

---

## 🛣️ Roadmap

### Completed ✅
- [x] Am-muk-ji learning system (neural network-inspired)
- [x] Pitfall detection (benevolent dissent)
- [x] RAG (retrieval-augmented generation)
- [x] Dual personas (Adam & Eve)
- [x] Goal progress tracking
- [x] Analytics dashboard
- [x] Voice customization
- [x] Smart notifications

### Planned 🔜
- [ ] Multi-modal emotion recognition (voice tone + facial)
- [ ] Habit formation coaching
- [ ] Multi-language support (English, Japanese)
- [ ] Wearable integration (Apple Watch, Galaxy Watch)
- [ ] Collaborative goal-setting (group mentorship)

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Health Check**: http://3.39.177.218:8000/health
- **API Docs**: http://3.39.177.218:8000/docs
- **Issues**: [GitHub Issues](https://github.com/yourusername/Garden_of_Eden/issues)

---

<div align="center">

**Built with ❤️ for meaningful AI mentorship**

[Get Started](#-quick-start) • [Documentation](#-documentation) • [한국어](README_KR.md)

</div>
