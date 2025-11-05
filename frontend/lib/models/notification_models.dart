/// Notification Models - Data structures for push notifications
library;

class NotificationPreferences {
  final bool enabled;
  final bool goalReminders;
  final bool stagnationAlerts;
  final bool milestoneNotifications;
  final bool encouragementMessages;
  final bool weeklySummaries;
  final String reminderTime;
  final String quietHoursStart;
  final String quietHoursEnd;
  final String timezone;
  final String? updatedAt;

  NotificationPreferences({
    required this.enabled,
    required this.goalReminders,
    required this.stagnationAlerts,
    required this.milestoneNotifications,
    required this.encouragementMessages,
    required this.weeklySummaries,
    required this.reminderTime,
    required this.quietHoursStart,
    required this.quietHoursEnd,
    required this.timezone,
    this.updatedAt,
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    return NotificationPreferences(
      enabled: json['enabled'] ?? true,
      goalReminders: json['goal_reminders'] ?? true,
      stagnationAlerts: json['stagnation_alerts'] ?? true,
      milestoneNotifications: json['milestone_notifications'] ?? true,
      encouragementMessages: json['encouragement_messages'] ?? true,
      weeklySummaries: json['weekly_summaries'] ?? true,
      reminderTime: json['reminder_time'] ?? '20:00',
      quietHoursStart: json['quiet_hours_start'] ?? '22:00',
      quietHoursEnd: json['quiet_hours_end'] ?? '08:00',
      timezone: json['timezone'] ?? 'Asia/Seoul',
      updatedAt: json['updated_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'goal_reminders': goalReminders,
      'stagnation_alerts': stagnationAlerts,
      'milestone_notifications': milestoneNotifications,
      'encouragement_messages': encouragementMessages,
      'weekly_summaries': weeklySummaries,
      'reminder_time': reminderTime,
      'quiet_hours_start': quietHoursStart,
      'quiet_hours_end': quietHoursEnd,
      'timezone': timezone,
    };
  }

  NotificationPreferences copyWith({
    bool? enabled,
    bool? goalReminders,
    bool? stagnationAlerts,
    bool? milestoneNotifications,
    bool? encouragementMessages,
    bool? weeklySummaries,
    String? reminderTime,
    String? quietHoursStart,
    String? quietHoursEnd,
    String? timezone,
    String? updatedAt,
  }) {
    return NotificationPreferences(
      enabled: enabled ?? this.enabled,
      goalReminders: goalReminders ?? this.goalReminders,
      stagnationAlerts: stagnationAlerts ?? this.stagnationAlerts,
      milestoneNotifications:
          milestoneNotifications ?? this.milestoneNotifications,
      encouragementMessages: encouragementMessages ?? this.encouragementMessages,
      weeklySummaries: weeklySummaries ?? this.weeklySummaries,
      reminderTime: reminderTime ?? this.reminderTime,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
      timezone: timezone ?? this.timezone,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class PushNotification {
  final String type;
  final String priority;
  final String title;
  final String body;
  final Map<String, dynamic> data;

  PushNotification({
    required this.type,
    required this.priority,
    required this.title,
    required this.body,
    required this.data,
  });

  factory PushNotification.fromJson(Map<String, dynamic> json) {
    return PushNotification(
      type: json['type'] ?? 'custom',
      priority: json['priority'] ?? 'normal',
      title: json['title'] ?? '',
      body: json['body'] ?? '',
      data: json['data'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'priority': priority,
      'title': title,
      'body': body,
      'data': data,
    };
  }

  bool get isHighPriority => priority == 'high';
}

class FCMTokenRequest {
  final String fcmToken;
  final Map<String, dynamic>? deviceInfo;

  FCMTokenRequest({
    required this.fcmToken,
    this.deviceInfo,
  });

  Map<String, dynamic> toJson() {
    return {
      'fcm_token': fcmToken,
      if (deviceInfo != null) 'device_info': deviceInfo,
    };
  }
}
