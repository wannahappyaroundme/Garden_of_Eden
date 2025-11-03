/// Push-to-Talk Button Widget
library;

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../utils/constants.dart';
import '../theme/app_theme.dart';

class PushToTalkButton extends StatefulWidget {
  final AppMode mode;
  final VoidCallback onPressStart;
  final VoidCallback onPressEnd;

  const PushToTalkButton({
    super.key,
    required this.mode,
    required this.onPressStart,
    required this.onPressEnd,
  });

  @override
  State<PushToTalkButton> createState() => _PushToTalkButtonState();
}

class _PushToTalkButtonState extends State<PushToTalkButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    final color = AppTheme.getColorForMode(widget.mode);
    final icon = AppTheme.getIconForMode(widget.mode);

    return GestureDetector(
      onTapDown: (_) {
        if (widget.mode == AppMode.idle) {
          setState(() => _isPressed = true);
          widget.onPressStart();
        }
      },
      onTapUp: (_) {
        if (_isPressed) {
          setState(() => _isPressed = false);
          widget.onPressEnd();
        }
      },
      onTapCancel: () {
        if (_isPressed) {
          setState(() => _isPressed = false);
          widget.onPressEnd();
        }
      },
      child: AnimatedContainer(
        duration: UIConstants.animQuick,
        width: UIConstants.pushToTalkButtonSize,
        height: UIConstants.pushToTalkButtonSize,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: color,
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha: 0.5),
              blurRadius: 30,
              spreadRadius: widget.mode == AppMode.listening ? 15 : 5,
            ),
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.8),
              blurRadius: 10,
              spreadRadius: 0,
            ),
          ],
        ),
        child: Icon(
          icon,
          size: UIConstants.pushToTalkIconSize,
          color: Colors.white,
        ),
      )
          .animate(
            target: widget.mode == AppMode.listening ? 1 : 0,
          )
          .scale(
            duration: 600.ms,
            curve: Curves.elasticOut,
          ),
    );
  }
}
