"""
Text-to-Speech Service using Edge TTS
FREE, high-quality neural voices with Adam/Eve persona distinction
"""
import os
import edge_tts
from pathlib import Path
import base64
from typing import Optional
import asyncio

from utils.logger import get_logger
from utils.constants import PersonaType

logger = get_logger(__name__)

# Voice mapping for personas using Microsoft Edge Neural Voices
# Adam: Masculine voice (InJoon)
# Eve: Feminine voice (SunHi)
EDGE_TTS_VOICES = {
    PersonaType.ADAM: "ko-KR-InJoonNeural",  # Male voice for Adam
    PersonaType.EVE: "ko-KR-SunHiNeural"      # Female voice for Eve
}


class TTSService:
    """Service for text-to-speech using Microsoft Edge TTS (Neural Voices)"""

    def __init__(self):
        """Initialize TTS service"""
        logger.info("Edge TTS service initialized (Neural Korean voices)")

    async def generate_speech(
        self,
        text: str,
        persona: PersonaType,
        output_path: Optional[str] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate speech from text using Edge TTS neural voices

        Args:
            text: Text to convert to speech
            persona: Adam or Eve (determines voice - masculine vs feminine)
            output_path: Optional path to save audio file. If None, uses temp path
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Path to generated audio file or None if error
        """
        # Select voice based on persona
        voice = EDGE_TTS_VOICES.get(persona, EDGE_TTS_VOICES[PersonaType.ADAM])

        # Generate output path if not provided
        if output_path is None:
            output_dir = Path("temp_audio")
            output_dir.mkdir(exist_ok=True)
            import uuid
            output_path = str(output_dir / f"tts_{uuid.uuid4()}.mp3")

        logger.info(f"Generating TTS with {persona.value} voice ({voice}) using Edge TTS")

        # Retry logic for network requests
        for attempt in range(max_retries):
            try:
                # Create Edge TTS communicator
                communicate = edge_tts.Communicate(text, voice)

                # Generate and save audio
                await communicate.save(output_path)

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

    async def generate_speech_stream(
        self,
        text: str,
        persona: PersonaType
    ):
        """
        Generate speech as a stream (yields audio chunks)

        Args:
            text: Text to convert to speech
            persona: Adam or Eve

        Yields:
            Audio data chunks
        """
        # Select voice based on persona
        voice = EDGE_TTS_VOICES.get(persona, EDGE_TTS_VOICES[PersonaType.ADAM])

        logger.info(f"Streaming TTS with {persona.value} voice ({voice})")

        try:
            # Create Edge TTS communicator
            communicate = edge_tts.Communicate(text, voice)

            # Stream audio chunks
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]

        except Exception as e:
            logger.error(f"Error streaming TTS: {e}")

    async def get_available_voices(self) -> list:
        """Get list of available Korean voices"""
        return [
            {
                "Name": "InJoon (Adam)",
                "Voice": "ko-KR-InJoonNeural",
                "Locale": "ko-KR",
                "Gender": "Male",
                "Persona": "Adam"
            },
            {
                "Name": "SunHi (Eve)",
                "Voice": "ko-KR-SunHiNeural",
                "Locale": "ko-KR",
                "Gender": "Female",
                "Persona": "Eve"
            }
        ]
