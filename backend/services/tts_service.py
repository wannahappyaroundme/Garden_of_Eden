"""
Text-to-Speech Service using Edge TTS
FREE and unlimited, supports high-quality Korean voices
"""
import os
import edge_tts
from pathlib import Path
import base64
from typing import Optional

from utils.logger import get_logger
from utils.constants import PersonaType, TTS_VOICES

logger = get_logger(__name__)


class TTSService:
    """Service for text-to-speech using Edge TTS"""

    def __init__(self):
        """Initialize TTS service"""
        logger.info("Edge TTS service initialized")

    async def generate_speech(
        self,
        text: str,
        persona: PersonaType,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate speech from text

        Args:
            text: Text to convert to speech
            persona: Adam or Eve (determines voice)
            output_path: Optional path to save audio file. If None, uses temp path

        Returns:
            Path to generated audio file or None if error
        """
        try:
            # Select voice based on persona
            voice_name = TTS_VOICES[persona]

            # Generate output path if not provided
            if output_path is None:
                output_dir = Path("temp_audio")
                output_dir.mkdir(exist_ok=True)
                import uuid
                output_path = str(output_dir / f"tts_{uuid.uuid4()}.mp3")

            logger.info(f"Generating TTS with {persona.value} voice: {voice_name}")

            # Generate speech
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(output_path)

            logger.info(f"TTS generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
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
        try:
            voices = await edge_tts.list_voices()
            korean_voices = [v for v in voices if v['Locale'].startswith('ko-')]

            logger.info(f"Found {len(korean_voices)} Korean voices")
            return korean_voices

        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []
