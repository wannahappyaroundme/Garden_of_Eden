/// Wake Word Settings Screen - Configure wake word detection and background listening
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/wake_word_provider.dart';
import '../utils/constants.dart';

class WakeWordSettingsScreen extends ConsumerWidget {
  final String userId;

  const WakeWordSettingsScreen({
    super.key,
    required this.userId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wakeWordState = ref.watch(wakeWordProvider);
    final wakeWordNotifier = ref.read(wakeWordProvider.notifier);

    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'Wake Word Settings',
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
          // Status card
          Container(
            padding: const EdgeInsets.all(UIConstants.spacingLG),
            decoration: BoxDecoration(
              color: const Color(UIConstants.darkGrey),
              borderRadius: BorderRadius.circular(UIConstants.spacingMD),
              border: Border.all(
                color: wakeWordState.isListening
                    ? const Color(UIConstants.electricCyan).withValues(alpha: 0.5)
                    : Colors.white.withValues(alpha: 0.1),
                width: 1,
              ),
            ),
            child: Column(
              children: [
                Icon(
                  wakeWordState.isListening ? Icons.mic : Icons.mic_off,
                  color: wakeWordState.isListening
                      ? const Color(UIConstants.electricCyan)
                      : Colors.white.withValues(alpha: 0.5),
                  size: 48,
                ),
                const SizedBox(height: UIConstants.spacingMD),
                Text(
                  wakeWordState.isListening
                      ? 'Wake Word Active'
                      : 'Wake Word Inactive',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: UIConstants.fontTitle,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: UIConstants.spacingSM),
                Text(
                  wakeWordState.isListening
                      ? 'Say "Hey Adam" to activate'
                      : 'Enable wake word to use voice activation',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.6),
                    fontSize: UIConstants.fontBody,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),

          const SizedBox(height: UIConstants.spacingLG),

          // Wake word toggle
          _buildSettingsItem(
            title: 'Wake Word Detection',
            subtitle: 'Enable "Hey Adam" voice activation',
            icon: Icons.hearing,
            trailing: Switch(
              value: wakeWordState.isListening,
              onChanged: wakeWordState.isInitialized
                  ? (value) async {
                      await wakeWordNotifier.toggle();
                    }
                  : null,
              activeColor: const Color(UIConstants.electricCyan),
            ),
          ),

          const SizedBox(height: UIConstants.spacingMD),

          // Background listening toggle
          _buildSettingsItem(
            title: 'Background Listening',
            subtitle: 'Keep wake word active when app is in background',
            icon: Icons.apps,
            trailing: Switch(
              value: wakeWordState.isBackgroundEnabled,
              onChanged: wakeWordState.isInitialized && wakeWordState.isListening
                  ? (value) async {
                      await wakeWordNotifier.toggleBackground();
                    }
                  : null,
              activeColor: const Color(UIConstants.electricCyan),
            ),
          ),

          const SizedBox(height: UIConstants.spacingLG),

          // Info section
          Container(
            padding: const EdgeInsets.all(UIConstants.spacingMD),
            decoration: BoxDecoration(
              color: Colors.blue.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(UIConstants.spacingMD),
              border: Border.all(
                color: Colors.blue.withValues(alpha: 0.3),
                width: 1,
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.info_outline,
                  color: Colors.blue,
                  size: 20,
                ),
                const SizedBox(width: UIConstants.spacingSM),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'About Wake Word',
                        style: TextStyle(
                          color: Colors.blue,
                          fontSize: UIConstants.fontBody,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: UIConstants.spacingXS),
                      Text(
                        'Currently only "Hey Adam" is supported on Android devices. '
                        'Background listening requires notification permissions.',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.8),
                          fontSize: UIConstants.fontCaption,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Error message
          if (wakeWordState.errorMessage != null) ...[
            const SizedBox(height: UIConstants.spacingLG),
            Container(
              padding: const EdgeInsets.all(UIConstants.spacingMD),
              decoration: BoxDecoration(
                color: Colors.red.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(UIConstants.spacingMD),
                border: Border.all(
                  color: Colors.red.withValues(alpha: 0.3),
                  width: 1,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.error_outline,
                    color: Colors.red,
                    size: 20,
                  ),
                  const SizedBox(width: UIConstants.spacingSM),
                  Expanded(
                    child: Text(
                      wakeWordState.errorMessage!,
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.8),
                        fontSize: UIConstants.fontCaption,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSettingsItem({
    required String title,
    required String subtitle,
    required IconData icon,
    required Widget trailing,
  }) {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.1),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: const Color(UIConstants.electricCyan),
            size: 28,
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
          trailing,
        ],
      ),
    );
  }
}
