/// Response Overlay Widget (Bottom 1/3 with Glassmorphism)
library;

import 'dart:ui';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../utils/constants.dart';

class ResponseOverlay extends StatelessWidget {
  final String? response;
  final bool isPlaying;
  final VoidCallback? onDismiss;

  const ResponseOverlay({
    super.key,
    required this.response,
    required this.isPlaying,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    if (response == null || response!.isEmpty) {
      return const SizedBox.shrink();
    }

    final screenHeight = MediaQuery.of(context).size.height;
    final overlayHeight = screenHeight * UIConstants.responseOverlayHeightRatio;

    return GestureDetector(
      onVerticalDragEnd: (details) {
        if (details.primaryVelocity != null && details.primaryVelocity! > 0) {
          onDismiss?.call();
        }
      },
      child: Positioned(
        bottom: 0,
        left: 0,
        right: 0,
        height: overlayHeight,
        child: ClipRRect(
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(24),
          ),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.7),
                    Colors.black.withValues(alpha: 0.9),
                  ],
                ),
                border: Border(
                  top: BorderSide(
                    color: Colors.white.withValues(alpha: 0.1),
                    width: 1,
                  ),
                ),
              ),
              padding: const EdgeInsets.all(UIConstants.spacingLG),
              child: Column(
                children: [
                  // Swipe indicator
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.3),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: UIConstants.spacingMD),

                  // TTS waveform (if playing)
                  if (isPlaying)
                    Container(
                      height: 40,
                      margin: const EdgeInsets.only(bottom: UIConstants.spacingMD),
                      child: const _TTSWaveform(),
                    ),

                  // Response text (markdown)
                  Expanded(
                    child: SingleChildScrollView(
                      child: MarkdownBody(
                        data: response!,
                        styleSheet: MarkdownStyleSheet(
                          p: const TextStyle(
                            color: Colors.white,
                            fontSize: UIConstants.fontBodyLarge,
                            height: 1.5,
                          ),
                          code: TextStyle(
                            backgroundColor: Colors.grey[800],
                            color: Color(UIConstants.electricCyan),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Simple TTS Waveform Animation
class _TTSWaveform extends StatefulWidget {
  const _TTSWaveform();

  @override
  State<_TTSWaveform> createState() => _TTSWaveformState();
}

class _TTSWaveformState extends State<_TTSWaveform>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: List.generate(20, (index) {
            final phase = (index / 20 * 2 * math.pi) + (_controller.value * 2 * math.pi);
            final height = 10 + (20 * (0.5 + 0.5 * math.sin(phase)));

            return Container(
              width: 3,
              height: height,
              margin: const EdgeInsets.symmetric(horizontal: 2),
              decoration: BoxDecoration(
                color: Color(UIConstants.electricCyan),
                borderRadius: BorderRadius.circular(2),
              ),
            );
          }),
        );
      },
    );
  }
}
