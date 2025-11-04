"""
Speech-to-Text Service using Groq Whisper Large v3
FREE tier: 14,400 requests/day
"""
import os
from typing import Optional
from groq import Groq
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


class STTService:
    """Service for speech-to-text transcription using Groq Whisper"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize STT service"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=self.api_key)

        # Test if audio attribute exists
        if not hasattr(self.client, 'audio'):
            logger.warning("Groq client missing 'audio' attribute - using direct API")

        logger.info("Groq Whisper STT service initialized")

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: str = "ko"  # Korean by default
    ) -> Optional[str]:
        """
        Transcribe audio file to text

        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Language code (ko for Korean)

        Returns:
            Transcribed text or None if error
        """
        try:
            # Check if file exists
            if not Path(audio_file_path).exists():
                logger.error(f"Audio file not found: {audio_file_path}")
                return None

            # Open and transcribe
            with open(audio_file_path, "rb") as audio_file:
                logger.info(f"Transcribing audio file: {audio_file_path}")

                transcription = self.client.audio.transcriptions.create(
                    file=(audio_file_path, audio_file),
                    model="whisper-large-v3-turbo",
                    language=language,
                    response_format="text",
                    temperature=0.0  # More deterministic
                )

                text = transcription.strip()

                logger.info(f"Transcription successful: {text[:100]}...")
                return text

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.mp3",
        language: str = "ko"
    ) -> Optional[str]:
        """
        Transcribe audio from bytes (for direct upload)

        Args:
            audio_bytes: Audio file as bytes
            filename: Filename (for MIME type detection)
            language: Language code

        Returns:
            Transcribed text or None if error
        """
        try:
            logger.info(f"Transcribing audio bytes: {len(audio_bytes)} bytes")

            # Create file-like object
            from io import BytesIO
            audio_file = BytesIO(audio_bytes)
            audio_file.name = filename

            transcription = self.client.audio.transcriptions.create(
                file=(filename, audio_file),
                model="whisper-large-v3",
                language=language,
                response_format="text",
                temperature=0.0
            )

            text = transcription.strip()

            logger.info(f"Transcription successful: {text[:100]}...")
            return text

        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {e}")
            return None
