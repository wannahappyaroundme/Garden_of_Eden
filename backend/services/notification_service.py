"""
Notification Service for Project Eden V2
Manage smart notifications, reminders, and FCM integration
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationType(str, Enum):
    """Types of notifications"""
    GOAL_REMINDER = "goal_reminder"
    STAGNATION_ALERT = "stagnation_alert"
    MILESTONE_ACHIEVED = "milestone_achieved"
    ENCOURAGEMENT = "encouragement"
    WEEKLY_SUMMARY = "weekly_summary"
    CUSTOM = "custom"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class NotificationService:
    """Service for managing smart notifications and reminders"""

    # Default notification settings
    DEFAULT_PREFERENCES = {
        "enabled": True,
        "goal_reminders": True,
        "stagnation_alerts": True,
        "milestone_notifications": True,
        "encouragement_messages": True,
        "weekly_summaries": True,
        "reminder_time": "20:00",  # 8 PM default
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        "timezone": "Asia/Seoul",
    }

    def __init__(self, db_service, goal_progress_service=None):
        """
        Initialize notification service

        Args:
            db_service: DynamoDB service instance
            goal_progress_service: Optional goal progress service for insights
        """
        self.db = db_service
        self.goal_service = goal_progress_service

    # ==================== FCM Token Management ====================

    async def register_fcm_token(
        self, user_id: str, fcm_token: str, device_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register or update FCM token for a user

        Args:
            user_id: User ID
            fcm_token: Firebase Cloud Messaging token
            device_info: Optional device information (platform, model, os_version)

        Returns:
            Registration status
        """
        try:
            logger.info(f"Registering FCM token for user {user_id}")

            # Get user profile
            profile = await self.db.get_user_profile(user_id)
            if not profile:
                logger.warning(f"Profile not found for user {user_id}")
                raise ValueError(f"User profile not found: {user_id}")

            # Store FCM token and device info
            fcm_data = {
                "fcm_token": fcm_token,
                "registered_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }

            if device_info:
                fcm_data["device_info"] = device_info

            # Add to user profile
            profile.fcm_data = fcm_data
            await self.db.save_user_profile(profile)

            logger.info(f"FCM token registered successfully for {user_id}")

            return {
                "success": True,
                "message": "FCM token registered successfully",
                "registered_at": fcm_data["registered_at"],
            }

        except Exception as e:
            logger.error(f"Error registering FCM token for {user_id}: {e}")
            raise

    async def unregister_fcm_token(self, user_id: str) -> Dict[str, Any]:
        """
        Remove FCM token for a user (e.g., on logout)

        Args:
            user_id: User ID

        Returns:
            Unregistration status
        """
        try:
            logger.info(f"Unregistering FCM token for user {user_id}")

            profile = await self.db.get_user_profile(user_id)
            if profile and hasattr(profile, "fcm_data"):
                profile.fcm_data = None
                await self.db.save_user_profile(profile)

            logger.info(f"FCM token unregistered for {user_id}")

            return {"success": True, "message": "FCM token unregistered"}

        except Exception as e:
            logger.error(f"Error unregistering FCM token for {user_id}: {e}")
            raise

    # ==================== Notification Preferences ====================

    async def get_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's notification preferences

        Returns:
            {
                "enabled": true,
                "goal_reminders": true,
                "stagnation_alerts": true,
                "milestone_notifications": true,
                "encouragement_messages": true,
                "weekly_summaries": true,
                "reminder_time": "20:00",
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00",
                "timezone": "Asia/Seoul"
            }
        """
        try:
            logger.info(f"Fetching notification preferences for user {user_id}")

            profile = await self.db.get_user_profile(user_id)
            if not profile:
                return self.DEFAULT_PREFERENCES.copy()

            # Get stored preferences or return defaults
            preferences = getattr(profile, "notification_preferences", None)
            if not preferences:
                return self.DEFAULT_PREFERENCES.copy()

            return preferences

        except Exception as e:
            logger.error(f"Error getting notification preferences for {user_id}: {e}")
            return self.DEFAULT_PREFERENCES.copy()

    async def update_notification_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user's notification preferences

        Args:
            user_id: User ID
            preferences: Dict of preference updates

        Returns:
            Updated preferences
        """
        try:
            logger.info(
                f"Updating notification preferences for user {user_id}",
                extra={"preferences": preferences},
            )

            profile = await self.db.get_user_profile(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")

            # Get current preferences or defaults
            current_prefs = await self.get_notification_preferences(user_id)

            # Update with new values
            current_prefs.update(preferences)
            current_prefs["updated_at"] = datetime.now().isoformat()

            # Save to profile
            profile.notification_preferences = current_prefs
            await self.db.save_user_profile(profile)

            logger.info(f"Notification preferences updated for {user_id}")

            return current_prefs

        except Exception as e:
            logger.error(f"Error updating notification preferences for {user_id}: {e}")
            raise

    # ==================== Notification Scheduling Logic ====================

    async def should_send_notification(
        self, user_id: str, notification_type: NotificationType
    ) -> bool:
        """
        Check if notification should be sent based on user preferences and quiet hours

        Args:
            user_id: User ID
            notification_type: Type of notification

        Returns:
            True if notification should be sent
        """
        try:
            preferences = await self.get_notification_preferences(user_id)

            # Check if notifications are globally enabled
            if not preferences.get("enabled", True):
                logger.info(f"Notifications disabled for user {user_id}")
                return False

            # Check type-specific preferences
            type_map = {
                NotificationType.GOAL_REMINDER: "goal_reminders",
                NotificationType.STAGNATION_ALERT: "stagnation_alerts",
                NotificationType.MILESTONE_ACHIEVED: "milestone_notifications",
                NotificationType.ENCOURAGEMENT: "encouragement_messages",
                NotificationType.WEEKLY_SUMMARY: "weekly_summaries",
            }

            pref_key = type_map.get(notification_type)
            if pref_key and not preferences.get(pref_key, True):
                logger.info(f"{notification_type} disabled for user {user_id}")
                return False

            # Check quiet hours
            if self._is_quiet_hours(preferences):
                logger.info(f"Currently in quiet hours for user {user_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking notification eligibility for {user_id}: {e}")
            return False

    def _is_quiet_hours(self, preferences: Dict[str, Any]) -> bool:
        """Check if current time is in quiet hours"""
        try:
            now = datetime.now().time()
            quiet_start = datetime.strptime(
                preferences.get("quiet_hours_start", "22:00"), "%H:%M"
            ).time()
            quiet_end = datetime.strptime(
                preferences.get("quiet_hours_end", "08:00"), "%H:%M"
            ).time()

            # Handle overnight quiet hours
            if quiet_start > quiet_end:
                return now >= quiet_start or now <= quiet_end
            else:
                return quiet_start <= now <= quiet_end

        except Exception as e:
            logger.error(f"Error checking quiet hours: {e}")
            return False

    # ==================== Notification Content Generation ====================

    async def generate_goal_reminder(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate daily goal reminder notification

        Returns:
            Notification payload or None if not applicable
        """
        try:
            logger.info(f"Generating goal reminder for user {user_id}")

            if not await self.should_send_notification(
                user_id, NotificationType.GOAL_REMINDER
            ):
                return None

            # Get goal progress
            if self.goal_service:
                tracker = await self.goal_service.get_goal_tracker(user_id)
                if not tracker:
                    return None

                goal_title = tracker.goal_title or "목표"

                # Check if already logged today
                snapshots = tracker.progress_snapshots or []
                today = datetime.now().date()
                logged_today = any(
                    datetime.fromisoformat(s.get("timestamp", "")).date() == today
                    for s in snapshots
                    if s.get("timestamp")
                )

                if logged_today:
                    logger.info(f"User {user_id} already logged progress today")
                    return None

                # Generate reminder message
                days_active = tracker.days_since_start or 0
                completion = tracker.completion_percentage or 0

                message = f"오늘의 '{goal_title}' 진행 상황을 기록하세요!"
                body = f"{days_active}일째 도전 중 • {completion:.1f}% 달성"

                return {
                    "type": NotificationType.GOAL_REMINDER,
                    "priority": NotificationPriority.NORMAL,
                    "title": message,
                    "body": body,
                    "data": {
                        "user_id": user_id,
                        "goal_id": tracker.goal_id,
                        "action": "open_progress_entry",
                    },
                }

            return None

        except Exception as e:
            logger.error(f"Error generating goal reminder for {user_id}: {e}")
            return None

    async def generate_stagnation_alert(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate stagnation alert notification

        Returns:
            Notification payload or None if not applicable
        """
        try:
            logger.info(f"Checking stagnation for user {user_id}")

            if not await self.should_send_notification(
                user_id, NotificationType.STAGNATION_ALERT
            ):
                return None

            if self.goal_service:
                tracker = await self.goal_service.get_goal_tracker(user_id)
                if not tracker:
                    return None

                # Check if stagnant (no progress in 3+ days)
                snapshots = tracker.progress_snapshots or []
                if not snapshots:
                    return None

                last_snapshot = snapshots[-1]
                last_date = datetime.fromisoformat(last_snapshot["timestamp"])
                days_since = (datetime.now() - last_date).days

                if days_since >= 3:
                    goal_title = tracker.goal_title or "목표"

                    return {
                        "type": NotificationType.STAGNATION_ALERT,
                        "priority": NotificationPriority.HIGH,
                        "title": f"'{goal_title}'를 기다리고 있어요!",
                        "body": f"{days_since}일 동안 기록이 없어요. 작은 진전이라도 괜찮아요!",
                        "data": {
                            "user_id": user_id,
                            "goal_id": tracker.goal_id,
                            "days_since": days_since,
                            "action": "open_progress_entry",
                        },
                    }

            return None

        except Exception as e:
            logger.error(f"Error generating stagnation alert for {user_id}: {e}")
            return None

    async def generate_milestone_notification(
        self, user_id: str, milestone_title: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate milestone achievement notification

        Args:
            user_id: User ID
            milestone_title: Title of completed milestone

        Returns:
            Notification payload
        """
        try:
            logger.info(f"Generating milestone notification for user {user_id}")

            if not await self.should_send_notification(
                user_id, NotificationType.MILESTONE_ACHIEVED
            ):
                return None

            return {
                "type": NotificationType.MILESTONE_ACHIEVED,
                "priority": NotificationPriority.HIGH,
                "title": "🎉 마일스톤 달성!",
                "body": f"'{milestone_title}'를 완료했어요! 축하합니다!",
                "data": {
                    "user_id": user_id,
                    "milestone_title": milestone_title,
                    "action": "open_goal_dashboard",
                },
            }

        except Exception as e:
            logger.error(f"Error generating milestone notification for {user_id}: {e}")
            return None

    async def generate_encouragement_message(
        self, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate personalized encouragement notification

        Returns:
            Notification payload or None
        """
        try:
            logger.info(f"Generating encouragement message for user {user_id}")

            if not await self.should_send_notification(
                user_id, NotificationType.ENCOURAGEMENT
            ):
                return None

            if self.goal_service:
                tracker = await self.goal_service.get_goal_tracker(user_id)
                if not tracker:
                    return None

                # Get trend to personalize message
                trend = tracker.trend or {}
                direction = trend.get("direction", "stable")
                streak = trend.get("current_streak", 0)

                messages = {
                    "improving": [
                        "점점 더 나아지고 있어요! 이 기세를 유지하세요 💪",
                        f"{streak}일 연속 기록 중! 정말 대단해요!",
                    ],
                    "stable": [
                        "꾸준히 하고 계시네요! 일관성이 성공의 열쇠예요 🔑",
                        "한 걸음 한 걸음 나아가고 있어요. 화이팅!",
                    ],
                    "declining": [
                        "완벽하지 않아도 괜찮아요. 작은 진전도 진전이에요!",
                        "어려운 시기도 있어요. 지금 이 순간도 소중해요 💚",
                    ],
                }

                message_list = messages.get(direction, messages["stable"])
                import random

                message = random.choice(message_list)

                return {
                    "type": NotificationType.ENCOURAGEMENT,
                    "priority": NotificationPriority.LOW,
                    "title": "작은 응원의 메시지",
                    "body": message,
                    "data": {
                        "user_id": user_id,
                        "action": "open_goal_dashboard",
                    },
                }

            return None

        except Exception as e:
            logger.error(f"Error generating encouragement message for {user_id}: {e}")
            return None

    # ==================== Test Notification ====================

    async def send_test_notification(self, user_id: str) -> Dict[str, Any]:
        """
        Send a test notification to verify FCM setup

        Args:
            user_id: User ID

        Returns:
            Test notification payload
        """
        try:
            logger.info(f"Generating test notification for user {user_id}")

            profile = await self.db.get_user_profile(user_id)
            if not profile or not hasattr(profile, "fcm_data"):
                raise ValueError("FCM token not registered for this user")

            fcm_data = profile.fcm_data
            if not fcm_data or not fcm_data.get("fcm_token"):
                raise ValueError("FCM token not found")

            return {
                "type": NotificationType.CUSTOM,
                "priority": NotificationPriority.NORMAL,
                "title": "Eden 알림 테스트",
                "body": "알림이 정상적으로 작동하고 있어요! 🌱",
                "data": {
                    "user_id": user_id,
                    "test": True,
                    "timestamp": datetime.now().isoformat(),
                },
                "fcm_token": fcm_data["fcm_token"],
            }

        except Exception as e:
            logger.error(f"Error generating test notification for {user_id}: {e}")
            raise

    # ==================== Bulk Operations ====================

    async def get_users_needing_reminders(self) -> List[str]:
        """
        Get list of user IDs who need daily reminders
        (To be called by scheduled task)

        Returns:
            List of user IDs
        """
        try:
            logger.info("Fetching users needing reminders")

            # This would query all users with active goals and reminder preferences
            # For now, return empty list (implement when needed)
            # In production, this would scan users with:
            # - notification_preferences.enabled = true
            # - notification_preferences.goal_reminders = true
            # - Has active goal tracker
            # - Hasn't logged today
            # - Current time matches reminder_time

            return []

        except Exception as e:
            logger.error(f"Error fetching users needing reminders: {e}")
            return []
