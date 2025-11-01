/// Loading Overlay Widget with Detailed Status
library;

import 'package:flutter/material.dart';
import '../utils/constants.dart';

class LoadingOverlay extends StatelessWidget {
  final String message;
  final int? retryAttempt;
  final int? estimatedSeconds;
  final VoidCallback? onCancel;

  const LoadingOverlay({
    super.key,
    required this.message,
    this.retryAttempt,
    this.estimatedSeconds,
    this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withValues(alpha: 0.7),
      child: Center(
        child: Container(
          margin: const EdgeInsets.all(UIConstants.spacingXL),
          padding: const EdgeInsets.all(UIConstants.spacingXL),
          decoration: BoxDecoration(
            color: const Color(UIConstants.darkGrey),
            borderRadius: BorderRadius.circular(UIConstants.spacingLG),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.5),
                blurRadius: 30,
                spreadRadius: 10,
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Loading spinner
              const SizedBox(
                width: 60,
                height: 60,
                child: CircularProgressIndicator(
                  strokeWidth: 4,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    Color(UIConstants.electricCyan),
                  ),
                ),
              ),

              const SizedBox(height: UIConstants.spacingLG),

              // Loading message
              Text(
                message,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: UIConstants.fontBodyLarge,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),

              // Retry attempt indicator
              if (retryAttempt != null && retryAttempt! > 0) ...[
                const SizedBox(height: UIConstants.spacingSM),
                Text(
                  '재시도 중... ($retryAttempt/3)',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: UIConstants.fontBody,
                  ),
                ),
              ],

              // Estimated time
              if (estimatedSeconds != null) ...[
                const SizedBox(height: UIConstants.spacingSM),
                Text(
                  '예상 시간: $estimatedSeconds초',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.5),
                    fontSize: UIConstants.fontCaption,
                  ),
                ),
              ],

              // Cancel button
              if (onCancel != null) ...[
                const SizedBox(height: UIConstants.spacingLG),
                TextButton(
                  onPressed: onCancel,
                  style: TextButton.styleFrom(
                    foregroundColor: Colors.white.withValues(alpha: 0.7),
                    padding: const EdgeInsets.symmetric(
                      horizontal: UIConstants.spacingLG,
                      vertical: UIConstants.spacingSM,
                    ),
                  ),
                  child: const Text('취소'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
