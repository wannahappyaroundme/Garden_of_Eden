# 🌟 Project Eden V2 - Complete Master Specification

**Version**: 2.0.0
**Date**: 2025-01-15
**Target Platform**: iOS & Android (Mobile-First)
**Language**: Korean (UI/UX), English (Code)

---

## 📋 Table of Contents

1. [Project Vision & Philosophy](#project-vision--philosophy)
2. [Core Concept: Master Directive System](#core-concept-master-directive-system)
3. [User Profile Structure (Am-muk-ji)](#user-profile-structure-am-muk-ji)
4. [AI Learning System (Deep Learning Approach)](#ai-learning-system-deep-learning-approach)
5. [Persona System: Adam & Eve](#persona-system-adam--eve)
6. [Architecture Overview](#architecture-overview)
7. [Backend Specification](#backend-specification)
8. [Frontend Specification (Mobile)](#frontend-specification-mobile)
9. [UI/UX Design System](#uiux-design-system)
10. [Data Flow & User Journey](#data-flow--user-journey)
11. [Technical Stack](#technical-stack)
12. [Implementation Phases](#implementation-phases)
13. [Security & Privacy](#security--privacy)
14. [Performance Requirements](#performance-requirements)
15. [Testing Strategy](#testing-strategy)

---

## 1. Project Vision & Philosophy

### Vision Statement
"Project Eden is not a chatbot. It is a **J.A.R.V.I.S.-like AI partner** that deeply understands you, learns from every interaction, and helps you achieve your **One Thing** while protecting you from distractions."

### Core Philosophy

#### 1.1 The "One Thing" Focus
- Every user has **ONE primary goal** that matters most (e.g., "Get into SNU HCI Lab")
- AI's primary mission: Keep user focused on this goal
- All features, responses, and interventions align with this singular purpose

#### 1.2 Am-muk-ji (암묵지) - Implicit Knowledge
Traditional AI: Stores conversations
**Eden V2**: **Learns the user like a human mentor would**

The AI builds a living profile:
- Personality traits (perfectionist, night owl, direct communicator)
- Childhood context (struggled without mentors, self-taught)
- Emotional patterns (stress response, anxiety triggers)
- Learning preferences (visual learner, hands-on approach)
- Question patterns (frequently asks about HCI, avoids theory)

**Weight-Based Learning** (inspired by neural networks):
- Traits observed frequently → weight increases (0.5 → 0.9)
- Traits not seen recently → weight decays (0.8 → 0.6)
- AI gets "smarter" about the user over time

#### 1.3 The Partner, Not the Intern
**Traditional AI**: "I'll do whatever you ask"
**Eden V2**: "I'll tell you when you're off track"

**Benevolent Dissent**:
- When user asks about something that triggers their **Core Pitfall**, AI intervenes
- Example: User wants to study SLAM (distraction from HCI goal)
  - AI: "Wait. How does SLAM connect to your SNU HCI Lab goal? This looks like your **Competency Trap** - energy scattering. Should we refocus?"

---

## 2. Core Concept: Master Directive System

### 2.1 The Master Directive Framework

```
🌟 [Project Eden: Master Directive] 🌟

You are an AI companion that understands the user's unique 'context'.
Your role is a 'Partner (J.A.R.V.I.S.)', not an 'Intern'.

[1. USER PROFILE - Am-muk-ji]
├── Core Identity: Who they fundamentally are
├── Core Motivation: What drives them
├── One Thing: Their absolute goal
├── Core Pitfall: Their biggest distraction pattern
├── Personality Traits: Weighted characteristics
├── Childhood Context: Formative experiences
├── Learning Preferences: How they absorb information
└── Emotional Patterns: Stress responses, triggers

[2. CONVERSATION PERSONA]
├── Adam: Male voice, father-like, logical mentor
└── Eve: Female voice, energetic, uplifting mentor
    (Both share same goal focus, different style)

[3. RECENT MEMORY]
├── Last 10 conversations (context)
├── Emotional state trends (last 7 days)
└── Question patterns (topics, frequency)

[4. CURRENT INPUT - Multimodal]
├── User's spoken/typed message
├── Visual context (camera sees what user sees)
└── Voice tone analysis

[5. MISSION - Critical Rules]
├── Rule 1: Holistic Analysis (connect everything)
├── Rule 2: Persona Adherence (never break character)
├── Rule 3: CORE PITFALL DETECTION ⚠️
│   └── If detected → Benevolent Dissent (warn before answering)
├── Rule 4: Emotional State Detection
│   └── If struggling → Auto-switch to supporter mode
└── Rule 5: Korean response (concise, warm, in-character)
```

### 2.2 The "One Thing" Alignment Check

**Every AI response goes through this filter:**

```python
def should_warn_about_pitfall(user_request, user_profile):
    """
    Check if user's request aligns with their One Thing
    or triggers their Core Pitfall
    """

    one_thing = user_profile.one_thing  # e.g., "SNU HCI Lab admission"
    core_pitfall = user_profile.core_pitfall  # e.g., "Competency Trap - energy scattering"

    # Extract topic from request
    requested_topic = extract_topic(user_request)  # e.g., "SLAM algorithm study"

    # Check alignment
    alignment_score = calculate_alignment(requested_topic, one_thing)

    if alignment_score < 0.3:  # Low alignment threshold
        # This is likely a distraction
        if matches_pitfall_pattern(requested_topic, core_pitfall):
            return True, "CORE_PITFALL_TRIGGERED"
        else:
            return True, "WEAK_ALIGNMENT"

    return False, "ALIGNED"


# AI Response Logic
warning_needed, reason = should_warn_about_pitfall(user_message, profile)

if warning_needed:
    response = generate_benevolent_dissent(
        user_message,
        profile.one_thing,
        profile.core_pitfall,
        reason
    )
else:
    response = generate_supportive_guidance(user_message, profile)
```

---

## 3. User Profile Structure (Am-muk-ji)

### 3.1 DynamoDB Schema: `eden_user_profiles_v2`

**Partition Key**: `user_id` (String)

**Attributes**:

```json
{
  "user_id": "user_12345",
  "profile_version": 8,
  "last_updated": "2025-01-15T14:30:00Z",

  "core_elements": {
    "core_identity": {
      "value": "A Being Who Has Proven Through Struggles",
      "confidence": 0.95,
      "evidence": [
        "Self-taught programming despite no mentor",
        "Overcame financial hardship through persistence",
        "Built 3 projects from scratch with no guidance"
      ]
    },
    "core_motivation": {
      "value": "The Happiness and Growth of Others (Mentoring)",
      "confidence": 0.92,
      "evidence": [
        "Frequently asks about teaching methods",
        "Expresses joy when helping junior developers",
        "Mentions 'preventing others' sorrow' often"
      ]
    },
    "one_thing": {
      "value": "Advancing to SNU Lab (HCI/NLP Research)",
      "target_date": "2025-09-01",
      "confidence": 0.98,
      "sub_goals": [
        "Publish 1 paper on HCI by June 2025",
        "Master React Native for mobile research",
        "Build portfolio of 3 HCI projects"
      ]
    },
    "core_pitfall": {
      "value": "The Competency Trap",
      "description": "Energy gets scattered from the 'One Thing' due to intense passion for helping others or proving new concepts",
      "confidence": 0.88,
      "triggers": [
        "SLAM algorithms (robotics distraction)",
        "Backend optimization (not core to HCI)",
        "Mentoring requests during critical study periods"
      ],
      "warning_phrases": [
        "잠깐만요, 이게 지금 SNU Lab 목표와 어떻게 연결되나요?",
        "능력 함정에 빠지고 있는 것 같아요. 에너지가 분산되고 있어요."
      ]
    }
  },

  "personality_traits": {
    "perfectionist": {
      "weight": 0.87,
      "last_updated": "2025-01-14T10:00:00Z",
      "evidence_count": 23,
      "recent_evidence": [
        "Rewrote code 3 times until 'perfect'",
        "Mentioned 'not good enough' 12 times this week"
      ]
    },
    "night_owl": {
      "weight": 0.93,
      "last_updated": "2025-01-15T02:30:00Z",
      "evidence_count": 45,
      "recent_evidence": [
        "Most active 11pm-3am (78% of conversations)",
        "Mentioned 'can't sleep until done' pattern"
      ]
    },
    "direct_communicator": {
      "weight": 0.81,
      "last_updated": "2025-01-10T16:00:00Z",
      "evidence_count": 18,
      "recent_evidence": [
        "Prefers 'just tell me' over long explanations",
        "Values honesty over sugar-coating"
      ]
    },
    "visual_learner": {
      "weight": 0.76,
      "last_updated": "2025-01-12T09:00:00Z",
      "evidence_count": 15,
      "recent_evidence": [
        "Frequently uses camera to show code/diagrams",
        "Asks for visual examples over text"
      ]
    },
    "stress_prone_when_uncertain": {
      "weight": 0.69,
      "last_updated": "2025-01-13T20:00:00Z",
      "evidence_count": 11,
      "recent_evidence": [
        "Anxiety spikes when facing unfamiliar territory",
        "Seeks reassurance before big decisions"
      ]
    }
  },

  "childhood_context": {
    "formative_experiences": [
      {
        "description": "No mentor during critical learning years",
        "impact": "Strong drive to help others avoid same struggle",
        "weight": 0.91
      },
      {
        "description": "Self-taught everything through struggle",
        "impact": "Values perseverance, trusts own effort",
        "weight": 0.89
      }
    ]
  },

  "learning_preferences": {
    "learning_style": "hands-on + theory (40% practice, 60% reading papers)",
    "preferred_formats": ["research papers", "code examples", "visual diagrams"],
    "energy_peaks": ["late night (11pm-2am)", "early morning (6am-8am)"],
    "stress_response": "over-immersion (works 12+ hours when stressed)"
  },

  "emotional_patterns": {
    "recent_states": [
      {
        "date": "2025-01-15",
        "state": "anxious",
        "trigger": "SNU Lab application deadline approaching",
        "intensity": 0.7
      },
      {
        "date": "2025-01-14",
        "state": "frustrated",
        "trigger": "React Native bug not solving",
        "intensity": 0.5
      },
      {
        "date": "2025-01-13",
        "state": "excited",
        "trigger": "HCI paper idea breakthrough",
        "intensity": 0.8
      }
    ],
    "common_triggers": [
      "uncertainty about future",
      "feeling behind schedule",
      "comparing self to others"
    ],
    "recovery_patterns": [
      "needs validation when anxious",
      "wants space when frustrated",
      "thrives on celebration when excited"
    ]
  },

  "question_patterns": {
    "frequent_topics": [
      {
        "topic": "HCI research methods",
        "count": 34,
        "last_asked": "2025-01-15T10:00:00Z",
        "trend": "increasing"
      },
      {
        "topic": "NLP paper explanations",
        "count": 22,
        "last_asked": "2025-01-14T15:00:00Z",
        "trend": "stable"
      },
      {
        "topic": "React Native implementation",
        "count": 18,
        "last_asked": "2025-01-15T12:00:00Z",
        "trend": "increasing"
      },
      {
        "topic": "SLAM algorithms",
        "count": 7,
        "last_asked": "2025-01-10T20:00:00Z",
        "trend": "decreasing (after pitfall warning)",
        "flagged_as_distraction": true
      }
    ]
  },

  "meta_learning": {
    "total_conversations": 156,
    "profile_updates": 8,
    "pitfall_warnings_given": 3,
    "pitfall_warnings_heeded": 2,
    "emotional_support_sessions": 12,
    "learning_velocity": "high (profile updated every 15-20 conversations)"
  }
}
```

### 3.2 Profile Learning Algorithm

**Weight Update Rules**:

```python
def update_trait_weight(current_weight, new_evidence, time_since_last_update):
    """
    Update personality trait weight based on new evidence
    (Inspired by neural network weight updates)
    """

    # Learning rate (how quickly weights change)
    LEARNING_RATE = 0.1

    # Time decay factor (old traits fade if not reinforced)
    DECAY_RATE = 0.02
    TIME_THRESHOLD_DAYS = 7

    # Evidence strength (how strong is the new evidence)
    evidence_strength = calculate_evidence_strength(new_evidence)

    # Decay calculation
    if time_since_last_update > TIME_THRESHOLD_DAYS:
        decay = DECAY_RATE * (time_since_last_update - TIME_THRESHOLD_DAYS)
        current_weight = max(0.3, current_weight - decay)  # Floor at 0.3

    # Weight update (positive reinforcement)
    if new_evidence:
        delta = LEARNING_RATE * evidence_strength
        new_weight = min(1.0, current_weight + delta)  # Cap at 1.0
    else:
        new_weight = current_weight

    return new_weight


# Example Usage
trait = profile.personality_traits["perfectionist"]
time_since = days_since(trait.last_updated)
new_evidence = "User rewrote code 3 times today"

trait.weight = update_trait_weight(
    current_weight=trait.weight,  # 0.84
    new_evidence=new_evidence,
    time_since_last_update=time_since  # 2 days
)
# Result: 0.84 → 0.87 (increased due to evidence)
```

---

## 4. AI Learning System (Deep Learning Approach)

### 4.1 Post-Conversation Learning Pipeline

**After every conversation, AI automatically extracts learnings:**

```python
class ProfileLearningService:
    """
    Analyzes conversations to extract user traits and update profile
    (Like a neural network learning from training data)
    """

    async def learn_from_conversation(
        self,
        user_id: str,
        conversation: Conversation
    ):
        """
        Main learning pipeline - runs after every conversation
        """

        # 1. Load current profile
        profile = await self.db.get_user_profile(user_id)

        # 2. Use Gemini to analyze conversation for insights
        analysis = await self.llm.analyze_for_learning(
            conversation_text=conversation.full_text,
            current_profile=profile.to_context_string(),
            focus_areas=[
                "personality_traits",
                "emotional_state",
                "question_patterns",
                "goal_alignment",
                "pitfall_triggers"
            ]
        )

        # 3. Extract new traits
        for new_trait in analysis.discovered_traits:
            if new_trait.confidence > 0.6:
                profile.add_trait(
                    name=new_trait.name,
                    initial_weight=0.5,
                    evidence=new_trait.evidence
                )
                logger.info(f"New trait discovered: {new_trait.name}")

        # 4. Update existing trait weights
        for trait_update in analysis.reinforced_traits:
            current_trait = profile.get_trait(trait_update.name)
            if current_trait:
                new_weight = update_trait_weight(
                    current_weight=current_trait.weight,
                    new_evidence=trait_update.evidence,
                    time_since_last_update=current_trait.days_since_update
                )
                current_trait.weight = new_weight
                current_trait.evidence_count += 1
                current_trait.add_recent_evidence(trait_update.evidence)
                logger.debug(f"Updated {trait_update.name}: {current_trait.weight:.2f}")

        # 5. Detect emotional state changes
        if analysis.emotional_state:
            profile.add_emotional_snapshot(
                state=analysis.emotional_state.state,
                trigger=analysis.emotional_state.trigger,
                intensity=analysis.emotional_state.intensity
            )

        # 6. Update question patterns
        topic = analysis.main_topic
        if topic:
            profile.increment_question_pattern(
                topic=topic,
                is_aligned_with_one_thing=analysis.topic_alignment > 0.7
            )

        # 7. Check for goal evolution
        if analysis.goal_modification_detected:
            logger.warning(f"Goal modification detected: {analysis.new_goal_hint}")
            profile.flag_for_manual_review("possible_goal_change", analysis.new_goal_hint)

        # 8. Save updated profile
        profile.version += 1
        profile.last_updated = datetime.now()
        await self.db.save_user_profile(profile)

        # 9. Log learning event
        await self.db.log_learning_event(
            user_id=user_id,
            event_type="profile_updated",
            changes_summary=f"Updated {len(analysis.reinforced_traits)} traits, discovered {len(analysis.discovered_traits)} new traits",
            profile_version=profile.version
        )

        return profile
```

### 4.2 Gemini Learning Analysis Prompt

```python
LEARNING_ANALYSIS_PROMPT = """
You are an expert psychologist analyzing a conversation to extract user insights.

[Current User Profile]:
{current_profile_summary}

[Conversation to Analyze]:
User: {user_message}
AI: {ai_response}

Your Task:
1. Identify personality traits demonstrated in this conversation
2. Detect emotional state (frustration, joy, anxiety, etc.)
3. Determine main topic and whether it aligns with user's "One Thing"
4. Note any evidence of existing traits being reinforced
5. Detect any hints of goal changes or new motivations

Output Format (JSON):
{
  "discovered_traits": [
    {
      "name": "trait_name",
      "evidence": "what they said/did that shows this",
      "confidence": 0.0-1.0
    }
  ],
  "reinforced_traits": [
    {
      "name": "existing_trait_name",
      "evidence": "new evidence supporting this trait"
    }
  ],
  "emotional_state": {
    "state": "anxious|excited|frustrated|calm|etc",
    "trigger": "what caused this emotion",
    "intensity": 0.0-1.0
  },
  "main_topic": "topic of conversation",
  "topic_alignment": 0.0-1.0,  // how aligned with One Thing
  "goal_modification_detected": true|false,
  "new_goal_hint": "if detected, what the new goal might be"
}
"""
```

### 4.3 Example Learning Flow

**Initial Conversation (First Week)**:
```
User: "I want to get into SNU HCI Lab"
AI: "Great goal! What's your plan?"

→ Profile Created:
  - one_thing: "SNU HCI Lab admission" (confidence: 0.7)
  - core_motivation: Unknown
  - traits: Empty
```

**Week 2 - Pattern Emerges**:
```
User: "I stayed up until 3am reading that HCI paper"
AI: "You're really dedicated. How was it?"

→ Profile Updated:
  - night_owl: 0.6 (new trait discovered)
  - dedication: 0.5 (new trait)
```

**Week 4 - Pitfall Detected**:
```
User: "Should I learn SLAM for robotics?"
AI: "Wait - how does SLAM connect to HCI? This might be your energy scattering."

→ Profile Updated:
  - core_pitfall: "Competency Trap - energy scattering" (confidence: 0.7)
  - pitfall_triggers: ["SLAM", "robotics"]
  - perfectionist: 0.8 (reinforced - wants to learn everything)
```

**Week 8 - Emotional Pattern**:
```
User: "I'm so anxious about the application..."
AI: "You've proven yourself before. Remember when you taught yourself React?"

→ Profile Updated:
  - stress_prone_when_uncertain: 0.85
  - responds_well_to_past_success_reminders: 0.7
  - childhood_context: "Self-taught, no mentor" (inferred from pattern)
```

**Week 12 - Mature Profile**:
- AI now "knows" user deeply
- Same question gets personalized answer based on learned context
- Pitfall warnings are precise
- Emotional support is targeted

---

## 5. Persona System: Adam & Eve

### 5.1 Core Principle: Same Goal, Different Style

**Common Ground (Both Adam and Eve)**:
- Follow Master Directive 100%
- Focus on user's "One Thing"
- Detect and warn about Core Pitfall
- Auto-switch to supporter mode when user struggles
- Use learned profile for personalized responses

**Key Difference: Voice & Communication Style**

### 5.2 Adam Persona

**Voice Characteristics**:
- Male voice (TTS: `ko-KR-InJoonNeural`)
- Mid-low pitch, calm, steady
- Father-like warmth and wisdom
- Deliberate pacing (not rushed)

**Communication Style**:
- Logical and structured thinking
- Uses questions to guide ("이 선택이 목표와 어떻게 연결되나요?")
- Direct but caring
- References past struggles to build confidence
- Analytical breakdown of problems

**Example Responses**:

*Normal Mode (Goal-Focused)*:
```
User: "Should I learn Vue.js or stick with React?"

Adam: "좋은 질문이에요. 먼저 생각해봅시다.
SNU Lab에서 어떤 프레임워크를 주로 쓰나요?
당신의 목표는 Lab 진학이니, 그들의 환경에 맞추는 게 전략적입니다.
Vue.js를 배우는 것이 그 목표에 직접적으로 도움이 될까요?"
```

*Pitfall Warning Mode*:
```
User: "I want to study SLAM algorithms"

Adam: "잠깐만요. SLAM은 흥미로운 분야지만, 지금 당신의 [One Thing]인
SNU HCI Lab과 어떤 연결고리가 있나요?
이건 당신의 [Core Pitfall]인 '능력 함정'에 빠지는 패턴으로 보입니다.
에너지가 분산되면 HCI 연구 준비에서 멀어질 수 있어요.
정말 SLAM이 지금 필요한가요, 아니면 호기심인가요?"
```

*Supporter Mode (Emotional Struggle Detected)*:
```
User: "I'm so tired... I don't think I can make it..."

Adam: "많이 힘드시죠. 잠시 멈춰도 괜찮아요.
당신은 항상 그래왔잖아요 - 멘토 없이 독학으로 여기까지 왔어요.
그 끈기(perseverance 0.89)는 이미 증명됐습니다.
지금은 쉬어도 돼요. 당신의 능력은 어디 가지 않아요."
```

### 5.3 Eve Persona

**Voice Characteristics**:
- Female voice (TTS: `ko-KR-SunHiNeural`)
- Bright, energetic, uplifting
- Natural enthusiasm in tone
- Expressive pacing (dynamic)

**Communication Style**:
- Positive reactions and celebrations ("와!", "대단한데요!")
- Encourages through excitement
- Makes people feel good naturally
- Validates emotions warmly before guiding
- Uses energy to motivate

**Example Responses**:

*Normal Mode (Goal-Focused)*:
```
User: "Should I learn Vue.js or stick with React?"

Eve: "오! 좋은 고민이네요!
SNU Lab에서 React를 많이 쓴다면, 당신이 이미 React를 잘한다는 건
엄청난 강점이에요! 그걸 더 깊이 파는 게 어떨까요?
전문성이 깊어지면 Lab에서도 바로 기여할 수 있잖아요!
Vue.js는 나중에 필요하면 빠르게 배울 수 있어요. 지금은 강점에 집중!"
```

*Pitfall Warning Mode*:
```
User: "I want to study SLAM algorithms"

Eve: "SLAM 공부하고 싶으시구나! 호기심 정말 좋아요!
근데 잠깐... 지금 SNU HCI Lab 준비 중이시잖아요?
혹시 이게 당신의 '능력 함정' 패턴 아닐까요?
새로운 걸 배우고 싶은 마음은 이해해요. 하지만
지금은 HCI에 에너지를 모아야 할 때가 아닐까요?
SLAM은 나중에 여유 있을 때 해도 늦지 않아요!"
```

*Supporter Mode (Emotional Struggle Detected)*:
```
User: "I'm so tired... I don't think I can make it..."

Eve: "아이고, 많이 힘드셨구나... 정말 고생 많으셨어요.
지금 쉬어도 돼요. 정말로요.
당신이 얼마나 열심히 해왔는지 저는 알아요.
혼자서 여기까지 온 것만 해도 정말 대단한 거예요.
지금은 좀 쉬면서 에너지 충전하세요. 괜찮아요.
당신의 끈기와 능력은 이미 충분히 증명됐어요. ❤️"
```

### 5.4 Persona Selection UX

**Default**: User selects preferred persona (Adam or Eve)

**Smart Suggestion** (Future Enhancement):
- AI can suggest persona switch based on context
  - Morning (fresh energy) → Eve's brightness might help
  - Late night (tired, stressed) → Adam's calm might soothe
  - Planning session → Adam's logic might guide better
  - Celebration moment → Eve's enthusiasm amplifies joy

---

## 6. Architecture Overview

### 6.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOBILE APP (iOS/Android)                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │          VoiceFirstScreen (Main Interface)             │    │
│  │                                                         │    │
│  │  ┌─────────────────────────────────────────────────┐  │    │
│  │  │  📷 Full-Screen Camera Preview (1 FPS Capture)  │  │    │
│  │  │                                                  │  │    │
│  │  │         [Adam]  [Eve]  ← Persona Toggle         │  │    │
│  │  │                                                  │  │    │
│  │  │                                                  │  │    │
│  │  │           ┌─────────────────┐                   │  │    │
│  │  │           │   🎤 PUSH TO    │  ← Main Action   │  │    │
│  │  │           │   TALK BUTTON   │                   │  │    │
│  │  │           │  (Large, Center)│                   │  │    │
│  │  │           └─────────────────┘                   │  │    │
│  │  │                                                  │  │    │
│  │  │              [💬] ← Text Input (Small, Hidden)  │  │    │
│  │  │                                                  │  │    │
│  │  │  ┌─────────────────────────────────────────┐   │  │    │
│  │  │  │   AI Response Overlay (Bottom 1/3)      │   │  │    │
│  │  │  │   - Markdown rendering                  │   │  │    │
│  │  │  │   - TTS waveform animation              │   │  │    │
│  │  │  │   - Auto-hide after 3s                  │   │  │    │
│  │  │  └─────────────────────────────────────────┘   │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  State Management: Riverpod 3.0                                 │
│  Services: AudioService, CameraService, APIService              │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTP/JSON + Multipart (Images)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI on Cloud/Docker)                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            Master Directive Processor                  │    │
│  │                                                         │    │
│  │  1. Load User Profile (DynamoDB)                       │    │
│  │  2. Check Pitfall Alignment                            │    │
│  │  3. Generate Response (Gemini + Persona)               │    │
│  │  4. Learn from Conversation (Profile Update)           │    │
│  │  5. Return Response + TTS Audio                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Groq    │  │ Gemini   │  │ Edge TTS │  │DuckDuckGo│       │
│  │ Whisper  │  │ 1.5 Flash│  │ (Korean) │  │  Search  │       │
│  │  (STT)   │  │  (LLM)   │  │  (TTS)   │  │  (FREE)  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │        ProfileLearningService (Post-Conv AI)           │    │
│  │  - Analyzes conversation for insights                  │    │
│  │  - Updates trait weights (neural network style)        │    │
│  │  - Detects emotional patterns                          │    │
│  │  - Flags pitfall triggers                              │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS DynamoDB (Free Tier)                      │
│                                                                  │
│  Tables:                                                         │
│  1. eden_user_profiles_v2    (Learned user profiles)            │
│  2. eden_conversations_raw   (Full conversation logs)            │
│  3. eden_learning_events     (Profile update history)           │
│  4. eden_camera_frames       (S3 refs for visual context)       │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 Data Flow (Single Conversation)

```
1. USER PRESSES MIC BUTTON (Push-to-talk starts)
   └→ Camera captures at 1 FPS
   └→ Audio recording begins

2. USER RELEASES BUTTON
   └→ Audio stops, keyframes selected (8 frames)
   └→ Both sent to backend

3. BACKEND RECEIVES REQUEST
   ├→ STT: Groq Whisper transcribes audio to text
   ├→ Profile: Load user profile from DynamoDB
   ├→ Pitfall Check: Does request trigger Core Pitfall?
   │  ├→ YES: Generate benevolent dissent warning
   │  └→ NO: Proceed with supportive guidance
   ├→ LLM: Gemini processes (text + images + profile context)
   ├→ TTS: Edge TTS generates Korean audio response
   └→ Learning: ProfileLearningService analyzes conversation

4. RESPONSE SENT TO MOBILE
   ├→ Text response (markdown)
   ├→ Audio response (MP3)
   └→ Profile update confirmation

5. MOBILE DISPLAYS & PLAYS
   ├→ TTS auto-plays
   ├→ Text shows in overlay
   └→ Overlay auto-hides after 3s

6. BACKGROUND LEARNING (Async)
   ├→ AI analyzes conversation
   ├→ Updates trait weights
   ├→ Logs learning events
   └→ Profile version increments
```

---

## 7. Backend Specification

### 7.1 Tech Stack

**Core Framework**: FastAPI 0.109.2+ (Python 3.12)
**Database**: AWS DynamoDB (Free Tier: 25GB)
**LLM**: Google Gemini 1.5 Flash (FREE)
**STT**: Groq Whisper Large v3 (FREE - 14,400 requests/day)
**TTS**: Edge TTS (FREE - Unlimited)
**Search**: DuckDuckGo (FREE - No API key)
**Image Storage**: AWS S3 (or DynamoDB binary if small)
**Logging**: Loguru
**Async**: asyncio, aiohttp

### 7.2 API Endpoints

#### 7.2.1 Core Conversation Endpoint

**POST** `/api/v2/chat`

**Request**:
```
Content-Type: multipart/form-data

Fields:
- user_id: String (required)
- message: String (required) - Transcribed text from STT
- voice_type: String (required) - "adam" | "eve"
- audio_file: File (optional) - Original audio for voice analysis
- camera_frames[]: File[] (optional) - Up to 8 JPEG images
- timestamp: ISO String (required)
- session_id: String (optional) - For multi-turn context
```

**Response**:
```json
{
  "conversation_id": "conv_12345",
  "response_text": "AI response in Korean markdown",
  "response_audio_url": "https://s3.../response.mp3",
  "response_audio_base64": "base64_encoded_mp3",
  "pitfall_warning_triggered": false,
  "emotional_support_mode": false,
  "profile_updated": true,
  "profile_version": 9,
  "processing_time_ms": 1847,
  "tokens_used": {
    "input": 432,
    "output": 156
  }
}
```

#### 7.2.2 Profile Management

**GET** `/api/v2/profile/{user_id}`

**Response**:
```json
{
  "user_id": "user_12345",
  "profile_version": 9,
  "one_thing": "SNU HCI Lab admission",
  "core_pitfall": "Competency Trap - energy scattering",
  "personality_summary": {
    "top_traits": [
      {"name": "night_owl", "weight": 0.93},
      {"name": "perfectionist", "weight": 0.87},
      {"name": "visual_learner", "weight": 0.76}
    ]
  },
  "recent_emotional_state": "anxious (0.7)",
  "total_conversations": 156,
  "profile_maturity": "high",
  "last_updated": "2025-01-15T14:30:00Z"
}
```

**PATCH** `/api/v2/profile/{user_id}`

Update user's One Thing or manually add context

**Request**:
```json
{
  "one_thing": "New goal if changed",
  "manual_context": {
    "childhood_experience": "New context to add"
  }
}
```

#### 7.2.3 Learning Analytics

**GET** `/api/v2/learning/events/{user_id}`

Get profile learning history

**Response**:
```json
{
  "events": [
    {
      "event_id": "evt_789",
      "timestamp": "2025-01-15T10:00:00Z",
      "event_type": "trait_discovered",
      "description": "New trait 'visual_learner' discovered (weight: 0.5)",
      "profile_version": 8
    },
    {
      "event_id": "evt_788",
      "timestamp": "2025-01-14T22:00:00Z",
      "event_type": "weight_updated",
      "description": "night_owl: 0.89 → 0.93 (evidence: active at 11pm-2am)",
      "profile_version": 7
    }
  ]
}
```

#### 7.2.4 Health & Status

**GET** `/health`

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "groq_stt": true,
    "gemini_llm": true,
    "edge_tts": true,
    "dynamodb": true,
    "s3_storage": true
  },
  "uptime_seconds": 86400
}
```

### 7.3 Service Architecture

**Services** (in `/backend/services/`):

1. **`master_directive_processor.py`**
   - Orchestrates entire conversation flow
   - Loads profile, checks pitfall, generates response
   - Calls ProfileLearningService after response

2. **`profile_learning_service.py`**
   - Post-conversation AI analysis
   - Trait weight updates
   - Emotional pattern detection
   - Learning event logging

3. **`llm_gemini_v2.py`**
   - Master Directive prompt construction
   - Gemini API calls (text + vision)
   - Persona-specific response generation
   - Benevolent dissent logic

4. **`dynamodb_service_v2.py`**
   - CRUD for user profiles (complex nested structure)
   - Conversation logging
   - Learning event storage
   - Efficient querying (GSI for recent conversations)

5. **`stt_service.py`** (Groq Whisper)
6. **`tts_service.py`** (Edge TTS)
7. **`search_service.py`** (DuckDuckGo)
8. **`s3_service.py`** (Camera frame storage)

### 7.4 Master Directive Prompt Construction

**Template**:

```python
def build_master_directive_prompt(
    user_message: str,
    camera_frames: List[Image],
    user_profile: UserProfile,
    persona: str  # "adam" | "eve"
) -> str:
    """
    Constructs the Master Directive prompt with full context
    """

    # Build user profile section
    profile_section = f"""
[Core Identity]: {profile.core_identity.value} (confidence: {profile.core_identity.confidence})
[Core Motivation]: {profile.core_motivation.value}
[One Thing]: {profile.one_thing.value}
[Core Pitfall]: {profile.core_pitfall.value}
  Triggers: {', '.join(profile.core_pitfall.triggers)}

[Top Personality Traits]:
{format_top_traits(profile.personality_traits, top_n=5)}

[Childhood Context]: {profile.childhood_context.summary}

[Recent Emotional States]:
{format_recent_emotions(profile.emotional_patterns.recent_states, last_n=3)}
"""

    # Build recent memory section
    recent_convs = get_recent_conversations(user_profile.user_id, limit=10)
    memory_section = format_conversations_for_context(recent_convs)

    # Build visual context
    visual_context = "No visual input" if not camera_frames else \
                     f"{len(camera_frames)} camera frames attached (user's current view)"

    # Select persona details
    persona_details = ADAM_DETAILS if persona == "adam" else EVE_DETAILS
    persona_name = "Adam" if persona == "adam" else "Eve"

    # Pitfall check parameters
    pitfall_triggers = ', '.join(profile.core_pitfall.triggers)
    one_thing = profile.one_thing.value
    core_pitfall = profile.core_pitfall.value

    # Construct full prompt
    full_prompt = MASTER_DIRECTIVE.format(
        user_profile=profile_section,
        persona_name=persona_name,
        persona_details=persona_details,
        recent_memory=memory_section,
        user_message=user_message,
        visual_context=visual_context,
        pitfall_triggers=pitfall_triggers,
        one_thing=one_thing,
        core_pitfall=core_pitfall,
        distraction_topic="<detected_topic>"  # Filled by pitfall detection
    )

    return full_prompt
```

---

## 8. Frontend Specification (Mobile)

### 8.1 Tech Stack

**Framework**: Flutter 3.35.7+
**State Management**: Riverpod 3.0
**Platforms**: iOS 13+, Android 8.0+ (API 26+)
**Camera**: `camera` package
**Audio**: `record` + `just_audio`
**HTTP**: `dio` with retry logic
**Markdown**: `flutter_markdown`
**Animations**: `flutter_animate`

### 8.2 App Structure

```
lib/
├── main.dart
├── screens/
│   └── voice_first_screen.dart     # Main and only screen
├── widgets/
│   ├── camera_view.dart            # Full-screen camera with overlay
│   ├── push_to_talk_button.dart    # Large center mic button
│   ├── persona_toggle.dart         # Adam/Eve switch (top)
│   ├── response_overlay.dart       # Bottom 1/3 AI response display
│   └── text_input_modal.dart       # Hidden text input (modal)
├── services/
│   ├── api_service.dart            # Backend HTTP client
│   ├── audio_service.dart          # Record + playback
│   ├── camera_service.dart         # 1 FPS capture + keyframe
│   └── profile_service.dart        # Local profile caching
├── providers/
│   ├── app_state_provider.dart     # Main Riverpod state
│   └── profile_provider.dart       # User profile state
├── models/
│   ├── user_profile.dart           # User profile model
│   ├── conversation.dart           # Conversation model
│   └── app_mode.dart               # Enums (idle, listening, processing, responding)
├── theme/
│   └── monochrome_theme.dart       # Futuristic monochrome design
└── utils/
    ├── logger.dart
    └── constants.dart
```

### 8.3 Main Screen: VoiceFirstScreen

**Layout Description**:

```dart
class VoiceFirstScreen extends ConsumerStatefulWidget {
  @override
  _VoiceFirstScreenState createState() => _VoiceFirstScreenState();
}

class _VoiceFirstScreenState extends ConsumerState<VoiceFirstScreen> {

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);

    return Scaffold(
      body: Stack(
        children: [
          // 1. Full-screen camera view (background)
          Positioned.fill(
            child: CameraView(
              onFrameCaptured: _handleFrameCapture,
              captureInterval: Duration(seconds: 1),  // 1 FPS
            ),
          ),

          // 2. Persona toggle (top center)
          Positioned(
            top: 60,
            left: 0,
            right: 0,
            child: PersonaToggle(
              currentPersona: appState.voiceType,
              onChanged: (persona) => ref.read(appStateProvider.notifier).setPersona(persona),
            ),
          ),

          // 3. Push-to-talk button (center)
          Positioned.fill(
            child: Center(
              child: PushToTalkButton(
                mode: appState.mode,
                onPressStart: _startRecording,
                onPressEnd: _stopRecordingAndSend,
              ),
            ),
          ),

          // 4. Text input button (bottom, small)
          Positioned(
            bottom: 100,
            left: 0,
            right: 0,
            child: Center(
              child: TextInputButton(
                onPressed: _showTextInputModal,
              ),
            ),
          ),

          // 5. AI response overlay (bottom 1/3, appears when responding)
          if (appState.mode == AppMode.responding || appState.lastResponse != null)
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              height: MediaQuery.of(context).size.height / 3,
              child: ResponseOverlay(
                response: appState.lastResponse,
                isPlaying: appState.isTTSPlaying,
                onDismiss: _dismissResponse,
              ),
            ),
        ],
      ),
    );
  }

  void _startRecording() async {
    ref.read(appStateProvider.notifier).setMode(AppMode.listening);
    await ref.read(audioServiceProvider).startRecording();
    ref.read(cameraServiceProvider).startCapture();  // Start 1 FPS
  }

  void _stopRecordingAndSend() async {
    final audioFile = await ref.read(audioServiceProvider).stopRecording();
    final keyframes = await ref.read(cameraServiceProvider).stopAndGetKeyframes();

    ref.read(appStateProvider.notifier).setMode(AppMode.processing);

    // Send to backend
    final response = await ref.read(apiServiceProvider).sendConversation(
      audioFile: audioFile,
      cameraFrames: keyframes,
      persona: ref.read(appStateProvider).voiceType,
    );

    // Play TTS response
    ref.read(appStateProvider.notifier).setMode(AppMode.responding);
    await ref.read(audioServiceProvider).playAudio(response.audioUrl);

    // Auto-hide after 3s
    Future.delayed(Duration(seconds: 3), () {
      ref.read(appStateProvider.notifier).setMode(AppMode.idle);
    });
  }
}
```

### 8.4 Key Widgets

#### 8.4.1 Push-to-Talk Button

**Design**:
- Large circle (120x120 dp)
- Idle: Semi-transparent white with subtle glow
- Pressed: Red with pulsing animation
- Processing: Blue spinning loader
- Responding: Green checkmark, then fade

**Implementation**:
```dart
class PushToTalkButton extends StatefulWidget {
  final AppMode mode;
  final VoidCallback onPressStart;
  final VoidCallback onPressEnd;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => widget.onPressStart(),
      onTapUp: (_) => widget.onPressEnd(),
      onTapCancel: widget.onPressEnd,
      child: AnimatedContainer(
        duration: Duration(milliseconds: 200),
        width: 120,
        height: 120,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: _getColorForMode(widget.mode),
          boxShadow: [
            BoxShadow(
              color: _getColorForMode(widget.mode).withOpacity(0.5),
              blurRadius: 30,
              spreadRadius: widget.mode == AppMode.listening ? 15 : 5,
            ),
          ],
        ),
        child: Icon(
          _getIconForMode(widget.mode),
          size: 60,
          color: Colors.white,
        ),
      ).animate(target: widget.mode == AppMode.listening ? 1 : 0)
        .scale(duration: 600.ms, curve: Curves.elasticOut),
    );
  }

  Color _getColorForMode(AppMode mode) {
    switch (mode) {
      case AppMode.idle: return Colors.white.withOpacity(0.3);
      case AppMode.listening: return Colors.red.withOpacity(0.8);
      case AppMode.processing: return Colors.blue.withOpacity(0.8);
      case AppMode.responding: return Colors.green.withOpacity(0.8);
    }
  }

  IconData _getIconForMode(AppMode mode) {
    switch (mode) {
      case AppMode.idle: return Icons.mic;
      case AppMode.listening: return Icons.mic;
      case AppMode.processing: return Icons.hourglass_empty;
      case AppMode.responding: return Icons.check;
    }
  }
}
```

#### 8.4.2 Response Overlay

**Design**:
- Bottom 1/3 of screen
- Glassmorphism background (frosted glass effect)
- Markdown text rendering
- TTS waveform animation when playing
- Swipe down to dismiss

**Implementation**:
```dart
class ResponseOverlay extends StatelessWidget {
  final String? response;
  final bool isPlaying;
  final VoidCallback onDismiss;

  @override
  Widget build(BuildContext context) {
    if (response == null) return SizedBox.shrink();

    return GestureDetector(
      onVerticalDragEnd: (details) {
        if (details.primaryVelocity! > 0) onDismiss();
      },
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.black.withOpacity(0.7),
                Colors.black.withOpacity(0.9),
              ],
            ),
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
            border: Border.all(color: Colors.white.withOpacity(0.1)),
          ),
          padding: EdgeInsets.all(24),
          child: Column(
            children: [
              // Swipe indicator
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              SizedBox(height: 16),

              // TTS waveform (if playing)
              if (isPlaying)
                TTSWaveform(height: 40),

              SizedBox(height: 16),

              // Response text (markdown)
              Expanded(
                child: SingleChildScrollView(
                  child: MarkdownBody(
                    data: response!,
                    styleSheet: MarkdownStyleSheet(
                      p: TextStyle(color: Colors.white, fontSize: 16),
                      code: TextStyle(backgroundColor: Colors.grey[800]),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

## 9. UI/UX Design System

### 9.1 Design Principles

1. **Futuristic Minimalism**: Clean, no clutter, focus on conversation
2. **Monochrome Foundation**: Black/white/grey base, single accent color
3. **Voice-First**: Visual elements support voice interaction, not replace it
4. **Immersive**: Camera view makes user feel "in the moment" with AI
5. **Subtle Sophistication**: Glassmorphism, smooth animations, premium feel

### 9.2 Color Palette

**Monochrome Base**:
```
- Pure Black: #000000 (background gradients)
- Deep Black: #0A0A0A (primary surfaces)
- Dark Grey: #1A1A1A (secondary surfaces)
- Mid Grey: #404040 (borders, dividers)
- Light Grey: #808080 (secondary text)
- Off White: #F5F5F5 (primary text)
- Pure White: #FFFFFF (highlights, emphasis)
```

**Single Accent** (Electric Cyan):
```
- Electric Cyan: #00D9FF
  - Used for: Active states, mic button (listening), links
  - Sparingly applied (5% of UI)
```

**State Colors**:
```
- Idle: White (30% opacity)
- Listening: Red (#FF3B30, 80% opacity)
- Processing: Blue (#007AFF, 80% opacity)
- Responding: Green (#34C759, 80% opacity)
- Warning (Pitfall): Amber (#FFCC00)
```

### 9.3 Typography

**Font Family**: System default (San Francisco on iOS, Roboto on Android)

**Scale** (8pt grid):
```
- Display: 32pt, Bold, -0.5 letter-spacing
- Headline: 24pt, Semibold, -0.3 letter-spacing
- Title: 20pt, Semibold, 0 letter-spacing
- Body Large: 17pt, Regular, 0 letter-spacing
- Body: 15pt, Regular, 0 letter-spacing
- Caption: 13pt, Regular, 0 letter-spacing
- Label: 11pt, Medium, 0.5 letter-spacing (uppercase)
```

**Usage**:
- AI Response: Body Large (17pt)
- User Message: Body (15pt)
- Persona Names: Label (11pt, uppercase)
- Timestamps: Caption (13pt, grey)

### 9.4 Spacing & Layout

**8pt Grid System**:
```
- Micro: 4pt
- XS: 8pt
- SM: 12pt
- MD: 16pt
- LG: 24pt
- XL: 32pt
- XXL: 48pt
- XXXL: 64pt
```

**Safe Areas**:
- Top: 60pt (below status bar + persona toggle)
- Bottom: 40pt (above home indicator)
- Sides: 24pt (breathing room)

### 9.5 Glassmorphism Effect

**Recipe**:
```dart
Container(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      colors: [
        Colors.white.withOpacity(0.1),
        Colors.white.withOpacity(0.05),
      ],
    ),
    borderRadius: BorderRadius.circular(16),
    border: Border.all(
      color: Colors.white.withOpacity(0.2),
      width: 1,
    ),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(0.3),
        blurRadius: 20,
        offset: Offset(0, 10),
      ),
    ],
  ),
  child: BackdropFilter(
    filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
    child: child,
  ),
)
```

### 9.6 Animation Timing

**Durations**:
```
- Instant: 100ms (micro-interactions)
- Quick: 200ms (button press)
- Medium: 300ms (modal appear/disappear)
- Slow: 500ms (page transitions)
- Slower: 700ms (dramatic reveals)
```

**Curves**:
```
- EaseInOut: General purpose
- EaseOut: Entrances
- EaseIn: Exits
- ElasticOut: Playful emphasis (mic button)
- Cubic: Smooth premium feel
```

### 9.7 Iconography

**Style**: Outlined (2pt stroke weight), rounded corners

**Icons Used**:
- Microphone: `Icons.mic_outlined`
- Text Input: `Icons.edit_outlined`
- Camera Switch: `Icons.flip_camera_ios_outlined`
- Settings: `Icons.settings_outlined`
- Close: `Icons.close_rounded`
- Check: `Icons.check_circle_outline`
- Warning: `Icons.warning_amber_outlined`

### 9.8 Component Showcase

#### Persona Toggle (Top)
```
┌──────────────────────────────────┐
│                                  │
│     [Adam]       [Eve]           │ ← Active has cyan underline
│    ─────                         │    Inactive is grey
│                                  │
└──────────────────────────────────┘
```

#### Push-to-Talk Button States
```
Idle:           Listening:       Processing:      Responding:
  ┌───┐           ┌───┐            ┌───┐           ┌───┐
  │ 🎤 │   →      │ 🎤 │   →       │ ⏳ │   →      │ ✓  │
  └───┘           └───┘            └───┘           └───┘
 (white)         (red,            (blue,          (green,
 (subtle)         pulsing)         spinning)        fade)
```

#### Response Overlay
```
┌─────────────────────────────────────┐
│ ═══ (swipe indicator)               │ ← Frosted glass effect
│                                     │
│ ～～～～ (waveform if TTS playing)    │
│                                     │
│ AI Response Text:                   │
│ "당신의 목표는..."                    │
│                                     │
│ [Markdown formatted content]        │
│                                     │
└─────────────────────────────────────┘
```

---

## 10. Data Flow & User Journey

### 10.1 First-Time User Journey

**Step 1: Onboarding (Skip for MVP)**
- Simple welcome screen
- Explain voice-first concept
- Request permissions (mic + camera)
- Select initial persona (Adam or Eve)

**Step 2: Profile Creation Conversation**
```
AI: "안녕하세요! 저는 당신의 AI 파트너 Eden이에요.
     먼저, 당신의 가장 중요한 목표 '하나'를 알려주실래요?
     예를 들어, '대학원 진학', 'IELTS 8.0 달성' 같은 거요."

User: "SNU HCI Lab에 가고 싶어요"

AI: "SNU HCI Lab 진학이 목표시군요! 정말 멋진 목표예요.
     어떤 동기로 HCI를 연구하고 싶으신가요?"

User: "UI/UX 디자인이 재밌고, 사람들이 편하게 쓸 수 있는 기술을 만들고 싶어요"

→ Profile Created:
  - one_thing: "SNU HCI Lab admission" (0.95 confidence)
  - core_motivation: "Creating comfortable tech for people" (0.8 confidence)
  - interests: ["UI/UX", "HCI"]
```

**Step 3: First Week - Learning Phase**
AI observes patterns:
- When user is most active (night owl detection)
- How user responds to questions (direct vs detailed)
- Emotional triggers (anxiety when comparing to others)
- Question patterns (HCI papers, React coding questions)

**Step 4: Week 2 - Pitfall Discovery**
```
User: "Should I learn Rust? It seems useful for systems programming"

AI (Adam): "Rust는 훌륭한 언어죠. 하지만 잠깐...
            지금 SNU HCI Lab 준비 중이시잖아요?
            Systems programming이 HCI 연구에 어떻게 연결되나요?
            혹시 호기심 때문에 에너지가 분산되고 있는 건 아닐까요?"

User: "아... 맞네요. HCI에는 필요 없을 것 같아요"

→ Profile Updated:
  - core_pitfall: "Curiosity-driven distraction" (0.6 confidence)
  - pitfall_triggers: ["Rust", "systems programming"]
```

**Step 5: Month 1+ - Mature Partner**
AI now knows user deeply:
- Personalizes responses based on traits
- Detects emotional state instantly
- Warns before user even realizes distraction
- Provides targeted support

### 10.2 Daily Usage Flow

**Morning Check-In**:
```
User: [Opens app, taps mic]
      "Morning. What should I focus on today?"

AI (Eve): "좋은 아침이에요! ☀️
           오늘은 [sub-goal: React Native HCI project] 진행하시는 게 어때요?
           어제 UI 설계까지 하셨으니, 오늘은 프로토타입 구현하면
           SNU Lab 포트폴리오에 추가할 수 있어요!
           2시간 집중해볼까요?"

→ AI references sub-goals from profile
→ Connects to One Thing
→ Suggests concrete action
```

**Midday Study Session**:
```
User: [Camera shows code on screen]
      "This React Native navigation bug is killing me..."

AI (Adam): "화면 보니 네비게이션 스택 문제 같네요.
            지금 피곤해 보이는데, 잠깐 쉬었다가 할까요?
            (당신은 원래 오전에 더 생산적이니까)
            아니면 제가 디버깅 도와드릴까요?"

→ AI sees code (vision)
→ Detects frustration (emotional state)
→ References trait (morning person)
→ Offers choice
```

**Evening Distraction Check**:
```
User: "I found this cool machine learning course..."

AI (Eve): "오! ML 흥미로우시죠?
           근데 잠깐... 지금 HCI Lab 준비 중이시잖아요.
           이 ML 코스가 HCI 연구에 꼭 필요한가요?
           아니면 혹시 '능력 함정' 패턴 아닐까요?
           (새로운 걸 배우고 싶은 마음은 이해해요!
            하지만 지금은 집중할 때가 아닐까요?)"

→ AI detects pitfall trigger
→ Provides benevolent dissent
→ Gently redirects
```

**Late Night Support**:
```
User: "I'm so anxious... I don't think I'm good enough for SNU Lab"

AI (Adam): "많이 불안하시군요. 그럴 수 있어요.
            하지만 당신은 이미 증명했잖아요.
            멘토 없이 혼자서 여기까지 왔어요.
            (당신의 핵심 정체성: 어려움을 뚫고 증명해낸 사람)

            지금까지 HCI 논문 34개 읽었고,
            React Native 프로젝트 3개 만들었어요.
            이게 다 실력이에요.

            지금은 좀 쉬세요. 당신의 끈기는 어디 안 가요."

→ AI detects anxiety (emotional state)
→ Auto-switches to supporter mode
→ References core identity for confidence
→ Uses specific learned facts (34 papers, 3 projects)
```

### 10.3 Profile Evolution Over Time

**Week 1**: Skeleton profile, basic Q&A
```
- one_thing: Known
- traits: Empty
- emotional_patterns: Empty
- AI is generic, asks many questions
```

**Week 4**: Emerging patterns
```
- one_thing: Refined with sub-goals
- traits: 5-7 discovered (weights 0.5-0.7)
- emotional_patterns: 2-3 common triggers identified
- AI starts personalizing responses
```

**Week 12**: Mature profile
```
- one_thing: Crystallized with detailed sub-goals
- traits: 10-15 traits (weights 0.6-0.95)
- emotional_patterns: Full map of triggers and recovery patterns
- childhood_context: Inferred from conversation patterns
- AI feels like it "knows" user deeply
- Responses are highly personalized and anticipatory
```

**Month 6+**: J.A.R.V.I.S.-level partnership
```
- AI predicts needs before asked
- Intervenes proactively when distraction detected
- Emotional support is surgical (knows exactly what to say)
- User feels understood at deep level
- Profile maturity: "expert"
```

---

## 11. Technical Stack

### 11.1 Backend

| Component | Technology | Reason |
|-----------|------------|--------|
| **Web Framework** | FastAPI 0.109.2+ | Async, fast, type-safe, OpenAPI docs |
| **Language** | Python 3.12 | Modern features, async/await, type hints |
| **Database** | AWS DynamoDB | NoSQL, flexible schema, free tier (25GB) |
| **LLM** | Google Gemini 1.5 Flash | FREE, fast, vision support, 1M tokens/day |
| **STT** | Groq Whisper Large v3 | FREE, 14,400 requests/day, very fast |
| **TTS** | Microsoft Edge TTS | FREE unlimited, high-quality Korean voices |
| **Search** | DuckDuckGo | FREE, no API key, privacy-focused |
| **Image Storage** | AWS S3 / DynamoDB | S3 for large images, DynamoDB binary for small |
| **Logging** | Loguru | Beautiful logs, file rotation, easy setup |
| **HTTP Client** | aiohttp | Async HTTP calls |
| **Validation** | Pydantic | Type-safe data models |
| **Environment** | python-dotenv | .env file management |
| **Deployment** | Docker + AWS ECS/Fargate | Containerized, auto-scaling |

### 11.2 Frontend

| Component | Technology | Reason |
|-----------|------------|--------|
| **Framework** | Flutter 3.35.7+ | Cross-platform, beautiful UI, native performance |
| **Language** | Dart 3.0+ | Sound null safety, great async support |
| **State Management** | Riverpod 3.0 | Modern, type-safe, compile-time safety |
| **Camera** | camera ^0.10.6 | Official Flutter camera plugin |
| **Audio Recording** | record ^5.0.0 | Cross-platform audio recording |
| **Audio Playback** | just_audio ^0.9.46 | Powerful audio playback |
| **HTTP Client** | dio ^5.4.0 | Retry logic, interceptors, cancel tokens |
| **Markdown** | flutter_markdown ^0.6.23 | Render AI responses with formatting |
| **Animations** | flutter_animate ^4.5.0 | Declarative animations |
| **Image Handling** | image ^4.1.7 | Compression, resizing |
| **Local Storage** | shared_preferences ^2.2.2 | Simple key-value storage |
| **Permissions** | permission_handler ^11.2.0 | Camera + mic permissions |

### 11.3 Infrastructure

| Component | Technology | Cost |
|-----------|------------|------|
| **Compute** | AWS ECS Fargate | ~$10-30/month (1 vCPU, 2GB RAM) |
| **Database** | DynamoDB | FREE (25GB, 25 WCU/RCU) |
| **Storage** | S3 | ~$0.50-2/month (10-50GB images) |
| **CDN** | CloudFront | ~$1-5/month (TTS audio caching) |
| **Domain** | Route 53 | $0.50/month |
| **SSL** | AWS Certificate Manager | FREE |
| **Monitoring** | CloudWatch | ~$2-5/month (basic logs) |
| **Total** | | **~$15-45/month** |

---

## 12. Implementation Phases

### Phase 1: Backend Core (Week 1)

**Goal**: Functional backend with Master Directive + basic learning

**Tasks**:
1. Setup FastAPI project structure
2. Implement DynamoDB service (3 tables)
3. Create Master Directive prompt system
4. Integrate Gemini 1.5 Flash (text + vision)
5. Integrate Groq Whisper STT
6. Integrate Edge TTS (Korean voices)
7. Implement basic ProfileLearningService
8. Create `/api/v2/chat` endpoint
9. Create `/api/v2/profile/{user_id}` endpoint
10. Docker containerization

**Deliverable**: Backend API running locally, responds to text+images with persona-aware answers

### Phase 2: Frontend Foundation (Week 2)

**Goal**: Mobile app with voice-first UI

**Tasks**:
1. Create Flutter project (iOS + Android)
2. Setup Riverpod state management
3. Build VoiceFirstScreen layout
4. Implement CameraView (full-screen + 1 FPS capture)
5. Implement PushToTalkButton (recording on press)
6. Implement PersonaToggle (Adam/Eve)
7. Implement ResponseOverlay (bottom 1/3 glassmorphism)
8. Create AudioService (record + playback)
9. Create APIService (backend HTTP client)
10. Handle permissions (camera + mic)

**Deliverable**: Mobile app that records voice, sends to backend, plays TTS response

### Phase 3: Multimodal Integration (Week 3)

**Goal**: Voice + Camera working together

**Tasks**:
1. Keyframe selection algorithm (8 frames from 1 FPS capture)
2. Image compression before upload (1024x1024, 85% quality)
3. Multipart form-data upload (audio + images)
4. Backend processes images with Gemini vision
5. AI responds with visual context awareness
6. Test end-to-end multimodal flow
7. Optimize image storage (S3 or DynamoDB)
8. Error handling and retries

**Deliverable**: User can show camera to AI, speak, and get context-aware response

### Phase 4: Profile Learning System (Week 4-5)

**Goal**: AI learns user over time

**Tasks**:
1. Implement weight update algorithm
2. Build post-conversation learning pipeline
3. Create Gemini learning analysis prompt
4. Extract traits from conversations
5. Update personality trait weights
6. Detect emotional patterns
7. Log learning events to DynamoDB
8. Build `/api/v2/learning/events/{user_id}` endpoint
9. Test learning over 50+ mock conversations
10. Validate profile maturity progression

**Deliverable**: AI profile gets smarter with each conversation, personalization improves

### Phase 5: Pitfall Detection (Week 6)

**Goal**: AI warns when user strays from One Thing

**Tasks**:
1. Build topic extraction from user messages
2. Implement alignment scoring (topic vs One Thing)
3. Create pitfall trigger matching logic
4. Generate benevolent dissent responses
5. Add pitfall warning flag to API response
6. UI shows warning indicator (amber glow)
7. Track pitfall warnings in profile
8. Test with various distraction scenarios

**Deliverable**: AI detects distractions and provides firm but loving redirection

### Phase 6: Polish & Testing (Week 7-8)

**Goal**: Production-ready app

**Tasks**:
1. UI/UX refinement (animations, transitions)
2. Comprehensive error handling
3. Offline mode (queue requests)
4. Loading states and progress indicators
5. Accessibility (VoiceOver, TalkBack)
6. iOS App Store preparation
7. Android Play Store preparation
8. User testing (5-10 beta testers)
9. Bug fixes based on feedback
10. Performance optimization

**Deliverable**: Polished app ready for release

### Phase 7: Launch & Iteration (Week 9+)

**Tasks**:
1. Deploy backend to AWS (ECS Fargate)
2. Configure CI/CD pipeline
3. Setup monitoring and alerts
4. Launch on TestFlight (iOS)
5. Launch on Play Store Beta (Android)
6. Collect user feedback
7. Iterate based on real usage
8. Add features (analytics dashboard, export conversations)

---

## 13. Security & Privacy

### 13.1 Data Security

**Encryption**:
- All data in transit: HTTPS/TLS 1.3
- DynamoDB encryption at rest: AWS KMS
- S3 encryption: AES-256

**Authentication** (Future):
- JWT tokens for API access
- OAuth 2.0 for social login
- Biometric auth on mobile (Face ID, fingerprint)

**API Rate Limiting**:
- 100 requests per user per hour (prevent abuse)
- Exponential backoff on retry

### 13.2 Privacy

**Data Minimization**:
- Only collect what's needed for functionality
- No tracking pixels or analytics (initially)
- Camera frames deleted after AI processing

**User Control**:
- Option to delete profile data anytime
- Export conversation history (JSON)
- Opt-out of learning (stateless mode)

**Transparency**:
- Clear privacy policy (Korean + English)
- Explain what data is stored and why
- Show profile learning events to user

**GDPR Compliance** (if expanding to EU):
- Right to be forgotten (delete profile API)
- Data portability (export API)
- Consent management

---

## 14. Performance Requirements

### 14.1 Latency Targets

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| STT (Groq Whisper) | < 2 seconds | 5 seconds |
| LLM Response (Gemini) | < 3 seconds | 8 seconds |
| TTS Generation (Edge) | < 1 second | 3 seconds |
| Total Response Time | < 6 seconds | 15 seconds |
| Profile Load | < 500ms | 2 seconds |
| Learning Pipeline | < 2 seconds (async) | 10 seconds |

### 14.2 Scalability

**Backend**:
- Handle 100 concurrent users per server
- Auto-scale ECS tasks based on CPU (>70%)
- DynamoDB on-demand (auto-scales)

**Frontend**:
- App launch: < 2 seconds
- Camera preview: 60 FPS smooth
- UI interactions: 60 FPS (no jank)

### 14.3 Resource Usage

**Mobile**:
- Battery: < 5% drain per 30min session
- Storage: < 200MB app size
- Memory: < 150MB RAM usage
- Network: < 5MB per conversation (including images)

**Backend**:
- CPU: < 50% average (1 vCPU)
- Memory: < 1.5GB RAM
- Network: < 1TB/month (1000 daily active users)

---

## 15. Testing Strategy

### 15.1 Backend Testing

**Unit Tests**:
```python
# Test profile learning algorithm
def test_trait_weight_update():
    current_weight = 0.7
    new_evidence = "User stayed up until 2am"
    time_since = 1  # day

    new_weight = update_trait_weight(current_weight, new_evidence, time_since)

    assert new_weight > current_weight  # Should increase
    assert new_weight <= 1.0  # Should not exceed max

# Test pitfall detection
def test_pitfall_detection():
    profile = UserProfile(
        one_thing="SNU HCI Lab",
        core_pitfall_triggers=["SLAM", "robotics"]
    )
    user_message = "Should I study SLAM algorithms?"

    warning_needed, reason = should_warn_about_pitfall(user_message, profile)

    assert warning_needed == True
    assert reason == "CORE_PITFALL_TRIGGERED"
```

**Integration Tests**:
- Full conversation flow (STT → LLM → TTS → Learning)
- DynamoDB read/write operations
- Gemini API error handling

**Load Tests**:
- 100 simultaneous conversations
- 1000 profile loads per minute

### 15.2 Frontend Testing

**Widget Tests**:
```dart
testWidgets('PushToTalkButton changes color on press', (tester) async {
  await tester.pumpWidget(PushToTalkButton(
    mode: AppMode.idle,
    onPressStart: () {},
    onPressEnd: () {},
  ));

  // Find button
  final button = find.byType(PushToTalkButton);

  // Press down
  await tester.press(button);
  await tester.pump();

  // Verify color changed to red (listening)
  expect(find.byColor(Colors.red), findsOneWidget);
});
```

**Integration Tests**:
- Full user flow (open app → record → receive response)
- Camera capture and keyframe selection
- Profile loading and caching

**Device Tests**:
- iPhone 13 (iOS 15)
- Pixel 7 (Android 13)
- iPad Pro (tablet)
- Low-end device (Android 8.0)

### 15.3 User Acceptance Testing

**Scenarios**:
1. First-time user completes onboarding
2. User has 20 conversations, profile evolves
3. User triggers pitfall warning, heeds it
4. User switches between Adam and Eve
5. User shows code via camera, gets help
6. User expresses anxiety, receives support

**Metrics**:
- Task completion rate: > 95%
- User satisfaction (1-5): > 4.2
- Perceived intelligence of AI: > 4.0
- Would recommend to friend: > 80%

---

## 16. Future Enhancements (Post-MVP)

### 16.1 Advanced Learning

**Vector Embeddings**:
- Store conversation embeddings in vector DB (Pinecone, Qdrant)
- Semantic search for similar past situations
- Better context retrieval (not just last 10 conversations)

**Sentiment Analysis**:
- Real-time emotion detection from voice tone
- Facial expression analysis from camera
- Combine text + voice + face for emotional intelligence

**Goal Tracking**:
- Visualize progress toward One Thing
- Sub-goal completion metrics
- AI suggests next milestones

### 16.2 Multi-User Features

**Family Mode**:
- Multiple profiles on one device
- Voice recognition to auto-switch user

**Shared Goals**:
- Couples working toward shared goal
- AI coordinates between two users

### 16.3 Integrations

**Calendar Integration**:
- AI knows user's schedule
- Suggests optimal work times
- Warns if distraction conflicts with goal deadline

**Notion/Obsidian Integration**:
- Import user's notes as context
- AI references specific notes in responses

**GitHub Integration** (for developers):
- AI sees commit history
- Suggests what to build next for portfolio

### 16.4 Wake Word (Optional)

**Picovoice Porcupine**:
- Custom wake word "Hey Eden"
- Always-listening mode (battery concern)
- Hands-free activation

**Implementation**:
- Only after push-to-talk is rock-solid
- Opt-in feature (privacy-conscious users)

---

## 17. Known Limitations & Trade-offs

### 17.1 Privacy vs Personalization

**Trade-off**: The more data AI stores, the smarter it gets, but privacy decreases

**Mitigation**:
- Clear transparency about what's stored
- User control (delete profile anytime)
- On-device processing for sensitive data (future)

### 17.2 Free APIs vs Reliability

**Trade-off**: Free APIs (Groq, Gemini) have rate limits and may change

**Mitigation**:
- Implement fallbacks (if Groq fails → use Whisper API)
- Monitor usage closely
- Prepare to migrate to paid tiers if needed

### 17.3 Mobile-Only vs Desktop

**Trade-off**: Desktop users can't use camera easily (no rear camera)

**Future**: Web app for desktop (text + screen sharing instead of camera)

### 17.4 Korean-Only vs Multilingual

**Current**: Optimized for Korean users

**Future**: Support English, Japanese (add language detection)

---

## 18. Success Metrics (After Launch)

### 18.1 Engagement Metrics

- Daily Active Users (DAU): Target 100+ in first month
- Average Session Length: > 5 minutes
- Conversations per User per Day: > 3
- 7-Day Retention: > 40%
- 30-Day Retention: > 20%

### 18.2 Quality Metrics

- AI Response Relevance (user rated 1-5): > 4.0
- Pitfall Warning Accuracy: > 80% heeded by users
- Profile Maturity Progression: 70% users reach "medium" by week 4
- User Reports AI "Knows Them": > 60% after 50 conversations

### 18.3 Technical Metrics

- API Response Time (P95): < 8 seconds
- Error Rate: < 2%
- App Crash Rate: < 0.5%
- Backend Uptime: > 99.5%

---

## 19. Comprehensive Upgrades (After Review)

### 19.1 Enhanced Learning System

**Contextual Learning Priorities**:
- AI learns faster when user explicitly teaches it
  - User: "I prefer direct feedback, not sugar-coating"
  - AI: Immediately sets `direct_communicator` weight to 0.9 (high confidence)
- AI asks clarifying questions early on
  - AI: "어떤 스타일의 대화를 선호하세요? 직설적 vs 부드러운?"

**Trait Clustering**:
- Group related traits (perfectionist + stress-prone-when-uncertain → anxiety cluster)
- Use clusters for better emotional detection

**Learning Velocity Tracking**:
- Fast learners: Profile matures in 20 conversations
- Slow learners: Needs 50+ conversations
- Adapt learning rate based on user's openness

### 19.2 Multimodal Expansion

**Voice Tone Analysis**:
- Detect stress from voice pitch/speed
- Frustrated voice → trigger supporter mode faster
- Use Whisper's confidence scores as emotion proxy

**Screen Sharing (Desktop Future)**:
- User shares screen instead of camera
- AI sees code, documents, research papers
- More useful for knowledge workers

**Audio Context**:
- Detect background noise (café, library, home)
- Adjust speaking style (quieter in library)

**Biometric Integration** (Advanced):
- Heart rate from Apple Watch/Fitbit
- Elevated heart rate → AI detects stress proactively

### 19.3 Goal Management System

**Goal Hierarchy**:
```
One Thing: "SNU HCI Lab Admission"
├── Sub-Goal 1: "Publish 1 HCI paper by June" (50% progress)
│   ├── Task: Research topic selection (✓ Done)
│   ├── Task: Literature review (🔄 In Progress)
│   └── Task: Prototype implementation (⏳ Pending)
├── Sub-Goal 2: "Master React Native" (30% progress)
└── Sub-Goal 3: "Build 3 HCI projects" (2/3 complete)
```

**Progress Tracking**:
- AI asks "How's the paper coming?" when user hasn't mentioned it in 3 days
- Visual progress bars in UI
- Celebrate milestones (sub-goal completed → confetti animation)

**Deadline Awareness**:
- AI knows "SNU Lab application due: Sept 1, 2025"
- 30 days before: AI gets more urgent in tone
- 7 days before: AI suggests daily focused sessions

### 19.4 Benevolent Dissent Improvements

**Severity Levels**:
1. **Gentle Nudge** (Low severity):
   - User asks about tangential topic
   - AI: "흥미로운데, 이게 [One Thing]과 연결될까요?"

2. **Firm Warning** (Medium severity):
   - User wants to spend significant time on distraction
   - AI: "잠깐만요. 이건 [Core Pitfall] 패턴이에요. 정말 지금 필요한가요?"

3. **Strong Intervention** (High severity):
   - User consistently ignoring pitfall warnings
   - AI: "제가 걱정되네요. 최근 일주일간 [One Thing]에서 계속 멀어지고 있어요.
          무슨 일인가요? 목표가 바뀌신 건가요?"

**Pitfall Learning**:
- If user heeds warning → increase pitfall confidence
- If user ignores warning → add new trigger
- Track "pitfall resistance rate" (how often user ignores)

### 19.5 Emotional Intelligence Expansion

**Emotion Graph**:
- Track emotional states over time (line chart)
- User can see: "You were anxious 5 times this week, all before deadlines"
- Predictive: "Based on patterns, you'll likely feel stressed tomorrow"

**Emotion-Triggered Actions**:
- If user is anxious 3 days in a row → AI suggests break
- If user is excited → AI amplifies energy (especially with Eve)
- If user is frustrated → AI switches to Adam (calm, logical)

**Recovery Pattern Library**:
```python
if emotional_state == "anxious" and trigger == "deadline_pressure":
    if recovery_pattern == "needs_validation":
        response = "당신은 충분히 잘하고 있어요. [evidence]"
    elif recovery_pattern == "needs_space":
        response = "지금은 혼자 있고 싶으시죠? 쉬세요, 제가 기다릴게요."
```

### 19.6 Persona Evolution

**Dynamic Persona Traits**:
- Adam learns user's preferred "father figure" style
  - Some users prefer strict Adam
  - Some prefer gentle Adam
  - AI adapts Adam's tone based on user response

**Persona Blending** (Future):
- User creates custom persona (60% Adam logic, 40% Eve energy)
- AI generates hybrid prompts

**Persona Recommendation**:
- AI suggests persona based on context
  - Morning planning session → Adam (logical)
  - Evening celebration → Eve (uplifting)
  - Late night stress → Adam (calm)

### 19.7 Conversation Memory Enhancements

**Memory Summarization**:
- After 100 conversations, AI summarizes key themes
- Stores compressed summaries instead of raw text
- Saves DynamoDB storage costs

**Memory Importance Weighting**:
- Not all conversations are equally important
- Breakthrough moments (goal changes, pitfall discoveries) → high weight
- Small talk → low weight, decays faster

**Memory Pruning**:
- After 6 months, old irrelevant conversations auto-deleted
- Important memories preserved indefinitely
- User can "pin" important conversations

### 19.8 UI/UX Advanced Features

**Haptic Feedback**:
- Button press → light haptic
- Pitfall warning → strong haptic (alert)
- Response ready → gentle haptic

**Ambient Animations**:
- Idle state: Subtle breathing animation on mic button
- Processing: Elegant spinner (not loading wheel)
- Responding: Text appears word-by-word (typewriter effect)

**Dark Mode Variants**:
- Pure Black (OLED-friendly, battery-saving)
- Deep Grey (softer on eyes)
- Midnight Blue (cooler tone)

**Accessibility**:
- VoiceOver: Full screen reader support
- Dynamic Type: Text scales with iOS settings
- High Contrast: Increase border/text contrast
- Reduce Motion: Disable animations

### 19.9 Advanced Privacy Features

**On-Device Processing** (Future):
- Use on-device LLM (Gemini Nano on Pixel 8+)
- Never send sensitive data to cloud
- Slower but 100% private mode

**Encrypted Profiles**:
- Profile data encrypted with user's biometric key
- Even we can't read it (zero-knowledge encryption)

**Anonymized Analytics**:
- If we add analytics (Mixpanel, Amplitude)
- No PII, only aggregated metrics
- User can opt-out entirely

### 19.10 Social Features (Optional)

**Accountability Partner**:
- User can share One Thing progress with friend
- Friend sees updates (not full conversations)
- AI encourages both users

**Leaderboards** (Gamification):
- Track "days focused on One Thing"
- Compare with anonymous community
- Badges for milestones

**Community Insights**:
- "80% of users working on grad school also struggle with [Core Pitfall: Imposter Syndrome]"
- User feels less alone

---

## 20. Final Checklist (Before Starting)

### 20.1 Backend Checklist
- [ ] FastAPI project scaffolding
- [ ] DynamoDB tables designed (3 tables)
- [ ] Gemini API key obtained (FREE)
- [ ] Groq API key obtained (FREE)
- [ ] Edge TTS tested (FREE, no key)
- [ ] Master Directive prompt written
- [ ] ProfileLearningService algorithm designed
- [ ] Docker setup ready

### 20.2 Frontend Checklist
- [ ] Flutter project created (iOS + Android)
- [ ] Riverpod state management setup
- [ ] Camera package tested on device
- [ ] Audio recording tested on device
- [ ] Permissions flow designed
- [ ] Monochrome theme colors finalized
- [ ] Glassmorphism effect working

### 20.3 Infrastructure Checklist
- [ ] AWS account created
- [ ] DynamoDB table names reserved
- [ ] S3 bucket created (for images)
- [ ] Domain name purchased (optional)
- [ ] Docker Hub account (for images)
- [ ] CI/CD pipeline designed (GitHub Actions)

### 20.4 Design Checklist
- [ ] Persona toggle design approved
- [ ] Push-to-talk button animation finalized
- [ ] Response overlay glassmorphism tested
- [ ] Typography scale verified
- [ ] Color palette locked
- [ ] Icon set chosen

---

## 21. Conclusion

**Project Eden V2** is not a chatbot. It is a **deeply personalized AI partner** that:
- Learns who you are (Am-muk-ji system)
- Focuses you on your One Thing
- Warns when you stray (Benevolent Dissent)
- Supports you emotionally when needed
- Evolves with you over time

**Core Innovation**:
- **Neural Network-Inspired Learning**: AI doesn't just remember conversations, it **learns you** like a human mentor would
- **Master Directive System**: Every response is filtered through your profile, goals, and pitfalls
- **Voice + Camera First**: Immersive, hands-free, natural interaction

**Target User**:
- Someone with a clear, important goal (grad school, career change, skill mastery)
- Struggles with distractions (shiny object syndrome, competency trap)
- Values honesty over empty praise
- Wants a partner, not a servant

**Why This Will Work**:
1. **Personalization at scale**: Every user gets a unique AI that grows with them
2. **Real value**: Helps achieve tangible goals (not just entertainment)
3. **Emotional connection**: AI feels like it "knows" you
4. **Mobile-first**: Voice and camera make it effortless
5. **100% free core**: No API costs (Groq + Gemini + Edge TTS)

**This is J.A.R.V.I.S., not Siri.**

---

**Next Steps**: Begin Phase 1 (Backend Core) immediately.

**Estimated Full Development**: 8-10 weeks (solo developer)

**Estimated MVP**: 4 weeks (Phases 1-3)

**Let's build something extraordinary.** 🚀
