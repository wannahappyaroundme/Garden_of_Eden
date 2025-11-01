"""
Learning Analysis Prompt for Profile Updates
Used by ProfileLearningService to extract insights from conversations
"""

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

Analysis Guidelines:
- Be specific about evidence (quote exact phrases)
- Confidence should reflect strength of evidence
- For reinforced traits, provide NEW evidence (not already in profile)
- Emotional state should match the user's tone and word choice
- Topic alignment: 1.0 = perfectly aligned, 0.0 = completely unrelated

Output Format (JSON):
{{
  "discovered_traits": [
    {{
      "name": "trait_name",
      "evidence": "what they said/did that shows this",
      "confidence": 0.0-1.0
    }}
  ],
  "reinforced_traits": [
    {{
      "name": "existing_trait_name",
      "evidence": "new evidence supporting this trait"
    }}
  ],
  "emotional_state": {{
    "state": "anxious|excited|frustrated|calm|stressed|happy|sad|confused",
    "trigger": "what caused this emotion",
    "intensity": 0.0-1.0
  }},
  "main_topic": "topic of conversation",
  "topic_alignment": 0.0-1.0,
  "goal_modification_detected": true|false,
  "new_goal_hint": "if detected, what the new goal might be"
}}

IMPORTANT: Return ONLY valid JSON. No explanations before or after.
"""

def build_learning_analysis_prompt(
    current_profile_summary: str,
    user_message: str,
    ai_response: str
) -> str:
    """Build learning analysis prompt"""

    return LEARNING_ANALYSIS_PROMPT.format(
        current_profile_summary=current_profile_summary,
        user_message=user_message,
        ai_response=ai_response
    )
