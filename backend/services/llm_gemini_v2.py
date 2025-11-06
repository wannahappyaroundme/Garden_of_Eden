"""
Gemini LLM Service for Project Eden V2
Handles all interactions with Google Gemini 1.5 Flash API
"""
import os
import json
from typing import List, Optional
import google.generativeai as genai
from PIL import Image
import io
import base64

from models.user_profile import UserProfile
from models.conversation import Conversation
from models.api_schemas import ConversationAnalysis, DiscoveredTrait, ReinforcedTrait, EmotionalStateAnalysis
from prompts.master_directive import build_master_directive, build_benevolent_dissent, build_supporter_mode
from prompts.learning_analysis import build_learning_analysis_prompt
from utils.logger import get_logger
from utils.constants import PersonaType

logger = get_logger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        logger.info(f"🔑 Gemini API Key loaded: {self.api_key[:20]}...")
        genai.configure(api_key=self.api_key)

        # Use Gemini Flash (FREE tier model)
        # Reference: https://ai.google.dev/pricing
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Gemini model initialized: gemini-2.5-flash (FREE)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize gemini-2.5-flash: {e}")
            # Try gemini-flash-latest as fallback
            try:
                self.model = genai.GenerativeModel('gemini-flash-latest')
                logger.info("✅ Gemini model initialized: gemini-flash-latest (fallback)")
            except Exception as e2:
                logger.error(f"❌ Failed to initialize fallback model: {e2}")
                raise

        logger.info("Gemini service initialized")

    async def generate_response(
        self,
        user_message: str,
        user_profile: UserProfile,
        persona: PersonaType,
        recent_conversations: List[Conversation],
        camera_frames: Optional[List[Image.Image]] = None,
        pitfall_warning_mode: bool = False,
        pitfall_details: Optional[dict] = None,
        emotional_support_mode: bool = False,
        emotional_details: Optional[dict] = None,
        rag_context: str = "No semantic memory retrieved.",
        web_context: str = "No web search performed.",
        goal_context: str = "No goal tracking info available."
    ) -> str:
        """
        Generate AI response using Master Directive system with RAG, WebSearch, and Goal Tracking

        Args:
            user_message: User's input text
            user_profile: User's profile with Am-muk-ji
            persona: Adam or Eve
            recent_conversations: Recent conversation history
            camera_frames: Optional images from camera
            pitfall_warning_mode: Whether to activate benevolent dissent
            pitfall_details: Details about detected pitfall
            emotional_support_mode: Whether to activate supporter mode
            emotional_details: Details about emotional state
            rag_context: Semantic memory from RAG search
            web_context: Current web information from search
            goal_context: Goal progress tracking information

        Returns:
            AI response text in Korean
        """
        try:
            # Build profile context
            profile_context = user_profile.to_context_string()

            # Build learning preferences context (NEW - for weighted mentor adaptation)
            learning_preferences_context = user_profile.get_learning_preferences_context()

            # Build recent memory
            recent_memory = self._format_recent_conversations(recent_conversations)

            # Build visual context
            visual_context = "No visual input"
            if camera_frames:
                visual_context = f"{len(camera_frames)} camera frames attached (user's current view)"

            # Get persona details
            persona_name = persona.value.capitalize()

            # Get One Thing and Core Pitfall
            one_thing = user_profile.one_thing.value if user_profile.one_thing else "Not set"
            core_pitfall = user_profile.core_pitfall.value if user_profile.core_pitfall else "Not detected yet"
            pitfall_triggers = ", ".join(user_profile.core_pitfall.triggers) if user_profile.core_pitfall else "None"

            detected_topic = pitfall_details.get('detected_topic', 'Unknown') if pitfall_details else 'Unknown'

            # Build mode-specific instructions
            mode_instructions = ""
            if pitfall_warning_mode and pitfall_details:
                mode_instructions = build_benevolent_dissent(
                    user_request=user_message,
                    detected_topic=pitfall_details.get('detected_topic', 'Unknown'),
                    one_thing=one_thing,
                    core_pitfall=core_pitfall,
                    alignment_score=pitfall_details.get('alignment_score', 0.0),
                    persona_name=persona_name
                )
            elif emotional_support_mode and emotional_details:
                mode_instructions = build_supporter_mode(
                    emotional_state=emotional_details.get('state', 'stressed'),
                    emotional_trigger=emotional_details.get('trigger', 'Unknown'),
                    intensity=emotional_details.get('intensity', 0.5),
                    persona_name=persona_name
                )

            # Build complete Master Directive prompt with RAG, WebSearch, and Goal Tracking
            master_directive = build_master_directive(
                user_message=user_message,
                user_profile_context=profile_context,
                learning_preferences_context=learning_preferences_context,
                persona_name=persona_name,
                recent_memory=recent_memory,
                visual_context=visual_context,
                one_thing=one_thing,
                core_pitfall=core_pitfall,
                pitfall_triggers=pitfall_triggers,
                detected_topic=detected_topic,
                mode_specific_instructions=mode_instructions,
                rag_context=rag_context,
                web_context=web_context,
                goal_context=goal_context
            )

            # Prepare content for Gemini
            content_parts = [master_directive]

            # Add images if provided
            if camera_frames:
                for img in camera_frames[:8]:  # Max 8 frames
                    content_parts.append(img)

            # Generate response
            logger.info(f"Generating {persona_name} response (pitfall={pitfall_warning_mode}, support={emotional_support_mode})")
            logger.info(f"📝 Prompt length: {len(master_directive)} chars, Images: {len(camera_frames) if camera_frames else 0}")

            try:
                response = self.model.generate_content(content_parts)
                ai_response = response.text.strip()
                logger.info(f"✅ Generated response: {ai_response[:100]}...")
                return ai_response
            except Exception as gen_error:
                logger.error(f"❌ Gemini API Error: {gen_error}")
                logger.error(f"Error type: {type(gen_error).__name__}")
                raise

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            return "죄송해요, 지금 응답을 생성하는데 문제가 있어요. 다시 한번 말씀해주시겠어요?"

    async def analyze_for_learning(
        self,
        user_message: str,
        ai_response: str,
        current_profile: UserProfile
    ) -> Optional[ConversationAnalysis]:
        """
        Analyze conversation to extract learning insights
        Used by ProfileLearningService

        Args:
            user_message: What user said
            ai_response: What AI responded
            current_profile: Current user profile

        Returns:
            ConversationAnalysis with discovered/reinforced traits, emotions, etc.
        """
        try:
            # Build profile summary
            profile_summary = current_profile.to_context_string()

            # Build learning analysis prompt
            prompt = build_learning_analysis_prompt(
                current_profile_summary=profile_summary,
                user_message=user_message,
                ai_response=ai_response
            )

            # Generate analysis
            logger.info("Analyzing conversation for learning insights...")

            response = self.model.generate_content(prompt)
            analysis_text = response.text.strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

            analysis_dict = json.loads(analysis_text)

            # Convert to ConversationAnalysis object
            analysis = ConversationAnalysis(
                discovered_traits=[
                    DiscoveredTrait(**trait)
                    for trait in analysis_dict.get('discovered_traits', [])
                ],
                reinforced_traits=[
                    ReinforcedTrait(**trait)
                    for trait in analysis_dict.get('reinforced_traits', [])
                ],
                emotional_state=(
                    EmotionalStateAnalysis(**analysis_dict['emotional_state'])
                    if analysis_dict.get('emotional_state')
                    else None
                ),
                main_topic=analysis_dict.get('main_topic'),
                topic_alignment=analysis_dict.get('topic_alignment', 0.0),
                goal_modification_detected=analysis_dict.get('goal_modification_detected', False),
                new_goal_hint=analysis_dict.get('new_goal_hint')
            )

            logger.info(f"Learning analysis complete: {len(analysis.discovered_traits)} new traits, {len(analysis.reinforced_traits)} reinforced")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse learning analysis JSON: {e}")
            logger.debug(f"Response was: {analysis_text}")
            return None
        except Exception as e:
            logger.error(f"Error in learning analysis: {e}")
            return None

    def _format_recent_conversations(self, conversations: List[Conversation]) -> str:
        """Format recent conversations for context"""
        if not conversations:
            return "No recent conversation history."

        lines = ["Recent conversations:"]
        for conv in conversations[-10:]:  # Last 10
            for msg in conv.messages:
                role = "User" if msg.role == "user" else "AI"
                timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M")
                lines.append(f"[{timestamp}] {role}: {msg.content[:100]}...")

        return "\n".join(lines)

    async def generate_text_only_response(
        self,
        prompt: str,
        max_tokens: int = 500
    ) -> str:
        """Generate a simple text-only response without persona or profile context"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7
                }
            )

            # Handle both simple and multi-part responses
            try:
                text = response.text.strip()
            except ValueError:
                # If response.text fails, extract from parts
                text_parts = []
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            text_parts.append(part.text)
                text = "".join(text_parts).strip()

            logger.debug(f"Generated text-only response: {text[:100]}...")
            return text

        except Exception as e:
            logger.error(f"Error generating text-only response: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다."

    async def extract_topic_from_text(self, text: str) -> str:
        """Extract main topic from user's message (for pitfall detection)"""
        try:
            prompt = f"""
Extract the main topic or subject matter from this user message in 2-4 words.
Be specific about what they're asking about.

User message: "{text}"

Return ONLY the topic, nothing else.
Examples:
- "SLAM algorithms"
- "Vue.js learning"
- "Machine learning course"
- "HCI research methods"
"""

            response = self.model.generate_content(prompt)
            topic = response.text.strip()

            logger.debug(f"Extracted topic: {topic}")
            return topic

        except Exception as e:
            logger.error(f"Error extracting topic: {e}")
            return "Unknown topic"
