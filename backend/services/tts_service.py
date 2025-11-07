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
# Adam: Masculine voice (Neural2-C)
# Eve: Feminine voice (Neural2-A)
GOOGLE_TTS_VOICES = {
    PersonaType.ADAM: {
        "name": "ko-KR-Neural2-C",  # Male voice for Adam
        "gender": texttospeech.SsmlVoiceGender.MALE
    },
    PersonaType.EVE: {
        "name": "ko-KR-Neural2-A",  # Female voice for Eve
        "gender": texttospeech.SsmlVoiceGender.FEMALE
    }
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

    async def generate_speech(
        self,
        text: str,
        persona: PersonaType,
        output_path: Optional[str] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate speech from text using Google Cloud TTS neural voices

        Args:
            text: Text to convert to speech
            persona: Adam or Eve (determines voice - masculine vs feminine)
            output_path: Optional path to save audio file. If None, uses temp path
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Path to generated audio file or None if error
        """
        if not self.client:
            logger.error("TTS client not initialized")
            return None

        # Select voice based on persona
        voice_config = GOOGLE_TTS_VOICES.get(persona, GOOGLE_TTS_VOICES[PersonaType.ADAM])

        # Generate output path if not provided
        if output_path is None:
            output_dir = Path("temp_audio")
            output_dir.mkdir(exist_ok=True)
            import uuid
            output_path = str(output_dir / f"tts_{uuid.uuid4()}.mp3")

        logger.info(f"Generating TTS with {persona.value} voice ({voice_config['name']}) using Google Cloud TTS")

        # Retry logic for network requests
        for attempt in range(max_retries):
            try:
                # Set the text input
                synthesis_input = texttospeech.SynthesisInput(text=text)

                # Build the voice request
                voice = texttospeech.VoiceSelectionParams(
                    language_code="ko-KR",
                    name=voice_config["name"],
                    ssml_gender=voice_config["gender"]
                )

                # Select the audio file type
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,  # Normal speed
                    pitch=0.0  # Normal pitch
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
        return [
            {
                "Name": "Neural2-C (Adam)",
                "Voice": "ko-KR-Neural2-C",
                "Locale": "ko-KR",
                "Gender": "Male",
                "Persona": "Adam"
            },
            {
                "Name": "Neural2-A (Eve)",
                "Voice": "ko-KR-Neural2-A",
                "Locale": "ko-KR",
                "Gender": "Female",
                "Persona": "Eve"
            }
        ]
