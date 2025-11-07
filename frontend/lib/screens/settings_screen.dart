/// Settings Screen - App settings and preferences
library;

import 'package:flutter/material.dart';
import '../utils/constants.dart';
import 'voice_settings_screen.dart';
import 'notification_settings_screen.dart';
import 'interaction_mode_screen.dart';

class SettingsScreen extends StatelessWidget {
  final String userId;

  const SettingsScreen({
    super.key,
    required this.userId,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'Settings',
          style: TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        children: [
          // Interaction Mode
          _buildSettingsCard(
            context,
            title: 'Interaction Mode',
            subtitle: 'Choose conversation style',
            icon: Icons.swap_horiz,
            color: Colors.purple,
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => InteractionModeScreen(userId: userId),
                ),
              );
            },
          ),
          const SizedBox(height: UIConstants.spacingMD),

          // Voice Settings
          _buildSettingsCard(
            context,
            title: 'Voice Settings',
            subtitle: 'Customize voice and persona',
            icon: Icons.record_voice_over,
            color: const Color(UIConstants.electricCyan),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => VoiceSettingsScreen(userId: userId),
                ),
              );
            },
          ),
          const SizedBox(height: UIConstants.spacingMD),

          // Notification Settings
          _buildSettingsCard(
            context,
            title: 'Notifications',
            subtitle: 'Manage alerts and reminders',
            icon: Icons.notifications,
            color: Colors.orange,
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      NotificationSettingsScreen(userId: userId),
                ),
              );
            },
          ),
          const SizedBox(height: UIConstants.spacingMD),

          // App Info
          _buildSettingsCard(
            context,
            title: 'About',
            subtitle: 'App version and information',
            icon: Icons.info_outline,
            color: Colors.blue,
            onTap: () {
              _showAboutDialog(context);
            },
          ),
          const SizedBox(height: UIConstants.spacingMD),

          // Danger Zone
          _buildSettingsCard(
            context,
            title: 'Clear Data',
            subtitle: 'Reset all conversations (cannot be undone)',
            icon: Icons.delete_forever,
            color: Colors.red,
            onTap: () {
              _showClearDataDialog(context);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      child: Container(
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        decoration: BoxDecoration(
          color: const Color(UIConstants.darkGrey),
          borderRadius: BorderRadius.circular(UIConstants.spacingMD),
          border: Border.all(
            color: color.withValues(alpha: 0.3),
            width: 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(UIConstants.spacingMD),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(UIConstants.spacingSM),
              ),
              child: Icon(
                icon,
                color: color,
                size: 28,
              ),
            ),
            const SizedBox(width: UIConstants.spacingMD),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: UIConstants.fontBody,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: UIConstants.spacingXS),
                  Text(
                    subtitle,
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.6),
                      fontSize: UIConstants.fontCaption,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right,
              color: Colors.white.withValues(alpha: 0.5),
            ),
          ],
        ),
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(UIConstants.darkGrey),
        title: const Text(
          'About Garden of Eden',
          style: TextStyle(color: Colors.white),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Version: 2.0.0',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
              ),
            ),
            const SizedBox(height: UIConstants.spacingSM),
            Text(
              'AI Personal Mentor System',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
              ),
            ),
            const SizedBox(height: UIConstants.spacingSM),
            Text(
              'Built with ❤️ for meaningful AI mentorship',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.6),
                fontSize: UIConstants.fontCaption,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Close',
              style: TextStyle(color: Color(UIConstants.electricCyan)),
            ),
          ),
        ],
      ),
    );
  }

  void _showClearDataDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(UIConstants.darkGrey),
        title: const Text(
          'Clear All Data?',
          style: TextStyle(color: Colors.white),
        ),
        content: Text(
          'This will delete all conversations and reset your profile. This action cannot be undone.',
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.8),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.6),
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              // TODO: Implement clear data functionality
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Data clearing not implemented yet'),
                  backgroundColor: Colors.orange,
                ),
              );
            },
            child: const Text(
              'Clear Data',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
}
