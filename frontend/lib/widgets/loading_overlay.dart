/// Loading Overlay Widget with Detailed Status
library;

import 'package:flutter/material.dart';
import '../utils/constants.dart';

class LoadingOverlay extends StatelessWidget {
  final String message;
  final PersonaType? persona;

  const LoadingOverlay({
    super.key,
    required this.message,
    this.persona,
  });

  /// Get display message with persona name if applicable
  String get displayMessage {
    // Replace "AI가 생각하는 중..." with persona-specific message
    if (persona != null && message.contains('AI가 생각하는 중')) {
      final personaName = persona!.displayName;
      return message.replaceAll('AI가 생각하는 중', '$personaName가 생각하는 중');
    }
    return message;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withValues(alpha: 0.7),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Loading spinner
            const SizedBox(
              width: 50,
              height: 50,
              child: CircularProgressIndicator(
                strokeWidth: 3,
                valueColor: AlwaysStoppedAnimation<Color>(
                  Color(UIConstants.electricCyan),
                ),
              ),
            ),

            const SizedBox(height: UIConstants.spacingLG),

            // Loading message
            Text(
              displayMessage,
              style: const TextStyle(
                color: Colors.white,
                fontSize: UIConstants.fontBodyLarge,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
