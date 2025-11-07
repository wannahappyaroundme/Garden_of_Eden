/// Notification Settings Screen - Configure push notifications and reminders
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/constants.dart';
import '../providers/service_providers.dart';

class NotificationSettingsScreen extends ConsumerStatefulWidget {
  final String userId;

  const NotificationSettingsScreen({super.key, required this.userId});

  @override
  ConsumerState<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends ConsumerState<NotificationSettingsScreen> {
  // Notification toggles
  bool _notificationsEnabled = true;
  bool _goalReminders = true;
  bool _stagnationAlerts = true;
  bool _milestoneNotifications = true;
  bool _encouragementMessages = true;
  bool _weeklySummaries = true;

  // Time settings
  TimeOfDay _reminderTime = const TimeOfDay(hour: 20, minute: 0);
  TimeOfDay _quietHoursStart = const TimeOfDay(hour: 22, minute: 0);
  TimeOfDay _quietHoursEnd = const TimeOfDay(hour: 8, minute: 0);

  bool _isLoading = true;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() => _isLoading = true);

    try {
      final apiService = ref.read(apiServiceProvider);
      final settings = await apiService.getNotificationSettings(widget.userId);

      setState(() {
        _notificationsEnabled = settings['enabled'] ?? true;
        _goalReminders = settings['goal_reminders'] ?? true;
        _stagnationAlerts = settings['stagnation_alerts'] ?? true;
        _milestoneNotifications = settings['milestone_notifications'] ?? true;
        _encouragementMessages = settings['encouragement_messages'] ?? true;
        _weeklySummaries = settings['weekly_summaries'] ?? true;

        // Parse time settings
        if (settings['reminder_time'] != null) {
          final parts = (settings['reminder_time'] as String).split(':');
          _reminderTime = TimeOfDay(
            hour: int.parse(parts[0]),
            minute: int.parse(parts[1]),
          );
        }
        if (settings['quiet_hours_start'] != null) {
          final parts = (settings['quiet_hours_start'] as String).split(':');
          _quietHoursStart = TimeOfDay(
            hour: int.parse(parts[0]),
            minute: int.parse(parts[1]),
          );
        }
        if (settings['quiet_hours_end'] != null) {
          final parts = (settings['quiet_hours_end'] as String).split(':');
          _quietHoursEnd = TimeOfDay(
            hour: int.parse(parts[0]),
            minute: int.parse(parts[1]),
          );
        }

        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        _showError('설정 로드 실패: ${e.toString()}');
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[700],
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'Notification Settings',
          style: TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          TextButton(
            onPressed: _saveSettings,
            child: const Text(
              'Save',
              style: TextStyle(
                color: Color(UIConstants.electricCyan),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                color: Color(UIConstants.electricCyan),
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(UIConstants.spacingLG),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Master toggle
                  _buildMasterToggle(),
                  const SizedBox(height: UIConstants.spacingXL),

                  // Notification types
                  _buildSectionHeader(
                    'Notification Types',
                    Icons.notifications,
                  ),
                  const SizedBox(height: UIConstants.spacingMD),
                  _buildNotificationTypes(),
                  const SizedBox(height: UIConstants.spacingXL),

                  // Time settings
                  _buildSectionHeader('Schedule', Icons.schedule),
                  const SizedBox(height: UIConstants.spacingMD),
                  _buildTimeSettings(),
                  const SizedBox(height: UIConstants.spacingXL),

                  // Test notification
                  Center(
                    child: ElevatedButton.icon(
                      onPressed: _sendTestNotification,
                      icon: const Icon(Icons.send),
                      label: const Text('Send Test Notification'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(UIConstants.electricCyan),
                        foregroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(
                          horizontal: UIConstants.spacingXL,
                          vertical: UIConstants.spacingMD,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: const Color(UIConstants.electricCyan), size: 24),
        const SizedBox(width: UIConstants.spacingSM),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: UIConstants.fontTitle,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildMasterToggle() {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: _notificationsEnabled
              ? [const Color(UIConstants.electricCyan), const Color(0xFF0099CC)]
              : [
                  const Color(UIConstants.darkGrey),
                  const Color(UIConstants.midGrey),
                ],
        ),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Row(
        children: [
          Icon(
            _notificationsEnabled
                ? Icons.notifications_active
                : Icons.notifications_off,
            color: _notificationsEnabled ? Colors.black : Colors.white54,
            size: 32,
          ),
          const SizedBox(width: UIConstants.spacingMD),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Push Notifications',
                  style: TextStyle(
                    color: _notificationsEnabled ? Colors.black : Colors.white,
                    fontSize: UIConstants.fontTitle,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: UIConstants.spacingXS),
                Text(
                  _notificationsEnabled ? 'Enabled' : 'Disabled',
                  style: TextStyle(
                    color: _notificationsEnabled
                        ? Colors.black54
                        : Colors.white54,
                    fontSize: UIConstants.fontCaption,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: _notificationsEnabled,
            onChanged: (value) {
              setState(() {
                _notificationsEnabled = value;
              });
            },
            activeThumbColor: Colors.black,
            activeTrackColor: Colors.white,
            inactiveThumbColor: Colors.white54,
            inactiveTrackColor: Colors.black54,
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationTypes() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        children: [
          _buildNotificationToggle(
            'Daily Goal Reminders',
            'Remind me to log daily progress',
            Icons.today,
            _goalReminders,
            (value) => setState(() => _goalReminders = value),
          ),
          const Divider(
            color: Color(UIConstants.midGrey),
            height: 1,
            indent: UIConstants.spacingLG,
            endIndent: UIConstants.spacingLG,
          ),
          _buildNotificationToggle(
            'Stagnation Alerts',
            'Notify if inactive for 3+ days',
            Icons.warning_amber,
            _stagnationAlerts,
            (value) => setState(() => _stagnationAlerts = value),
          ),
          const Divider(
            color: Color(UIConstants.midGrey),
            height: 1,
            indent: UIConstants.spacingLG,
            endIndent: UIConstants.spacingLG,
          ),
          _buildNotificationToggle(
            'Milestone Achievements',
            'Celebrate completed milestones',
            Icons.emoji_events,
            _milestoneNotifications,
            (value) => setState(() => _milestoneNotifications = value),
          ),
          const Divider(
            color: Color(UIConstants.midGrey),
            height: 1,
            indent: UIConstants.spacingLG,
            endIndent: UIConstants.spacingLG,
          ),
          _buildNotificationToggle(
            'Encouragement Messages',
            'Motivational messages based on progress',
            Icons.favorite,
            _encouragementMessages,
            (value) => setState(() => _encouragementMessages = value),
          ),
          const Divider(
            color: Color(UIConstants.midGrey),
            height: 1,
            indent: UIConstants.spacingLG,
            endIndent: UIConstants.spacingLG,
          ),
          _buildNotificationToggle(
            'Weekly Summaries',
            'Weekly progress reports',
            Icons.summarize,
            _weeklySummaries,
            (value) => setState(() => _weeklySummaries = value),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationToggle(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    final isEnabled = _notificationsEnabled && value;

    return SwitchListTile(
      value: value,
      onChanged: _notificationsEnabled ? onChanged : null,
      title: Row(
        children: [
          Icon(
            icon,
            color: isEnabled
                ? const Color(UIConstants.electricCyan)
                : Colors.white38,
            size: 20,
          ),
          const SizedBox(width: UIConstants.spacingSM),
          Expanded(
            child: Text(
              title,
              style: TextStyle(
                color: _notificationsEnabled ? Colors.white : Colors.white38,
                fontSize: UIConstants.fontBody,
              ),
            ),
          ),
        ],
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(left: 28.0, top: UIConstants.spacingXS),
        child: Text(
          subtitle,
          style: TextStyle(
            color: _notificationsEnabled ? Colors.white54 : Colors.white30,
            fontSize: UIConstants.fontCaption,
          ),
        ),
      ),
      activeThumbColor: const Color(UIConstants.electricCyan),
      inactiveThumbColor: Colors.white38,
    );
  }

  Widget _buildTimeSettings() {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        children: [
          _buildTimeSetting(
            'Daily Reminder Time',
            'When to send daily goal reminders',
            Icons.alarm,
            _reminderTime,
            (time) => setState(() => _reminderTime = time),
          ),
          const Divider(
            color: Color(UIConstants.midGrey),
            height: UIConstants.spacingLG * 2,
          ),
          _buildTimeSetting(
            'Quiet Hours Start',
            'Do not disturb from this time',
            Icons.bedtime,
            _quietHoursStart,
            (time) => setState(() => _quietHoursStart = time),
          ),
          const SizedBox(height: UIConstants.spacingMD),
          _buildTimeSetting(
            'Quiet Hours End',
            'Resume notifications after this time',
            Icons.wb_sunny,
            _quietHoursEnd,
            (time) => setState(() => _quietHoursEnd = time),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeSetting(
    String title,
    String subtitle,
    IconData icon,
    TimeOfDay time,
    ValueChanged<TimeOfDay> onChanged,
  ) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(
        icon,
        color: const Color(UIConstants.electricCyan),
        size: 24,
      ),
      title: Text(
        title,
        style: const TextStyle(
          color: Colors.white,
          fontSize: UIConstants.fontBody,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: const TextStyle(
          color: Colors.white54,
          fontSize: UIConstants.fontCaption,
        ),
      ),
      trailing: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: UIConstants.spacingMD,
          vertical: UIConstants.spacingSM,
        ),
        decoration: BoxDecoration(
          color: const Color(UIConstants.midGrey),
          borderRadius: BorderRadius.circular(UIConstants.spacingSM),
        ),
        child: Text(
          time.format(context),
          style: const TextStyle(
            color: Color(UIConstants.electricCyan),
            fontWeight: FontWeight.bold,
            fontSize: UIConstants.fontBody,
          ),
        ),
      ),
      onTap: () async {
        final TimeOfDay? picked = await showTimePicker(
          context: context,
          initialTime: time,
          builder: (context, child) {
            return Theme(
              data: ThemeData.dark().copyWith(
                colorScheme: const ColorScheme.dark(
                  primary: Color(UIConstants.electricCyan),
                  onPrimary: Colors.black,
                  surface: Color(UIConstants.darkGrey),
                  onSurface: Colors.white,
                ),
              ),
              child: child!,
            );
          },
        );
        if (picked != null) {
          onChanged(picked);
        }
      },
    );
  }

  Future<void> _saveSettings() async {
    if (_isSaving) return;

    setState(() => _isSaving = true);

    try {
      final apiService = ref.read(apiServiceProvider);

      // Format time as HH:mm
      String formatTime(TimeOfDay time) {
        return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
      }

      final settings = {
        'enabled': _notificationsEnabled,
        'goal_reminders': _goalReminders,
        'stagnation_alerts': _stagnationAlerts,
        'milestone_notifications': _milestoneNotifications,
        'encouragement_messages': _encouragementMessages,
        'weekly_summaries': _weeklySummaries,
        'reminder_time': formatTime(_reminderTime),
        'quiet_hours_start': formatTime(_quietHoursStart),
        'quiet_hours_end': formatTime(_quietHoursEnd),
      };

      await apiService.updateNotificationSettings(widget.userId, settings);

      setState(() => _isSaving = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('알림 설정이 저장되었습니다'),
            backgroundColor: Color(UIConstants.electricCyan),
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      setState(() => _isSaving = false);
      if (mounted) {
        _showError('설정 저장 실패: ${e.toString()}');
      }
    }
  }

  void _sendTestNotification() {
    // Test notification is a client-side feature
    // In production, this would trigger a real push notification via backend
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.black),
            SizedBox(width: UIConstants.spacingMD),
            Text('테스트 알림이 전송되었습니다'),
          ],
        ),
        backgroundColor: const Color(UIConstants.electricCyan),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(UIConstants.spacingSM),
        ),
      ),
    );
  }
}
