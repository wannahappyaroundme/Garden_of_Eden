"""
Custom exceptions for Goal Progress tracking
Provides clear, user-friendly error messages with proper categorization
"""


class GoalProgressException(Exception):
    """Base exception for all goal progress errors"""
    def __init__(self, message: str, user_id: str = None):
        self.message = message
        self.user_id = user_id
        super().__init__(self.message)


class GoalNotFoundException(GoalProgressException):
    """Raised when a goal tracker is not found for a user"""
    def __init__(self, user_id: str):
        message = f"목표를 찾을 수 없습니다. 먼저 목표를 설정해주세요. (User: {user_id})"
        super().__init__(message, user_id)


class MilestoneNotFoundException(GoalProgressException):
    """Raised when a milestone is not found"""
    def __init__(self, user_id: str, milestone_id: str):
        message = f"마일스톤을 찾을 수 없습니다. (Milestone ID: {milestone_id})"
        super().__init__(message, user_id)
        self.milestone_id = milestone_id


class OneThingNotSetException(GoalProgressException):
    """Raised when trying to create a goal without One Thing set"""
    def __init__(self, user_id: str):
        message = "먼저 '가장 중요한 한 가지'를 설정해주세요. 온보딩을 완료하면 자동으로 설정됩니다."
        super().__init__(message, user_id)


class InvalidMetricsConfigException(GoalProgressException):
    """Raised when metrics configuration is invalid"""
    def __init__(self, user_id: str, reason: str):
        message = f"잘못된 측정 항목 설정입니다: {reason}"
        super().__init__(message, user_id)
        self.reason = reason


class InvalidMoodRatingException(GoalProgressException):
    """Raised when mood rating is out of valid range"""
    def __init__(self, user_id: str, mood_value: int):
        message = f"기분 점수는 1-5 사이여야 합니다. (입력값: {mood_value})"
        super().__init__(message, user_id)
        self.mood_value = mood_value


class InvalidDateFormatException(GoalProgressException):
    """Raised when date format is incorrect"""
    def __init__(self, user_id: str, date_value: str):
        message = f"날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용해주세요. (입력값: {date_value})"
        super().__init__(message, user_id)
        self.date_value = date_value


class AIServiceException(GoalProgressException):
    """Raised when AI service (Gemini) fails"""
    def __init__(self, user_id: str, operation: str, original_error: Exception = None):
        message = f"AI 서비스 요청 중 오류가 발생했습니다 ({operation}). 기본 설정을 사용합니다."
        super().__init__(message, user_id)
        self.operation = operation
        self.original_error = original_error


class DatabaseOperationException(GoalProgressException):
    """Raised when database operation fails"""
    def __init__(self, user_id: str, operation: str, original_error: Exception = None):
        message = f"데이터베이스 작업 중 오류가 발생했습니다 ({operation}). 잠시 후 다시 시도해주세요."
        super().__init__(message, user_id)
        self.operation = operation
        self.original_error = original_error


class InsufficientDataException(GoalProgressException):
    """Raised when there's not enough data for analysis"""
    def __init__(self, user_id: str, required_count: int, actual_count: int):
        message = f"분석을 위한 데이터가 부족합니다. 최소 {required_count}개의 기록이 필요합니다. (현재: {actual_count}개)"
        super().__init__(message, user_id)
        self.required_count = required_count
        self.actual_count = actual_count
