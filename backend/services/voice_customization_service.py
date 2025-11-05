"""
Voice Customization Service for Project Eden V2
Manage voice settings and persona customization
"""
from typing import Optional, Dict, Any
from datetime import datetime

from services.dynamodb_service_v2 import DynamoDBService
from utils.logger import get_logger

logger = get_logger(__name__)


class VoiceCustomizationService:
    """Service for managing voice and persona customization settings"""

    # Available voice options
    AVAILABLE_VOICES = {
        "default": {"name": "Default", "description": "Standard English voice"},
        "female_gentle": {"name": "Gentle Female", "description": "Soft, caring tone"},
        "male_confident": {"name": "Confident Male", "description": "Clear, assured tone"},
        "neutral_calm": {"name": "Calm Neutral", "description": "Soothing, balanced tone"},
    }

    # Persona traits
    PERSONA_TRAITS = {
        "empathy_level": {"min": 1, "max": 5, "default": 3},
        "directness": {"min": 1, "max": 5, "default": 3},
        "formality": {"min": 1, "max": 5, "default": 2},
        "encouragement": {"min": 1, "max": 5, "default": 4},
    }

    def __init__(self, db_service: DynamoDBService):
        self.db = db_service

    async def get_voice_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's voice customization settings

        Returns:
            {
                "voice_id": "female_gentle",
                "voice_name": "Gentle Female",
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "persona_traits": {
                    "empathy_level": 4,
                    "directness": 2,
                    "formality": 2,
                    "encouragement": 5
                },
                "updated_at": "2025-11-06T..."
            }
        """
        try:
            logger.info(f"Fetching voice settings for user {user_id}")

            # Get user profile (voice settings stored there)
            profile = await self.db.get_user_profile(user_id)

            if not profile:
                logger.warning(f"Profile not found for user {user_id}")
                return self._get_default_settings()

            # Extract voice settings (add to profile if not exists)
            voice_settings = getattr(profile, "voice_settings", None)

            if not voice_settings:
                logger.info(f"No voice settings found, returning defaults for {user_id}")
                return self._get_default_settings()

            return voice_settings

        except Exception as e:
            logger.error(f"Error getting voice settings for {user_id}: {e}")
            return self._get_default_settings()

    async def update_voice_settings(
        self,
        user_id: str,
        voice_id: Optional[str] = None,
        speed: Optional[float] = None,
        pitch: Optional[float] = None,
        volume: Optional[float] = None,
        persona_traits: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Update user's voice customization settings

        Args:
            user_id: User ID
            voice_id: Voice identifier (e.g., "female_gentle")
            speed: Speech speed (0.5 - 2.0)
            pitch: Voice pitch (0.5 - 2.0)
            volume: Volume level (0.5 - 2.0)
            persona_traits: Dict of persona trait values

        Returns:
            Updated settings
        """
        try:
            logger.info(
                f"Updating voice settings for user {user_id}",
                extra={
                    "voice_id": voice_id,
                    "speed": speed,
                    "pitch": pitch,
                    "has_persona_traits": bool(persona_traits),
                },
            )

            # Get current settings
            current_settings = await self.get_voice_settings(user_id)

            # Update with new values
            if voice_id is not None:
                if voice_id not in self.AVAILABLE_VOICES:
                    logger.warning(f"Invalid voice_id: {voice_id}, keeping current")
                else:
                    current_settings["voice_id"] = voice_id
                    current_settings["voice_name"] = self.AVAILABLE_VOICES[voice_id][
                        "name"
                    ]

            if speed is not None:
                current_settings["speed"] = max(0.5, min(2.0, speed))

            if pitch is not None:
                current_settings["pitch"] = max(0.5, min(2.0, pitch))

            if volume is not None:
                current_settings["volume"] = max(0.5, min(2.0, volume))

            if persona_traits:
                current_persona = current_settings.get("persona_traits", {})
                for trait, value in persona_traits.items():
                    if trait in self.PERSONA_TRAITS:
                        trait_config = self.PERSONA_TRAITS[trait]
                        clamped_value = max(
                            trait_config["min"], min(trait_config["max"], value)
                        )
                        current_persona[trait] = clamped_value
                    else:
                        logger.warning(f"Unknown persona trait: {trait}")

                current_settings["persona_traits"] = current_persona

            current_settings["updated_at"] = datetime.now().isoformat()

            # Save to database (store in user profile)
            profile = await self.db.get_user_profile(user_id)
            if profile:
                # Add voice_settings attribute
                profile.voice_settings = current_settings
                await self.db.save_user_profile(profile)

            logger.info(f"Voice settings updated successfully for {user_id}")
            return current_settings

        except Exception as e:
            logger.error(f"Error updating voice settings for {user_id}: {e}")
            raise

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default voice settings"""
        return {
            "voice_id": "default",
            "voice_name": "Default",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
            "persona_traits": {
                trait: config["default"]
                for trait, config in self.PERSONA_TRAITS.items()
            },
            "updated_at": datetime.now().isoformat(),
        }

    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voice options"""
        return self.AVAILABLE_VOICES

    def get_persona_trait_configs(self) -> Dict[str, Any]:
        """Get persona trait configuration"""
        return self.PERSONA_TRAITS
