# 🌟 Project Eden V2

**A J.A.R.V.I.S.-like AI Partner That Deeply Understands You**

Version: 2.1.0 | Status: **Production Ready** 🚀 | AWS EC2 Deployed ✅

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
- 🔍 **Remembers semantically** - RAG searches your entire conversation history
- 🌐 **Accesses current info** - WebSearch when WiFi available

**This is J.A.R.V.I.S., not Siri.**

---

## 🚀 Quick Start (Galaxy Device)

### 1. Install APK

**Download:**
- Transfer `app-debug.apk` to your Galaxy device
- Or connect via USB and run `flutter install`

**Install:**
1. Open the APK file
2. Allow "Install from unknown sources" (first time only)
3. Proceed with installation

### 2. Grant Permissions

App will request 2 permissions on first launch:
- 📹 **Camera** - For visual context sharing
- 🎤 **Microphone** - For voice conversations

### 3. Start Using!

1. **Press and hold** the big microphone button
2. Speak in Korean (e.g., "안녕하세요")
3. Release your finger
4. Listen to AI response!

**That's it!** 🎉

---

## 💡 Key Features

### 1. Master Directive System

Every AI response is filtered through:
- Your profile (One Thing, Core Pitfall, personality traits)
- Recent conversation memory (last 10 conversations)
- **Semantic memory (RAG)** - Top 5 similar conversations from entire history
- **Web context** - Current information from web search (when WiFi available)
- Current input (voice + camera + text)
- Pitfall detection with alignment check
- Emotional state detection

### 2. Benevolent Dissent

When you ask about something that triggers your **Core Pitfall**, AI intervenes:

**Example:**
```
User: "Should I learn SLAM algorithms?"
AI (Adam): "Wait a moment. SLAM is interesting, but
           isn't SNU HCI Lab your goal right now?
           This looks like your 'capability trap' pattern.
           Spreading energy might distance you from HCI preparation."
```

### 3. Dual Personas

**Adam (아담)**
- Male voice, logical, father-like mentor
- Uses Socratic questions to guide thinking
- Direct but caring

**Eve (이브)**
- Female voice, energetic, uplifting coach
- Celebrates and validates warmly
- Makes you feel good naturally

### 4. Profile Evolution

- **Week 1**: Basic profile, AI asks questions
- **Week 4**: Patterns emerge, 5-7 traits discovered
- **Week 12**: Mature profile, AI "knows" you deeply
- **Month 6+**: J.A.R.V.I.S.-level partnership

### 5. RAG (Retrieval-Augmented Generation)

AI searches your **entire conversation history** semantically:
- Uses ChromaDB for vector storage (local persistence)
- Sentence-transformers for embeddings (384-dim vectors)
- Retrieves top 5 similar conversations (cosine similarity)
- Provides context from weeks/months ago when relevant

**Example:** If you asked about React 2 months ago, AI remembers that context when you ask about state management today.

### 6. WebSearch Integration

When WiFi is available and query needs current info:
- **Primary**: Tavily API (high-quality results)
- **Fallback**: DuckDuckGo (always available)
- Smart trigger detection (keywords: "latest", "current", "2024", "news", etc.)
- Top 3 results integrated into AI response

**Example:** "What are the latest AI trends in 2024?" triggers web search automatically.

---

## 🧠 Core Algorithms Explained

### 1. Am-muk-ji (Implicit Knowledge) Learning System

**Concept:** Inspired by neural network weight updates. Continuously learns from conversations and updates personality trait weights using evidence accumulation and time decay mechanisms.

**Core Parameters:**
```python
LEARNING_RATE = 0.1          # Weight increase per reinforcement
DECAY_RATE = 0.02            # Weight decay per day
TIME_THRESHOLD_DAYS = 7      # Days before decay starts
MIN_TRAIT_WEIGHT = 0.3       # Minimum possible weight
MAX_TRAIT_WEIGHT = 1.0       # Maximum possible weight
```

**Weight Calculation Formula:**

```
Step 1: Apply time decay (if trait hasn't been reinforced recently)
  If days_since_last_update > 7:
    decay_days = days_since_last_update - 7
    decay_amount = 0.02 × decay_days
    decayed_weight = max(0.3, current_weight - decay_amount)
  Else:
    decayed_weight = current_weight

Step 2: Apply learning (positive reinforcement)
  delta = 0.1 × evidence_strength (fixed at 0.8)
  new_weight = min(1.0, decayed_weight + delta)
```

**Example:**
- Trait "perfectionist" hasn't appeared for 17 days
- Decay: 0.02 × (17-7) = 0.2 reduction
- Current weight 0.8 → decays to 0.6
- Perfectionist behavior observed in conversation
- Increase: 0.1 × 0.8 = 0.08
- New weight: 0.6 + 0.08 = 0.68

**Profile Maturity Calculation:**
```python
NEW:        < 10 conversations
EMERGING:   10-30 conversations
MEDIUM:     30-70 conversations
HIGH:       70-120 conversations
EXPERT:     120+ conversations
```

**Learning Pipeline (10 Steps):**
1. Load current profile
2. Extract messages (user + AI response)
3. LLM analysis for insights
4. Discover new traits (confidence > 0.6)
5. Reinforce existing traits (update weights)
6. Detect emotional states
7. Update question patterns
8. Check goal evolution
9. Apply time decay
10. Save and log

---

### 2. Pitfall Detection Algorithm

**Concept:** Detects when user's requests stray from their "One Thing" goal. Implements the Benevolent Dissent system.

**Core Thresholds:**
```python
ALIGNMENT_THRESHOLD = 0.3  # Below this = weak alignment
PITFALL_CONFIDENCE_THRESHOLD = 0.6
```

**Detection Pipeline (4 Steps):**

```
1. Extract topic from user message
   → LLM identifies topic keywords

2. Calculate alignment with "One Thing"
   → LLM semantic alignment analysis (0.0 ~ 1.0)

3. Check if alignment is weak
   → Is alignment_score < 0.3?

4. Check if it matches Core Pitfall pattern
   → Keyword matching confirmation
```

**Alignment Score Interpretation:**
```
1.0         = Perfect alignment (direct contribution to goal)
0.7 - 0.9   = Indirect support (related skill)
0.4 - 0.6   = Tangential relevance
0.1 - 0.3   = Weak connection
0.0         = No connection

< 0.3       = Trigger warning!
```

**Warning Message Generation:**
- **High** (Core Pitfall detected): "⚠️ CORE PITFALL DETECTED: '{topic}' matches your {pitfall_name}."
- **Low** (Weak alignment): "'{topic}' has weak alignment with your goal '{one_thing}'. Consider if this is necessary now."

---

### 3. RAG (Retrieval-Augmented Generation)

**Concept:** Semantic conversation search using vector database and sentence embeddings.

**Embedding Model:**
```python
Model: sentence-transformers/all-MiniLM-L6-v2
Dimensions: 384
Features: Lightweight, fast inference, optimized for semantic similarity
```

**Storage Process:**
```
1. Extract user message and AI response from conversation

2. Create combined text
   → "User: {user_message} Assistant: {ai_response}"

3. Generate embedding (384-dimensional vector)
   → sentence-transformers encoding

4. Prepare metadata
   → user_id, timestamp, topic, etc.

5. Store in ChromaDB
   → Local persistence (backend/chroma_db/)
```

**Search Mechanism:**
```
1. Generate query embedding
   → Convert user message to 384-dim vector

2. Search ChromaDB
   → Find top K by cosine similarity

3. Convert distance to similarity
   → similarity_score = 1.0 - L2_distance

4. Filter by minimum similarity
   → Keep only similarity_score >= 0.5

5. Return results
   → Sorted by similarity score (descending)
```

**Default Parameters:**
```python
k (top-K results) = 5           # Top 5 most similar conversations
min_similarity = 0.5            # Minimum 50% similarity required
metadata_text_limit = 500       # Truncate to 500 characters
recent_conversations = 10       # For context
```

**Similarity Score Formula:**
```
similarity_score = 1.0 - L2_distance

Range: 0.0 (no similarity) ~ 1.0 (identical)
Threshold: 0.5 (50% similarity minimum)
```

---

### 4. WebSearch Integration

**Concept:** Automatically performs web search when current/recent information is needed.

**Query Detection Algorithm:**

**Keyword Weights:**
```python
Current info keywords = ["latest", "current", "now", "today", "recent",
                         "최신", "현재", "지금", "오늘", "요즘", "최근",
                         "2024", "2025", "this year", "올해"]
  → +0.3 per match

Factual keywords = ["news", "price", "weather", "stock",
                    "뉴스", "소식", "가격", "날씨", "주가"]
  → +0.4 per match
```

**Trigger Conditions:**
```
Confidence calculation:
  confidence = Σ(current_info_keywords × 0.3) + Σ(factual_keywords × 0.4)
  confidence = min(confidence, 1.0)  # Cap at 1.0

Trigger:
  confidence >= 0.3 → Execute web search
```

**Examples:**
```
"latest AI trends" → Detects "latest" → confidence = 0.3 → TRIGGER!
"news today" → Detects "news" + "today" → confidence = 0.7 → TRIGGER!
"learn Python" → No keywords → confidence = 0.0 → NO TRIGGER
```

**Tavily vs DuckDuckGo Selection:**
```
Primary attempt: Tavily API (if API key available)
  → High-quality results, relevance scores provided
  → 1,000 free searches/month

Fallback: DuckDuckGo
  → Used if no API key or Tavily error
  → Always available, no scores
```

**Result Selection:**
```python
max_results = 3         # Top 3 results
search_depth = "basic"  # Search depth level
```

**Context Formatting:**
```
Web Search Results: "{query}"
(Source: Tavily/DuckDuckGo, {num_results} results)

1. {title}
   {content first 200 chars}...
   URL: {url}

2. {title}
   ...
```

---

### 5. Master Directive Processing Pipeline

**Concept:** Main orchestrator that coordinates all services to process conversations.

**Complete Pipeline (11 Steps):**

```
1. Load user profile
   → Fetch from DynamoDB/in-memory DB

2. Load recent conversations (for context)
   → Last 10 conversations

3. RAG semantic search
   → Top 5 similar conversations (min_similarity 0.5)

4. Web search (if WiFi available and query needs current info)
   → Check trigger conditions → Tavily/DuckDuckGo search

5. Check for pitfall (benevolent dissent)
   → Calculate alignment score → Generate warning

6. Detect emotional state
   → Keyword heuristics (tired, anxious, worried, etc.)

7. Generate AI response (with full context)
   → Gemini 2.5 Flash LLM

8. Generate TTS audio
   → Google TTS (Adam/Eve voice)

9. Save conversation
   → Persist to database

10. Embed conversation for RAG
    → Store vector in ChromaDB

11. Learn from conversation (async background)
    → Update trait weights
```

**Context Assembly Logic:**

**1. RAG Context:**
```python
if rag_results.retrieved_conversations:
    "Found {num_results} semantically similar past conversations:

    1. (Similarity: 0.87) 2024-10-15
       User: React state management...
       AI: The difference between useState and useReducer...

    2. (Similarity: 0.72) 2024-09-28
       ..."
```

**2. Web Context:**
```python
if wifi_available and should_search:
    "Web Search Results: \"{query}\"
    (Source: Tavily, 3 results)

    1. 2024 AI Trends: GPT-4 and Multimodal AI
       ...
       URL: https://..."
else:
    "Web search not needed: {reason}"
```

**3. Profile Context:**
```python
[Core Identity]: Pragmatic learner
[One Thing]: Get into SNU HCI Lab
[Core Pitfall]: Capability Trap (spreading too thin)
  Triggers: SLAM, robotics, quantum computing

[Top Personality Traits]:
  - perfectionist: 0.87
  - night_owl: 0.93
  - visual_learner: 0.76
  - stress_prone_when_uncertain: 0.69
```

**Emotional Detection Heuristics:**
```python
stress_keywords = [
    "tired", "anxious", "worried", "scared", "difficult",
    "힘들", "어려워", "불안", "걱정", "두려", "무서",
    "exhausted", "give up", "can't", "fail", "지쳤", "포기"
]

Emotional state mapping:
  "anxious", "worried", "불안" → anxious
  "tired", "exhausted", "힘들", "지쳤" → exhausted
  "give up", "fail", "포기", "실패" → frustrated
  Others → stressed
```

---

## 📊 Core Numeric Parameters Summary

| System | Parameter | Value | Description |
|--------|-----------|-------|-------------|
| **Am-muk-ji Learning** | Learning Rate | 0.1 | Weight increase per reinforcement |
| | Decay Rate | 0.02/day | Time-based weight decay |
| | Time Threshold | 7 days | Days before decay starts |
| | Min Weight | 0.3 | Minimum trait weight |
| | Max Weight | 1.0 | Maximum trait weight |
| | New Trait Confidence | 0.6 | Addition threshold |
| | Evidence Strength | 0.8 | Fixed value |
| | Recent Evidence | 5 items | Examples kept |
| **Pitfall Detection** | Alignment Threshold | 0.3 | Below = warning |
| | Pitfall Confidence | 0.6 | Detection threshold |
| **RAG** | Embedding Dimensions | 384 | Vector size |
| | Top-K Results | 5 | Search count |
| | Min Similarity | 0.5 | 50% threshold |
| | Metadata Limit | 500 chars | Text truncation |
| | Recent Conversations | 10 | Context window |
| **Web Search** | Trigger Confidence | 0.3 | Execute search |
| | Current Info Weight | +0.3 | Per keyword |
| | Factual Info Weight | +0.4 | Per keyword |
| | Max Results | 3 | Return count |
| | Content Preview | 200 chars | Display length |
| **Profile Maturity** | NEW | < 10 | Conversation count |
| | EMERGING | 10-30 | Conversation count |
| | MEDIUM | 30-70 | Conversation count |
| | HIGH | 70-120 | Conversation count |
| | EXPERT | 120+ | Conversation count |

---

## 🏗️ Technical Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: DynamoDB (NoSQL) + Local in-memory
- **Vector DB**: ChromaDB (for RAG semantic search)
- **LLM**: Google Gemini 2.5 Flash (FREE, vision support)
- **STT**: Groq Whisper Large v3 (FREE, 14,400 req/day)
- **TTS**: Google TTS (gTTS) - FREE unlimited, Korean voices
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **WebSearch**: Tavily API + DuckDuckGo fallback

### Frontend
- **Framework**: Flutter 3.35.7+
- **State Management**: Riverpod 3.0
- **Platform**: iOS & Android
- **Audio**: Record + Just Audio
- **Camera**: 1 FPS capture with keyframe selection
- **Caching**: SharedPreferences
- **Error Handling**: Global error boundary

### Infrastructure
- **Deployment**: AWS EC2 (Seoul ap-northeast-2)
- **Server IP**: 3.39.177.218:8000
- **Cost**: ~$15-45/month (AWS EC2 after free tier)

---

## 🛠️ Development Setup

### Backend

**Initial Setup:**
```bash
cd backend
./setup_local.sh    # Creates venv, installs dependencies
```

**Start Server:**
```bash
cd backend
./start_local.sh    # Activates venv and starts on port 8000
```

**API Documentation:**
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend

**Get Local IP (for development):**
```bash
ipconfig getifaddr en0  # macOS/Linux
```

**Install Dependencies:**
```bash
cd frontend
flutter pub get
```

**Run on Device:**
```bash
flutter run  # Ensure device connected via USB
```

**Build Release:**
```bash
cd frontend
flutter build apk --release
```

---

## 🔧 API Reference

### POST /api/v2/chat
Main chat endpoint with RAG and WebSearch support.

**Request:**
```bash
curl -X POST "http://3.39.177.218:8000/api/v2/chat" \
  -F "user_id=user_123" \
  -F "message=I want to get into SNU HCI Lab" \
  -F "voice_type=adam" \
  -F "wifi_available=true"
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "response_text": "SNU HCI Lab is your goal! That's excellent...",
  "response_audio_base64": "base64_mp3_data",
  "pitfall_warning_triggered": false,
  "emotional_support_mode": false,
  "profile_updated": true,
  "profile_version": 2,
  "processing_time_ms": 1847,
  "rag_context_used": true,
  "web_search_performed": false
}
```

### GET /api/v2/profile/{user_id}
Retrieve user profile with traits and maturity.

**Response:**
```json
{
  "user_id": "user_123",
  "one_thing": "Get into SNU HCI Lab",
  "core_pitfall": "Capability Trap",
  "personality_traits": [
    {"name": "perfectionist", "weight": 0.87},
    {"name": "night_owl", "weight": 0.93}
  ],
  "conversation_count": 45,
  "profile_maturity": "MEDIUM",
  "profile_version": 12
}
```

### POST /api/v2/stt
Transcribe audio to text (Speech-to-Text).

**Request:**
```bash
curl -X POST "http://3.39.177.218:8000/api/v2/stt" \
  -F "audio_file=@recording.wav" \
  -F "language=ko"
```

**Response:**
```json
{
  "text": "안녕하세요"
}
```

---

## 📱 App Usage Guide

### Main Screen (Voice-First)
- **Push-to-Talk**: Press and hold microphone button to record
- **Persona Toggle**: Switch between Adam and Eve
- **Camera View**: Full-screen camera with 1 FPS capture
- **Response Overlay**: Glassmorphism design with AI responses
- **Pitfall Warning**: Visual banner when straying from goals
- **Loading States**: Animated feedback during processing

### Profile Screen
- View your "One Thing" and "Core Pitfall"
- See personality traits with weights
- View conversation stats and maturity level
- Track profile evolution over time

### Settings Screen
- Adjust TTS volume
- Enable/disable camera
- Select default persona (Adam/Eve)
- Clear cache
- View app version

---

## 🔧 Troubleshooting

### Backend Connection Failure
**Symptom**: "Cannot connect to server"

**Solution:**
1. Verify backend is running: `curl http://3.39.177.218:8000/health`
2. Check WiFi/data connection
3. Ensure firewall allows port 8000

### Voice Recognition Fails
**Symptom**: Speech not converted to text

**Solution:**
1. Check microphone permission (Settings > Apps > Project Eden > Permissions)
2. Speak clearly in quiet environment
3. Use Korean language (default)

### Camera Not Working
**Symptom**: Black screen or camera error

**Solution:**
1. Check camera permission
2. Ensure no other app is using camera
3. Restart app

### APK Installation Failed
**Symptom**: "App cannot be installed"

**Solution:**
1. Allow "Install from unknown sources" (Settings > Security)
2. Uninstall previous version and reinstall
3. Ensure sufficient storage (minimum 100MB)

---

## 📖 Additional Documentation

- **[README_KR.md](README_KR.md)** - Korean user documentation
- **[AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)** - AWS EC2 deployment guide
- **[PROJECT_EDEN_V2_MASTER_SPEC.md](PROJECT_EDEN_V2_MASTER_SPEC.md)** - Complete technical specification
- **[CLAUDE.md](CLAUDE.md)** - AI development assistant guide

---

## 💭 Key Concepts

**One Thing:** The user's single most important goal. AI keeps user focused on this.

**Core Pitfall:** User's primary distraction pattern (e.g., "Capability Trap" - spreading too thin).

**Benevolent Dissent:** AI warns when user asks about things that conflict with their One Thing.

**Am-muk-ji (암묵지):** Korean term for implicit knowledge. System learns user traits through observation, not explicit declaration.

**Trait Weights:** Personality traits (0.0-1.0 scale) that increase with reinforcement and decay without it.

**Profile Maturity:** Calculated from conversation count and trait confidence (NEW → EMERGING → MEDIUM → HIGH → EXPERT).

---

## 🎯 Vision

_"Project Eden is not a chatbot. It is a deeply personalized AI partner that understands you, learns from every interaction, and helps you achieve your One Thing while protecting you from distractions."_

**All 7 development phases complete. Ready for production deployment.** 🚀

---

**Built with**: FastAPI • Flutter • Gemini • Riverpod • DynamoDB • ChromaDB • Groq Whisper • Tavily
