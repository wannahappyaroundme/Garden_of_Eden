"""
Onboarding V3 Prompts - Personality Profiling + Goal Discovery
Redesigned system with structured personality assessment
"""

# New onboarding questions combining personality profiling with goal discovery
ONBOARDING_V3_QUESTIONS = [
    {
        "step": 1,
        "type": "personal_info",
        "question_kr": "안녕하세요! 저는 당신의 AI 멘토입니다. 먼저, 이름을 알려주시겠어요?",
        "question_en": "Hello! I'm your AI mentor. First, may I know your name?",
        "purpose": "Collect user's name for personalization",
        "field": "name",
        "validation": "required"
    },
    {
        "step": 2,
        "type": "multiple_choice",
        "question_kr": "{name}님, 반갑습니다! 문제를 해결할 때, 당신은 어떤 스타일인가요?",
        "question_en": "Nice to meet you, {name}! When solving problems, what's your style?",
        "purpose": "Identify thinking style and problem-solving approach",
        "field": "thinking_style",
        "options": [
            {
                "value": "analytical",
                "label_kr": "분석적 - 데이터와 논리로 접근해요",
                "label_en": "Analytical - I approach with data and logic",
                "traits": ["analytical", "detail_oriented", "systematic"],
                "learning_prefs": {"needs_logical_structure": 0.8, "prefers_questions_over_answers": 0.6}
            },
            {
                "value": "intuitive",
                "label_kr": "직관적 - 감각과 경험으로 판단해요",
                "label_en": "Intuitive - I judge by feel and experience",
                "traits": ["intuitive", "creative", "flexible"],
                "learning_prefs": {"needs_logical_structure": 0.3, "prefers_questions_over_answers": 0.5}
            },
            {
                "value": "experimental",
                "label_kr": "실험적 - 일단 해보면서 배워요",
                "label_en": "Experimental - I learn by trying things out",
                "traits": ["experimental", "action_oriented", "pragmatic"],
                "learning_prefs": {"values_autonomy": 0.8, "prefers_questions_over_answers": 0.4}
            },
            {
                "value": "collaborative",
                "label_kr": "협력적 - 다른 사람들과 함께 고민해요",
                "label_en": "Collaborative - I think through with others",
                "traits": ["collaborative", "social", "empathetic"],
                "learning_prefs": {"responds_to_encouragement": 0.8, "prefers_questions_over_answers": 0.7}
            }
        ]
    },
    {
        "step": 3,
        "type": "multiple_choice",
        "question_kr": "동기부여에 대해 물어볼게요. 당신이 가장 힘을 받는 순간은 언제인가요?",
        "question_en": "About motivation - when do you feel most energized?",
        "purpose": "Understand motivation drivers and energy sources",
        "field": "motivation_style",
        "options": [
            {
                "value": "achievement",
                "label_kr": "성취 - 목표를 달성했을 때",
                "label_en": "Achievement - When I reach goals",
                "traits": ["goal_oriented", "ambitious", "persistent"],
                "learning_prefs": {"prefers_questions_over_answers": 0.6, "values_autonomy": 0.7}
            },
            {
                "value": "growth",
                "label_kr": "성장 - 새로운 것을 배웠을 때",
                "label_en": "Growth - When I learn something new",
                "traits": ["curious", "growth_mindset", "adaptable"],
                "learning_prefs": {"prefers_questions_over_answers": 0.8, "responds_to_encouragement": 0.6}
            },
            {
                "value": "impact",
                "label_kr": "영향력 - 다른 사람에게 도움이 되었을 때",
                "label_en": "Impact - When I help others",
                "traits": ["empathetic", "service_oriented", "altruistic"],
                "learning_prefs": {"responds_to_encouragement": 0.8, "prefers_questions_over_answers": 0.5}
            },
            {
                "value": "autonomy",
                "label_kr": "자율성 - 내 방식대로 할 수 있을 때",
                "label_en": "Autonomy - When I can do things my way",
                "traits": ["independent", "self_directed", "creative"],
                "learning_prefs": {"values_autonomy": 0.9, "prefers_questions_over_answers": 0.4}
            }
        ]
    },
    {
        "step": 4,
        "type": "multiple_choice",
        "question_kr": "어려운 상황에 직면했을 때, 당신은 주로 어떻게 반응하나요?",
        "question_en": "When facing difficulties, how do you typically respond?",
        "purpose": "Assess resilience patterns and coping mechanisms",
        "field": "resilience_style",
        "options": [
            {
                "value": "problem_solver",
                "label_kr": "문제 해결 - 즉시 해결책을 찾아요",
                "label_en": "Problem Solver - I immediately look for solutions",
                "traits": ["resilient", "proactive", "solution_focused"],
                "pitfall_tendency": "rushing_without_reflection"
            },
            {
                "value": "reflector",
                "label_kr": "성찰 - 먼저 상황을 깊이 생각해요",
                "label_en": "Reflector - I think deeply about the situation first",
                "traits": ["thoughtful", "introspective", "strategic"],
                "pitfall_tendency": "over_analysis_paralysis"
            },
            {
                "value": "seeker",
                "label_kr": "조언 구함 - 다른 사람의 의견을 들어요",
                "label_en": "Seeker - I ask for others' opinions",
                "traits": ["humble", "collaborative", "open_minded"],
                "pitfall_tendency": "over_reliance_on_others"
            },
            {
                "value": "adapter",
                "label_kr": "적응 - 상황을 받아들이고 조정해요",
                "label_en": "Adapter - I accept and adjust to the situation",
                "traits": ["flexible", "accepting", "pragmatic"],
                "pitfall_tendency": "avoiding_hard_decisions"
            }
        ]
    },
    {
        "step": 5,
        "type": "open_ended",
        "question_kr": "이제 본질적인 질문을 드릴게요. 요즘 당신에게 가장 중요한 한 가지는 무엇인가요? 이루고 싶은 목표나 집중하고 싶은 것을 자유롭게 말씀해주세요.",
        "question_en": "Now for the essential question. What's the ONE thing that matters most to you right now? Feel free to share your goal or what you want to focus on.",
        "purpose": "Discover user's One Thing - primary goal",
        "field": "one_thing",
        "follow_up_prompts": [
            "그것이 왜 지금 중요한가요?",
            "더 구체적으로 말씀해주실 수 있나요?",
            "그것을 달성했을 때 당신의 삶은 어떻게 변할까요?"
        ]
    },
    {
        "step": 6,
        "type": "open_ended",
        "question_kr": "마지막 질문입니다. 그 목표를 향해 나아가는 데 있어서 가장 큰 장애물이나 어려움은 무엇인가요?",
        "question_en": "Final question. What's the biggest obstacle or challenge preventing you from moving toward that goal?",
        "purpose": "Identify core pitfall/obstacle",
        "field": "core_pitfall",
        "follow_up_prompts": [
            "그 장애물은 언제부터 있었나요?",
            "이전에 극복하려고 시도한 적이 있나요?",
            "무엇이 그것을 어렵게 만드나요?"
        ]
    }
]


# Adaptive persona configuration - unified for Adam and Eve
ADAPTIVE_PERSONA_CONFIG = {
    "persona_modes": {
        "mentor": {
            "name_kr": "멘토",
            "name_en": "Mentor",
            "description": "Socratic questioner, challenges thinking, goal-focused",
            "characteristics": {
                "questioning_ratio": 0.7,  # 70% questions vs statements
                "directness": 0.8,
                "empathy": 0.5,
                "challenge_level": 0.7
            },
            "when_to_use": "Initial phase, when user needs structure and direction"
        },
        "supporter": {
            "name_kr": "지지자",
            "name_en": "Supporter",
            "description": "Encouraging, validates feelings, celebrates progress",
            "characteristics": {
                "questioning_ratio": 0.4,
                "directness": 0.5,
                "empathy": 0.9,
                "challenge_level": 0.3
            },
            "when_to_use": "When user shows vulnerability, needs encouragement"
        },
        "friend": {
            "name_kr": "친구",
            "name_en": "Friend",
            "description": "Casual, relatable, shares experiences, mutual growth",
            "characteristics": {
                "questioning_ratio": 0.5,
                "directness": 0.6,
                "empathy": 0.8,
                "challenge_level": 0.5
            },
            "when_to_use": "After trust is built, comfortable sharing"
        }
    },

    "evolution_triggers": {
        "mentor_to_supporter": {
            "conditions": [
                "user_shows_vulnerability",
                "user_expresses_frustration",
                "user_shares_failure",
                "consecutive_setbacks >= 2"
            ],
            "interaction_count_min": 5
        },
        "supporter_to_friend": {
            "conditions": [
                "user_shares_personal_story",
                "user_asks_about_ai_opinion",
                "positive_interaction_streak >= 5",
                "trust_score >= 0.7"
            ],
            "interaction_count_min": 15
        },
        "friend_to_mentor": {
            "conditions": [
                "user_asks_for_direction",
                "user_is_off_track",
                "pitfall_detected",
                "goal_progress_stagnant"
            ],
            "interaction_count_min": 10
        }
    },

    "voice_differences": {
        "adam": {
            "voice_type": "male",
            "tone": "calm, steady, reassuring",
            "personality_hints": "더 차분하고 논리적인 접근"
        },
        "eve": {
            "voice_type": "female",
            "tone": "warm, energetic, encouraging",
            "personality_hints": "더 따뜻하고 공감적인 접근"
        }
    }
}


# Profile extraction prompt for V3 onboarding
EXTRACTION_V3_PROMPT = """Based on the personality profiling onboarding, extract comprehensive user profile:

User Responses:
{responses}

Extract and return in JSON format:
{{
    "personal_info": {{
        "name": "user's name",
        "preferred_language": "ko"
    }},
    "one_thing": "user's primary goal (from step 5)",
    "core_motivation": "deeper why behind their goal",
    "core_pitfall": "main obstacle (from step 6)",

    "personality_traits_weighted": {{
        "trait_name": confidence_0_to_1,
        "another_trait": confidence_0_to_1
    }},

    "thinking_style": "analytical|intuitive|experimental|collaborative",
    "motivation_style": "achievement|growth|impact|autonomy",
    "resilience_style": "problem_solver|reflector|seeker|adapter",
    "pitfall_tendency": "identified_from_resilience_style",

    "learning_preferences": {{
        "prefers_questions_over_answers": 0.0_to_1.0,
        "responds_to_encouragement": 0.0_to_1.0,
        "needs_logical_structure": 0.0_to_1.0,
        "values_autonomy": 0.0_to_1.0,
        "growth_mindset_strength": 0.0_to_1.0
    }},

    "initial_persona_mode": "mentor|supporter|friend",
    "persona_evolution_readiness": 0.0_to_1.0,

    "summary": "comprehensive summary of what you learned"
}}

Use the trait mappings from the multiple choice options.
Calculate learning preferences by combining selections from steps 2, 3, 4.
Determine initial_persona_mode based on user's responses and needs."""


def get_question_v3(step: int, context: dict = None) -> dict:
    """
    Get onboarding V3 question by step

    Args:
        step: Question step number (1-6)
        context: Optional context like user's name for personalization

    Returns:
        Question dict with all metadata
    """
    for q in ONBOARDING_V3_QUESTIONS:
        if q["step"] == step:
            question = q.copy()

            # Personalize question with context
            if context and "name" in context:
                question["question_kr"] = question["question_kr"].format(name=context["name"])
                question["question_en"] = question["question_en"].format(name=context["name"])

            return question

    return ONBOARDING_V3_QUESTIONS[0]


def calculate_learning_preferences(responses: dict) -> dict:
    """
    Calculate learning preferences from personality profiling responses

    Args:
        responses: User's responses to multiple choice questions

    Returns:
        Learning preferences dict with 0.0-1.0 scores
    """
    preferences = {
        "prefers_questions_over_answers": 0.5,
        "responds_to_encouragement": 0.5,
        "needs_logical_structure": 0.5,
        "values_autonomy": 0.5,
        "growth_mindset_strength": 0.6
    }

    # Combine preferences from multiple selections
    for step, response in responses.items():
        if isinstance(response, dict) and "learning_prefs" in response:
            for pref, value in response["learning_prefs"].items():
                if pref in preferences:
                    # Average with existing value
                    preferences[pref] = (preferences[pref] + value) / 2

    return preferences


def determine_initial_persona_mode(responses: dict, learning_prefs: dict) -> str:
    """
    Determine initial persona mode based on user profile

    Args:
        responses: User's onboarding responses
        learning_prefs: Calculated learning preferences

    Returns:
        "mentor", "supporter", or "friend"
    """
    # Default to mentor for most users
    if learning_prefs.get("prefers_questions_over_answers", 0.5) > 0.6:
        return "mentor"

    # Supporter for those who respond to encouragement
    if learning_prefs.get("responds_to_encouragement", 0.5) > 0.7:
        return "supporter"

    # Friend for highly autonomous users
    if learning_prefs.get("values_autonomy", 0.5) > 0.8:
        return "friend"

    return "mentor"  # Default
