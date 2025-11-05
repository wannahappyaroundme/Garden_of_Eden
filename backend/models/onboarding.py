"""
Onboarding Models for Project Eden V2
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from utils.constants import PersonaType


class OnboardingQuestion(BaseModel):
    """A single onboarding question"""
    question: str
    purpose: str  # What this question helps discover
    follow_up_hints: List[str] = Field(default_factory=list)


class OnboardingTurn(BaseModel):
    """One turn in the onboarding conversation"""
    question: str
    user_response: str
    timestamp: datetime = Field(default_factory=datetime.now)


class OnboardingSession(BaseModel):
    """Active onboarding session"""
    session_id: str
    user_id: str
    persona: PersonaType
    current_step: int = 0
    turns: List[OnboardingTurn] = Field(default_factory=list)
    extracted_info: Dict[str, str] = Field(default_factory=dict)
    one_thing_identified: bool = False
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_turn(self, question: str, user_response: str):
        """Add a conversation turn"""
        self.turns.append(OnboardingTurn(
            question=question,
            user_response=user_response
        ))
        self.current_step += 1
        self.updated_at = datetime.now()

    def extract_info(self, key: str, value: str):
        """Store extracted information"""
        self.extracted_info[key] = value
        self.updated_at = datetime.now()


class OnboardingResult(BaseModel):
    """Result of completed onboarding"""
    user_id: str
    one_thing: str
    core_identity: Optional[str] = None
    core_motivation: Optional[str] = None
    personality_hints: List[str] = Field(default_factory=list)
    conversation_summary: str
    completed_at: datetime = Field(default_factory=datetime.now)
