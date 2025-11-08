"""
Text-to-Speech Service using Google Cloud TTS
High-quality neural voices with Adam/Eve persona distinction
"""
import os
from google.cloud import texttospeech
from pathlib import Path
import base64
from typing import Optional

from utils.logger import get_logger
from utils.constants import PersonaType

logger = get_logger(__name__)

# Voice mapping for personas using Google Cloud Neural2 Voices
# Supports both Korean (ko-KR) and English (en-US)
# Default language: Korean

# Korean Voices
GOOGLE_TTS_VOICES_KO = {
    PersonaType.ADAM: {
        "name": "ko-KR-Neural2-C",  # Male voice for Adam (deep, stable)
        "gender": texttospeech.SsmlVoiceGender.MALE,
        "language_code": "ko-KR"
    },
    PersonaType.EVE: {
        "name": "ko-KR-Neural2-A",  # Female voice for Eve (default: bright, friendly)
        "gender": texttospeech.SsmlVoiceGender.FEMALE,
        "language_code": "ko-KR"
    }
}

# English Voices (Premium Neural2 - Higher Quality)
GOOGLE_TTS_VOICES_EN = {
    PersonaType.ADAM: {
        "name": "en-US-Neural2-D",  # Male voice for Adam (deep, authoritative)
        "gender": texttospeech.SsmlVoiceGender.MALE,
        "language_code": "en-US"
    },
    PersonaType.EVE: {
        "name": "en-US-Neural2-F",  # Female voice for Eve (natural, conversational)
        "gender": texttospeech.SsmlVoiceGender.FEMALE,
        "language_code": "en-US"
    }
}

# Default to Korean for backward compatibility
GOOGLE_TTS_VOICES = GOOGLE_TTS_VOICES_KO

# Korean Eve voice variants
EVE_VOICE_VARIANTS_KO = {
    "Neural2-A": "ko-KR-Neural2-A",  # Bright & Friendly
    "Neural2-B": "ko-KR-Neural2-B",  # Soft & Calm
}

# English voice variants (both Adam and Eve)
VOICE_VARIANTS_EN = {
    # Adam variants
    "Neural2-D": "en-US-Neural2-D",  # Deep, authoritative (default)
    "Neural2-J": "en-US-Neural2-J",  # Warm, friendly
    # Eve variants
    "Neural2-F": "en-US-Neural2-F",  # Natural, conversational (default)
    "Neural2-G": "en-US-Neural2-G",  # Professional, warm
    "Neural2-C": "en-US-Neural2-C",  # Clear, energetic
}


class TTSService:
    """Service for text-to-speech using Google Cloud TTS (Neural2 Voices)"""

    def __init__(self):
        """Initialize TTS service"""
        try:
            # Initialize Google Cloud TTS client
            self.client = texttospeech.TextToSpeechClient()
            logger.info("✅ Google Cloud TTS service initialized (Neural2 Korean voices)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Cloud TTS: {e}")
            self.client = None

    def _detect_language(self, text: str) -> str:
        """Detect if text is primarily Korean or English"""
        korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7a3')  # Korean syllables
        total_chars = len([c for c in text if c.isalpha()])

        if total_chars == 0:
            return "ko-KR"  # Default to Korean

        korean_ratio = korean_chars / total_chars
        return "ko-KR" if korean_ratio > 0.3 else "en-US"

    async def generate_speech(
        self,
        text: str,
        persona: PersonaType,
        output_path: Optional[str] = None,
        max_retries: int = 3,
        voice_variant: Optional[str] = None,
        language: Optional[str] = None  # NEW: Allow explicit language override
    ) -> Optional[str]:
        """
        Generate speech from text using Google Cloud TTS neural voices
        Automatically detects language (Korean/English) and uses appropriate voice

        Args:
            text: Text to convert to speech
            persona: Adam or Eve (determines voice - masculine vs feminine)
            output_path: Optional path to save audio file. If None, uses temp path
            max_retries: Maximum number of retry attempts (default: 3)
            voice_variant: Optional voice variant code (e.g., "Neural2-A", "Neural2-B" for Korean Eve)
            language: Optional language override ("ko-KR" or "en-US"). If None, auto-detects.

        Returns:
            Path to generated audio file or None if error
        """
        if not self.client:
            logger.error("TTS client not initialized")
            return None

        # Detect language if not explicitly provided
        detected_lang = language if language else self._detect_language(text)

        # Select voice map based on language
        voice_map = GOOGLE_TTS_VOICES_EN if detected_lang == "en-US" else GOOGLE_TTS_VOICES_KO
        voice_config = voice_map.get(persona, voice_map[PersonaType.ADAM]).copy()

        # Override with voice variant if provided
        if voice_variant:
            if detected_lang == "ko-KR" and persona == PersonaType.EVE and voice_variant in EVE_VOICE_VARIANTS_KO:
                voice_config["name"] = EVE_VOICE_VARIANTS_KO[voice_variant]
                logger.info(f"Using Korean Eve voice variant: {voice_variant} ({voice_config['name']})")
            elif detected_lang == "en-US" and voice_variant in VOICE_VARIANTS_EN:
                voice_config["name"] = VOICE_VARIANTS_EN[voice_variant]
                logger.info(f"Using English voice variant: {voice_variant} ({voice_config['name']})")

        # Generate output path if not provided
        if output_path is None:
            output_dir = Path("temp_audio")
            output_dir.mkdir(exist_ok=True)
            import uuid
            output_path = str(output_dir / f"tts_{uuid.uuid4()}.mp3")

        logger.info(f"Generating TTS with {persona.value} voice ({voice_config['name']}) - Language: {detected_lang}")

        # Retry logic for network requests
        for attempt in range(max_retries):
            try:
                # Set the text input
                synthesis_input = texttospeech.SynthesisInput(text=text)

                # Build the voice request
                voice = texttospeech.VoiceSelectionParams(
                    language_code=voice_config["language_code"],  # Use detected language
                    name=voice_config["name"],
                    ssml_gender=voice_config["gender"]
                )

                # Select the audio file type with natural-sounding settings
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=0.95,  # Slightly slower for more natural feel
                    pitch=-2.0,  # Slightly lower pitch for warmth
                    effects_profile_id=["small-bluetooth-speaker-class-device"]  # Optimized for mobile
                )

                # Perform the text-to-speech request
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )

                # Write the response to the output file
                with open(output_path, "wb") as out:
                    out.write(response.audio_content)

                logger.info(f"✅ TTS generated successfully: {output_path}")
                return output_path

            except Exception as e:
                if attempt < max_retries - 1:
                    import asyncio
                    wait_time = (attempt + 1) * 2  # 2s, 4s, 6s...
                    logger.warning(f"⚠️ TTS attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ TTS failed after {max_retries} attempts: {e}")
                    return None

        return None

    async def generate_speech_base64(
        self,
        text: str,
        persona: PersonaType,
        voice_variant: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate speech and return as base64 string

        Args:
            text: Text to convert to speech
            persona: Adam or Eve
            voice_variant: Optional voice variant code for Eve

        Returns:
            Base64 encoded audio or None if error
        """
        try:
            # Generate audio file first
            audio_path = await self.generate_speech(text, persona, voice_variant=voice_variant)

            if not audio_path:
                return None

            # Read and encode
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

            # Clean up temp file
            try:
                os.remove(audio_path)
            except:
                pass

            logger.info(f"Generated base64 TTS ({len(audio_base64)} chars)")
            return audio_base64

        except Exception as e:
            logger.error(f"Error generating base64 TTS: {e}")
            return None

    async def get_available_voices(self) -> list:
        """Get list of available voices (Korean and English)"""
        return [
            # Korean Voices
            {
                "Name": "Adam (Deep, Stable) - Korean",
                "Voice": "ko-KR-Neural2-C",
                "VoiceCode": "Neural2-C",
                "Locale": "ko-KR",
                "Gender": "Male",
                "Persona": "Adam",
                "Description": "Masculine voice with deep and stable tone",
                "Language": "Korean"
            },
            {
                "Name": "Eve - Bright & Friendly - Korean",
                "Voice": "ko-KR-Neural2-A",
                "VoiceCode": "Neural2-A",
                "Locale": "ko-KR",
                "Gender": "Female",
                "Persona": "Eve",
                "Description": "Energetic and warm tone, perfect for encouragement",
                "Language": "Korean"
            },
            {
                "Name": "Eve - Soft & Calm - Korean",
                "Voice": "ko-KR-Neural2-B",
                "VoiceCode": "Neural2-B",
                "Locale": "ko-KR",
                "Gender": "Female",
                "Persona": "Eve",
                "Description": "Gentle and soothing tone, ideal for reflection",
                "Language": "Korean"
            },
            # English Voices
            {
                "Name": "Adam (Deep, Authoritative) - English",
                "Voice": "en-US-Neural2-D",
                "VoiceCode": "Neural2-D",
                "Locale": "en-US",
                "Gender": "Male",
                "Persona": "Adam",
                "Description": "Deep, authoritative voice - Professional and commanding",
                "Language": "English"
            },
            {
                "Name": "Adam (Warm, Friendly) - English",
                "Voice": "en-US-Neural2-J",
                "VoiceCode": "Neural2-J",
                "Locale": "en-US",
                "Gender": "Male",
                "Persona": "Adam",
                "Description": "Warm, friendly tone - Approachable and supportive",
                "Language": "English"
            },
            {
                "Name": "Eve (Natural, Conversational) - English",
                "Voice": "en-US-Neural2-F",
                "VoiceCode": "Neural2-F",
                "Locale": "en-US",
                "Gender": "Female",
                "Persona": "Eve",
                "Description": "Natural, conversational tone - Relatable and engaging",
                "Language": "English"
            },
            {
                "Name": "Eve (Professional, Warm) - English",
                "Voice": "en-US-Neural2-G",
                "VoiceCode": "Neural2-G",
                "Locale": "en-US",
                "Gender": "Female",
                "Persona": "Eve",
                "Description": "Professional, warm voice - Confident and reassuring",
                "Language": "English"
            },
            {
                "Name": "Eve (Clear, Energetic) - English",
                "Voice": "en-US-Neural2-C",
                "VoiceCode": "Neural2-C",
                "Locale": "en-US",
                "Gender": "Female",
                "Persona": "Eve",
                "Description": "Clear, energetic tone - Bright and motivating",
                "Language": "English"
            }
        ]
