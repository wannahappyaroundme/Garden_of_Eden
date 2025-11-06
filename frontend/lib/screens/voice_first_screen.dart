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

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _initializeSession();
  }

  Future<void> _initializeSession() async {
    final session = ref.read(sessionProvider.notifier);
    await session.initialize(widget.userId);
  }

  @override
  void dispose() {
    _autoHideTimer?.cancel();
    _disposeServices();
    super.dispose();
  }

  Future<void> _initializeCamera() async {
    try {
      final cameraService = ref.read(cameraServiceProvider);
      await cameraService.initialize();
      setState(() {}); // Refresh to show camera
    } catch (e) {
      _showError('카메라 초기화 실패: $e');
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

      appState.setMode(AppMode.listening);
      appState.setLoadingMessage('녹음 중...');

      // Start audio recording
      await audioService.startRecording();

      // Start camera capture
      cameraService.startCapture();
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
      final cameraFrames = await cameraService.stopAndGetKeyframes();

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

      // Send to backend with retry callback
      final response = await apiService.sendChat(
        userId: widget.userId,
        message: message,  // Now contains actual transcription
        voiceType: currentState.persona,
        sessionId: sessionId,  // Include session ID
        cameraFrames: cameraFrames,
        audioFile: audioFile,
        onRetry: (attempt, error) {
          // Update retry state
          appState.setRetryAttempt(attempt);
          appState.setLoadingMessage('재시도 중... ($attempt/3)');
        },
      );

      // Increment turn count after successful conversation
      sessionNotifier.incrementTurnCount();

      // Clear loading
      appState.clearLoadingMessage();
      appState.setRetryAttempt(0);

      // Check for pitfall warning
      if (response.pitfallWarningTriggered) {
        appState.showPitfall('주의: One Thing에서 벗어나고 있습니다!');
      }

      // Update state with response
      appState.setLastResponse(response);
      appState.setMode(AppMode.responding);

      // Play TTS audio
      if (response.responseAudioBase64 != null) {
        appState.setTTSPlaying(true);
        await audioService.playFromBase64(response.responseAudioBase64!);
        appState.setTTSPlaying(false);
      }

      // Auto-hide response after 3 seconds
      _autoHideTimer?.cancel();
      _autoHideTimer = Timer(UIConstants.responseAutoHideDuration, () {
        appState.setMode(AppMode.idle);
        appState.clearResponse();
      });

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

    return Scaffold(
      body: Stack(
        children: [
          // 1. Full-screen camera view
          CameraView(controller: cameraService.controller),

          // 2. Top navigation bar
          Positioned(
            top: 50,
            left: 16,
            right: 16,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Profile button
                IconButton(
                  icon: const Icon(Icons.person, color: Colors.white, size: 28),
                  onPressed: () {
                    AppNavigation.toProfile(context, widget.userId);
                  },
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

          // 5. Response overlay (bottom 1/3)
          if (appState.lastResponse != null)
            ResponseOverlay(
              response: appState.lastResponse?.responseText,
              isPlaying: appState.isTTSPlaying,
              onDismiss: () {
                ref.read(appStateProvider.notifier).clearResponse();
                ref.read(appStateProvider.notifier).setMode(AppMode.idle);
              },
            ),

          // 6. Loading overlay (full screen)
          if (appState.loadingMessage != null)
            LoadingOverlay(
              message: appState.loadingMessage!,
              retryAttempt: appState.retryAttempt > 0 ? appState.retryAttempt : null,
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
