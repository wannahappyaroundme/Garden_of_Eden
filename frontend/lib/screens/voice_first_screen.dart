/// Voice First Screen - Main UI
library;

import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/camera_view.dart';
import '../widgets/persona_toggle.dart';
import '../widgets/push_to_talk_button.dart';
import '../widgets/response_overlay.dart';
import '../widgets/loading_overlay.dart';
import '../widgets/pitfall_warning_banner.dart';
import '../providers/app_state_provider.dart';
import '../providers/session_provider.dart';
import '../providers/service_providers.dart';
import '../providers/wake_word_provider.dart';
import '../models/chat_models.dart';
import '../utils/constants.dart';
import '../utils/page_transitions.dart';

class VoiceFirstScreen extends ConsumerStatefulWidget {
  final String userId;

  const VoiceFirstScreen({
    super.key,
    required this.userId,
  });

  @override
  ConsumerState<VoiceFirstScreen> createState() => _VoiceFirstScreenState();
}

class _VoiceFirstScreenState extends ConsumerState<VoiceFirstScreen> {
  Timer? _autoHideTimer;
  bool _isCameraEnabled = false;

  @override
  void initState() {
    super.initState();
    // Camera is now optional - don't initialize automatically
    _initializeSession();
    _initializeWakeWord();
  }

  Future<void> _initializeSession() async {
    final session = ref.read(sessionProvider.notifier);
    await session.initialize(widget.userId);
  }

  Future<void> _initializeWakeWord() async {
    try {
      final wakeWordService = ref.read(wakeWordServiceProvider);
      final currentPersona = ref.read(appStateProvider).persona;

      // Initialize wake word with callback
      await wakeWordService.initialize(
        persona: currentPersona,
        onDetected: (detectedPersona) {
          // Wake word detected! Start recording automatically
          _onWakeWordDetected(detectedPersona);
        },
        onErrorCallback: (error) {
          // Handle wake word errors silently
        },
      );

      // Start listening automatically
      await wakeWordService.startListening();
    } catch (e) {
      // Silently fail - wake word is optional feature
      // Could be iOS or unsupported device
    }
  }

  void _onWakeWordDetected(PersonaType detectedPersona) {
    // Wake word detected - start recording
    _startRecording();
  }

  @override
  void dispose() {
    _autoHideTimer?.cancel();
    _disposeServices();
    super.dispose();
  }

  Future<void> _toggleCamera() async {
    if (_isCameraEnabled) {
      // Disable camera
      final cameraService = ref.read(cameraServiceProvider);
      await cameraService.dispose();
      setState(() {
        _isCameraEnabled = false;
      });
    } else {
      // Enable camera
      try {
        final cameraService = ref.read(cameraServiceProvider);
        await cameraService.initialize();
        setState(() {
          _isCameraEnabled = true;
        });
      } catch (e) {
        _showError('카메라 초기화 실패: $e');
      }
    }
  }

  Future<void> _disposeServices() async {
    final audioService = ref.read(audioServiceProvider);
    final cameraService = ref.read(cameraServiceProvider);
    await audioService.dispose();
    await cameraService.dispose();
  }

  Future<void> _startRecording() async {
    try {
      final audioService = ref.read(audioServiceProvider);
      final cameraService = ref.read(cameraServiceProvider);
      final appState = ref.read(appStateProvider.notifier);

      // Stop TTS playback if currently playing (allow interruption)
      if (ref.read(appStateProvider).isTTSPlaying) {
        await audioService.stopPlayback();
        appState.setTTSPlaying(false);
      }

      appState.setMode(AppMode.listening);
      appState.setLoadingMessage('녹음 중...');

      // Start audio recording
      await audioService.startRecording();

      // Start camera capture (only if camera is enabled)
      if (_isCameraEnabled) {
        cameraService.startCapture();
      }
    } catch (e) {
      _showError('녹음 시작 실패: $e');
      ref.read(appStateProvider.notifier).setMode(AppMode.idle);
      ref.read(appStateProvider.notifier).clearLoadingMessage();
    }
  }

  Future<void> _stopRecordingAndSend() async {
    try {
      final audioService = ref.read(audioServiceProvider);
      final cameraService = ref.read(cameraServiceProvider);
      final apiService = ref.read(apiServiceProvider);
      final appState = ref.read(appStateProvider.notifier);
      final currentState = ref.read(appStateProvider);

      // Stop recording
      appState.setLoadingMessage('음성을 처리하는 중...');
      final audioFile = await audioService.stopRecording();

      // Get camera keyframes (only if camera is enabled)
      final cameraFrames = _isCameraEnabled
          ? await cameraService.stopAndGetKeyframes()
          : <File>[];

      if (audioFile == null) {
        _showError('녹음 파일이 없습니다');
        appState.setMode(AppMode.idle);
        appState.clearLoadingMessage();
        return;
      }

      // Set processing mode
      appState.setMode(AppMode.processing);
      appState.setLoadingMessage('음성을 텍스트로 변환하는 중...');
      appState.setRetryAttempt(0);

      // Transcribe audio to text
      String message;
      try {
        message = await apiService.transcribeAudio(
          audioFile: audioFile,
          language: 'ko',
          onRetry: (attempt, error) {
            appState.setRetryAttempt(attempt);
            appState.setLoadingMessage('음성 인식 재시도 중... ($attempt/3)');
          },
        );

        if (message.isEmpty) {
          _showError('음성 인식 결과가 없습니다');
          appState.setMode(AppMode.idle);
          appState.clearLoadingMessage();
          return;
        }
      } catch (e) {
        _showError('음성 인식 실패: ${e.toString()}');
        appState.setMode(AppMode.idle);
        appState.clearLoadingMessage();
        return;
      }

      // Update loading message for AI processing
      appState.setLoadingMessage('AI가 생각하는 중...');
      appState.setRetryAttempt(0);

      // Get or create session ID
      final sessionNotifier = ref.read(sessionProvider.notifier);
      final sessionId = await sessionNotifier.getOrCreateSessionId(
        userId: widget.userId,
        persona: currentState.persona,
      );

      // Stream response from backend
      String fullResponseText = '';
      String? finalConversationId;
      String? finalAudioBase64;
      bool finalPitfallWarning = false;
      bool finalEmotionalSupport = false;

      try {
        final stream = apiService.sendChatStream(
          userId: widget.userId,
          message: message,
          voiceType: currentState.persona,
          sessionId: sessionId,
          cameraFrames: cameraFrames,
          audioFile: audioFile,
        );

        // Keep loading overlay (don't clear yet - wait for TTS)
        appState.setMode(AppMode.responding);

        await for (final event in stream) {
          if (event.isTextChunk) {
            // Accumulate text chunks
            fullResponseText += event.textContent!;

            // Update UI with progressive text display
            // Create temporary response for progressive display
            final tempResponse = ChatResponse(
              conversationId: 'streaming',
              responseText: fullResponseText,
              responseAudioBase64: null,
              pitfallWarningTriggered: false,
              emotionalSupportMode: false,
              profileUpdated: false,
              profileVersion: 0,
              processingTimeMs: 0,
            );
            appState.setLastResponse(tempResponse);
          } else if (event.isComplete) {
            // Final event with metadata and audio
            finalConversationId = event.conversationId!;
            finalAudioBase64 = event.audioBase64;
            finalPitfallWarning = event.pitfallWarningTriggered ?? false;
            finalEmotionalSupport = event.emotionalSupportMode ?? false;

            // Check for pitfall warning
            if (finalPitfallWarning) {
              appState.showPitfall('주의: One Thing에서 벗어나고 있습니다!');
            }

            // NOW clear loading overlay before playing TTS
            appState.clearLoadingMessage();

            // Play TTS audio
            if (finalAudioBase64 != null) {
              appState.setTTSPlaying(true);
              await audioService.playFromBase64(finalAudioBase64);
              appState.setTTSPlaying(false);
            }
          }
        }

        // Create ChatResponse for compatibility
        final response = ChatResponse(
          conversationId: finalConversationId ?? 'unknown',
          responseText: fullResponseText,
          responseAudioBase64: finalAudioBase64,
          pitfallWarningTriggered: finalPitfallWarning,
          emotionalSupportMode: finalEmotionalSupport,
          profileUpdated: false,
          profileVersion: 0,
          processingTimeMs: 0,
        );

        // Update state with final response
        appState.setLastResponse(response);

        // Add to conversation history
        appState.addConversation(message, fullResponseText);

        // Increment turn count after successful conversation
        sessionNotifier.incrementTurnCount();
      } catch (e) {
        _showError('스트리밍 오류: $e');
        appState.setMode(AppMode.idle);
        appState.clearResponse();
        return;
      }

      // Don't auto-hide - keep conversation history visible
      // User can start new conversation anytime (even during TTS playback)

      // Clean up temporary files
      await _cleanupTempFiles([audioFile, ...cameraFrames]);
    } catch (e) {
      _showError('오류: $e');
      final appState = ref.read(appStateProvider.notifier);
      appState.setMode(AppMode.idle);
      appState.clearLoadingMessage();
      appState.setRetryAttempt(0);
    }
  }

  Future<void> _cleanupTempFiles(List<File> files) async {
    for (final file in files) {
      try {
        if (await file.exists()) {
          await file.delete();
        }
      } catch (_) {}
    }
  }

  void _showError(String message) {
    ref.read(appStateProvider.notifier).setError(message);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[700],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    final cameraService = ref.watch(cameraServiceProvider);
    final wakeWordService = ref.watch(wakeWordServiceProvider);

    return Scaffold(
      body: Stack(
        children: [
          // 1. Full-screen camera view
          CameraView(controller: cameraService.controller),

          // 2. Top navigation bar with wake word indicator
          Positioned(
            top: 50,
            left: 16,
            right: 16,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Camera toggle button
                    IconButton(
                      icon: Icon(
                        _isCameraEnabled ? Icons.videocam : Icons.videocam_off,
                        color: _isCameraEnabled
                            ? Color(UIConstants.electricCyan)
                            : Colors.white.withValues(alpha: 0.5),
                        size: 28,
                      ),
                      onPressed: _toggleCamera,
                    ),
                    const SizedBox(width: 8),
                    // Profile button
                    IconButton(
                      icon: const Icon(Icons.person, color: Colors.white, size: 28),
                      onPressed: () {
                        AppNavigation.toProfile(context, widget.userId);
                      },
                    ),
                  ],
                ),
                // Wake word listening indicator
                if (wakeWordService.isListening)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.6),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: Color(UIConstants.electricCyan).withValues(alpha: 0.5),
                        width: 1,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Animated listening icon
                        TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0.0, end: 1.0),
                          duration: const Duration(milliseconds: 1000),
                          builder: (context, value, child) {
                            return Opacity(
                              opacity: 0.5 + (value * 0.5),
                              child: Icon(
                                Icons.mic,
                                color: Color(UIConstants.electricCyan),
                                size: 16,
                              ),
                            );
                          },
                          onEnd: () {
                            // Loop animation by triggering rebuild
                            if (mounted) setState(() {});
                          },
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Hey Adam 대기중',
                          style: TextStyle(
                            color: Color(UIConstants.electricCyan),
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                // Settings button
                IconButton(
                  icon: const Icon(Icons.settings, color: Colors.white, size: 28),
                  onPressed: () {
                    AppNavigation.toSettings(context, widget.userId);
                  },
                ),
              ],
            ),
          ),

          // 3. Persona toggle (top center)
          Positioned(
            top: 110,
            left: 0,
            right: 0,
            child: PersonaToggle(
              currentPersona: appState.persona,
              onChanged: (persona) {
                ref.read(appStateProvider.notifier).setPersona(persona);
              },
            ),
          ),

          // 4. Push-to-talk button (bottom center)
          Positioned(
            bottom: 100,
            left: 0,
            right: 0,
            child: Center(
              child: PushToTalkButton(
                mode: appState.mode,
                onPressStart: _startRecording,
                onPressEnd: _stopRecordingAndSend,
              ),
            ),
          ),

          // 5. Response overlay (bottom 1/3) with conversation history
          if (appState.lastResponse != null)
            ResponseOverlay(
              response: appState.lastResponse?.responseText,
              isPlaying: appState.isTTSPlaying,
              conversationHistory: appState.conversationHistory,
              onDismiss: () {
                // Don't clear response - keep history visible
                // Just return to idle mode
                ref.read(appStateProvider.notifier).setMode(AppMode.idle);
              },
            ),

          // 6. Loading overlay (full screen)
          if (appState.loadingMessage != null)
            LoadingOverlay(
              message: appState.loadingMessage!,
              persona: appState.persona,
            ),

          // 7. Pitfall warning banner (top)
          if (appState.showPitfallWarning && appState.pitfallMessage != null)
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: PitfallWarningBanner(
                message: appState.pitfallMessage!,
                onDismiss: () {
                  ref.read(appStateProvider.notifier).hidePitfall();
                },
              ),
            ),
        ],
      ),
    );
  }
}
