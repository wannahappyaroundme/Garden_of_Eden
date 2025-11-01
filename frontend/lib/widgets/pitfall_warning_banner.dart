/// Pitfall Warning Banner Widget
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/constants.dart';

class PitfallWarningBanner extends StatefulWidget {
  final String message;
  final VoidCallback onDismiss;
  final Duration autoHideDuration;

  const PitfallWarningBanner({
    super.key,
    required this.message,
    required this.onDismiss,
    this.autoHideDuration = const Duration(seconds: 5),
  });

  @override
  State<PitfallWarningBanner> createState() => _PitfallWarningBannerState();
}

class _PitfallWarningBannerState extends State<PitfallWarningBanner>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();

    // Haptic feedback
    HapticFeedback.mediumImpact();

    // Setup animation
    _controller = AnimationController(
      duration: UIConstants.animMedium,
      vsync: this,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, -1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    // Start animation
    _controller.forward();

    // Auto-hide after duration
    Future.delayed(widget.autoHideDuration, () {
      if (mounted) {
        _dismiss();
      }
    });
  }

  void _dismiss() async {
    await _controller.reverse();
    if (mounted) {
      widget.onDismiss();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: _slideAnimation,
      child: Container(
        width: double.infinity,
        margin: const EdgeInsets.all(UIConstants.spacingMD),
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        decoration: BoxDecoration(
          color: const Color(UIConstants.statePitfall),
          borderRadius: BorderRadius.circular(UIConstants.spacingMD),
          boxShadow: [
            BoxShadow(
              color: const Color(UIConstants.statePitfall).withValues(alpha: 0.3),
              blurRadius: 20,
              spreadRadius: 5,
            ),
          ],
        ),
        child: Row(
          children: [
            // Warning icon
            Container(
              padding: const EdgeInsets.all(UIConstants.spacingSM),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(UIConstants.spacingSM),
              ),
              child: const Icon(
                Icons.warning_amber_rounded,
                color: Colors.black,
                size: 32,
              ),
            ),
            const SizedBox(width: UIConstants.spacingMD),

            // Message
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    '⚠️ 함정 경고',
                    style: TextStyle(
                      color: Colors.black,
                      fontSize: UIConstants.fontTitle,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: UIConstants.spacingMicro),
                  Text(
                    widget.message,
                    style: const TextStyle(
                      color: Colors.black87,
                      fontSize: UIConstants.fontBody,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),

            // Close button
            IconButton(
              onPressed: _dismiss,
              icon: const Icon(
                Icons.close,
                color: Colors.black54,
              ),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
          ],
        ),
      ),
    );
  }
}
