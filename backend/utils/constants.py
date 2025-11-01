"""
Constants for Project Eden V2
"""
from enum import Enum

# Persona Types
class PersonaType(str, Enum):
    ADAM = "adam"
    EVE = "eve"

# App Modes
class AppMode(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"

# Emotional States
class EmotionalState(str, Enum):
    ANXIOUS = "anxious"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CALM = "calm"
    STRESSED = "stressed"
    HAPPY = "happy"
    SAD = "sad"
    CONFUSED = "confused"

# Learning Event Types
class LearningEventType(str, Enum):
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    TRAIT_DISCOVERED = "trait_discovered"
    TRAIT_REINFORCED = "trait_reinforced"
    WEIGHT_UPDATED = "weight_updated"
    EMOTIONAL_STATE_DETECTED = "emotional_state_detected"
    PITFALL_DETECTED = "pitfall_detected"
    GOAL_MODIFIED = "goal_modified"

# Pitfall Warning Reasons
class PitfallReason(str, Enum):
    CORE_PITFALL_TRIGGERED = "CORE_PITFALL_TRIGGERED"
    WEAK_ALIGNMENT = "WEAK_ALIGNMENT"
    ALIGNED = "ALIGNED"

# TTS Voice Names
TTS_VOICES = {
    PersonaType.ADAM: "ko-KR-InJoonNeural",  # Male, father-like
    PersonaType.EVE: "ko-KR-SunHiNeural"     # Female, energetic
}

# Learning Algorithm Constants
LEARNING_RATE = 0.1
DECAY_RATE = 0.02
TIME_THRESHOLD_DAYS = 7
MIN_TRAIT_WEIGHT = 0.3
MAX_TRAIT_WEIGHT = 1.0

# Pitfall Detection
ALIGNMENT_THRESHOLD = 0.3  # Below this = weak alignment
PITFALL_CONFIDENCE_THRESHOLD = 0.6

# API Limits
MAX_CAMERA_FRAMES = 8
MAX_FILE_SIZE_MB = 10
MAX_AUDIO_DURATION_SECONDS = 300  # 5 minutes

# Profile Maturity Levels
class ProfileMaturity(str, Enum):
    NEW = "new"  # < 10 conversations
    EMERGING = "emerging"  # 10-30 conversations
    MEDIUM = "medium"  # 30-70 conversations
    HIGH = "high"  # 70-120 conversations
    EXPERT = "expert"  # 120+ conversations

def get_profile_maturity(conversation_count: int) -> ProfileMaturity:
    """Determine profile maturity based on conversation count"""
    if conversation_count < 10:
        return ProfileMaturity.NEW
    elif conversation_count < 30:
        return ProfileMaturity.EMERGING
    elif conversation_count < 70:
        return ProfileMaturity.MEDIUM
    elif conversation_count < 120:
        return ProfileMaturity.HIGH
    else:
        return ProfileMaturity.EXPERT
