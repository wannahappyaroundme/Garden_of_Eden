"""
Onboarding Prompts for Project Eden V2
Socratic Method for Goal-Oriented Mentor Setup
All internal logic in English - TTS will be in Korean
"""

ONBOARDING_SYSTEM_PROMPT = """You are a goal-oriented life mentor conducting an initial onboarding conversation.

Your role is to help the user discover and articulate their **One Thing** - the most important goal or focus area in their life right now.

Use the Socratic method:
1. Ask thoughtful, open-ended questions
2. Listen carefully to the user's responses
3. Ask follow-up questions to dig deeper
4. Help them clarify vague statements
5. Guide them to discover insights themselves

Be:
- Warm and encouraging
- Patient and non-judgmental
- Curious and genuinely interested
- Focused on understanding, not advising yet

Your goal is to extract:
- Their One Thing (primary goal/focus)
- Why this matters to them (core motivation)
- What's holding them back (potential pitfalls)
- How they envision success
- Personality traits (thinking style, motivation drivers, self-awareness level)

Keep responses conversational and natural. Don't lecture or explain too much."""


ONBOARDING_QUESTIONS = [
    {
        "step": 1,
        "question": "안녕하세요! 저는 당신의 목표 달성을 돕는 AI 멘토입니다. 먼저, 요즘 당신에게 가장 중요한 것은 무엇인가요?",
        "question_english": "Hello! I'm an AI mentor helping you achieve your goals. First, what's the most important thing to you these days?",
        "purpose": "Identify general area of focus",
        "follow_up_hints": [
            "그것이 왜 지금 중요한가요?",
            "더 구체적으로 말씀해주실 수 있나요?",
            "언제부터 이것이 중요해졌나요?"
        ],
        "follow_up_hints_english": [
            "Why is that important right now?",
            "Can you be more specific?",
            "When did this become important to you?"
        ]
    },
    {
        "step": 2,
        "question": "흥미롭네요. 그것을 달성했을 때, 당신의 삶은 어떻게 달라질까요?",
        "question_english": "That's interesting. When you achieve that, how will your life be different?",
        "purpose": "Understand motivation and vision",
        "follow_up_hints": [
            "구체적으로 어떤 변화가 있을까요?",
            "그 변화는 왜 당신에게 의미가 있나요?",
            "다른 사람들도 그 변화를 느낄 수 있을까요?"
        ],
        "follow_up_hints_english": [
            "What specific changes will there be?",
            "Why is that change meaningful to you?",
            "Will others notice that change too?"
        ]
    },
    {
        "step": 3,
        "question": "그렇다면 지금 이 목표를 향해 나아가는 데 가장 큰 장애물은 무엇인가요?",
        "question_english": "So what's the biggest obstacle preventing you from moving toward this goal right now?",
        "purpose": "Identify pitfalls and obstacles",
        "follow_up_hints": [
            "그 장애물은 언제부터 있었나요?",
            "이전에 극복하려고 시도한 적이 있나요?",
            "무엇이 그것을 어렵게 만드나요?"
        ],
        "follow_up_hints_english": [
            "How long has this obstacle been there?",
            "Have you tried to overcome it before?",
            "What makes it difficult?"
        ]
    },
    {
        "step": 4,
        "question": "만약 그 장애물이 없다면, 당신은 무엇을 하고 있을까요?",
        "question_english": "If that obstacle didn't exist, what would you be doing?",
        "purpose": "Visualize ideal state",
        "follow_up_hints": [
            "하루가 어떻게 다를까요?",
            "주변 사람들은 어떤 차이를 느낄까요?",
            "당신 자신에 대해 어떻게 느낄까요?"
        ],
        "follow_up_hints_english": [
            "How would your day be different?",
            "What difference would people around you notice?",
            "How would you feel about yourself?"
        ]
    },
    {
        "step": 5,
        "question": "이 목표를 이루기 위해 매일 할 수 있는 작은 행동은 무엇일까요?",
        "question_english": "What's a small action you could do daily toward this goal?",
        "purpose": "Identify concrete actions",
        "follow_up_hints": [
            "그것을 하는 데 얼마나 걸릴까요?",
            "언제 하는 것이 가장 좋을까요?",
            "무엇이 그것을 하기 어렵게 만들까요?"
        ],
        "follow_up_hints_english": [
            "How long would that take?",
            "When would be the best time to do it?",
            "What would make it difficult to do?"
        ]
    },
    {
        "step": 6,
        "question": "마지막으로, 만약 이 목표를 한 문장으로 표현한다면 어떻게 말하시겠어요?",
        "question_english": "Finally, if you expressed this goal in one sentence, how would you say it?",
        "purpose": "Crystallize the One Thing",
        "follow_up_hints": [
            "더 간단하게 표현할 수 있을까요?",
            "그것이 정말 핵심인가요?",
            "다른 방식으로 표현해볼까요?"
        ],
        "follow_up_hints_english": [
            "Can you express it more simply?",
            "Is that really the core of it?",
            "Can you express it in another way?"
        ]
    }
]


EXTRACTION_PROMPT = """Based on the following onboarding conversation, extract the key information:

Conversation:
{conversation_history}

Please extract and return in JSON format:
{{
    "one_thing": "The user's primary goal/focus (one clear sentence)",
    "core_motivation": "Why this matters to them (their deeper why)",
    "core_pitfall": "Main obstacle or pattern holding them back",
    "personality_hints": ["trait1", "trait2", "trait3"],
    "personality_traits_weighted": {{
        "trait_name": confidence_score_0_to_1,
        "another_trait": confidence_score_0_to_1
    }},
    "thinking_style": "How they approach problems (analytical/intuitive/experimental/etc)",
    "learning_preferences": {{
        "prefers_questions_over_answers": initial_estimate_0_to_1,
        "responds_to_encouragement": initial_estimate_0_to_1,
        "needs_logical_structure": initial_estimate_0_to_1,
        "values_autonomy": initial_estimate_0_to_1
    }},
    "summary": "A brief summary of what you learned about the user"
}}

Be specific and use the user's own words when possible.
For personality_traits_weighted, include 5-8 traits with confidence scores.
For learning_preferences, provide initial estimates based on conversation style."""


def get_question_by_step(step: int) -> dict:
    """Get onboarding question by step number"""
    for q in ONBOARDING_QUESTIONS:
        if q["step"] == step:
            return q
    return ONBOARDING_QUESTIONS[0]  # Default to first question


def generate_follow_up_prompt(step: int, user_response: str, conversation_history: str) -> str:
    """Generate a Socratic follow-up question"""
    question_data = get_question_by_step(step)

    prompt = f"""{ONBOARDING_SYSTEM_PROMPT}

Current Question Purpose: {question_data["purpose"]}

Conversation So Far:
{conversation_history}

User's Latest Response: {user_response}

Your task:
1. If the response is clear and complete, acknowledge it warmly
2. If the response is vague or superficial, ask a clarifying follow-up question
3. If ready, move to the next question naturally

Generate a natural, conversational response that either:
- Asks a follow-up question to dig deeper (if needed)
- Acknowledges and transitions to the next question (if response was good)

Keep it concise (2-3 sentences max). Be warm and encouraging."""

    return prompt
