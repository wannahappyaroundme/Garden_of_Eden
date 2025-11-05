"""
Custom exceptions package for Project Eden V2
"""
from .goal_exceptions import (
    GoalProgressException,
    GoalNotFoundException,
    MilestoneNotFoundException,
    OneThingNotSetException,
    InvalidMetricsConfigException,
    InvalidMoodRatingException,
    InvalidDateFormatException,
    AIServiceException,
    DatabaseOperationException,
    InsufficientDataException
)

__all__ = [
    "GoalProgressException",
    "GoalNotFoundException",
    "MilestoneNotFoundException",
    "OneThingNotSetException",
    "InvalidMetricsConfigException",
    "InvalidMoodRatingException",
    "InvalidDateFormatException",
    "AIServiceException",
    "DatabaseOperationException",
    "InsufficientDataException"
]
