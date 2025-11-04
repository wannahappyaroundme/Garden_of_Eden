"""
Text-to-Speech Service using Google TTS (gTTS)
FREE and unlimited, supports high-quality Korean voices
"""
import os
from gtts import gTTS
from pathlib import Path
import base64
from typing import Optional
import asyncio

from utils.logger import get_logger
from utils.constants import PersonaType

logger = get_logger(__name__)

# Voice mapping for personas
# gTTS doesn't have different voice options for Korean, but we can use different speeds
GTTS_VOICES = {
    PersonaType.ADAM: {"lang": "ko", "slow": False},  # Normal speed for Adam
    PersonaType.EVE: {"lang": "ko", "slow": False}     # Normal speed for Eve
}


class TTSService:
    """Service for text-to-speech using Google TTS"""

    def __init__(self):
        """Initialize TTS service"""
        logger.info("Google TTS service initialized")

    async def generate_speech(
        self,
        text: str,
        persona: PersonaType,
        output_path: Optional[str] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate speech from text using Google TTS

        Args:
            text: Text to convert to speech
            persona: Adam or Eve (determines voice settings)
            output_path: Optional path to save audio file. If None, uses temp path
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Path to generated audio file or None if error
        """
        # Select voice settings based on persona
        voice_config = GTTS_VOICES.get(persona, GTTS_VOICES[PersonaType.ADAM])

        # Generate output path if not provided
        if output_path is None:
            output_dir = Path("temp_audio")
            output_dir.mkdir(exist_ok=True)
            import uuid
            output_path = str(output_dir / f"tts_{uuid.uuid4()}.mp3")

        logger.info(f"Generating TTS with {persona.value} voice using Google TTS")

        # Retry logic for gTTS (network requests can fail)
        for attempt in range(max_retries):
            try:
                # Generate speech (gTTS is sync, so we run it in executor)
                def _generate_tts():
                    tts = gTTS(text=text, lang=voice_config["lang"], slow=voice_config["slow"])
                    tts.save(output_path)

                # Run blocking call in executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, _generate_tts)

                logger.info(f"✅ TTS generated successfully: {output_path}")
                return output_path

            except Exception as e:
                if attempt < max_retries - 1:
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
        persona: PersonaType
    ) -> Optional[str]:
        """
        Generate speech and return as base64 string

        Args:
            text: Text to convert to speech
            persona: Adam or Eve

        Returns:
            Base64 encoded audio or None if error
        """
        try:
            # Generate audio file first
            audio_path = await self.generate_speech(text, persona)

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
        """Get list of available Korean voices"""
        # gTTS only has one Korean voice
        return [
            {
                "Name": "Google TTS Korean",
                "Locale": "ko-KR",
                "Gender": "Neutral"
            }
        ]
