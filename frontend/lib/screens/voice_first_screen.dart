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
import '../providers/app_state_provider.dart';
import '../providers/service_providers.dart';
import '../utils/constants.dart';

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

      // Start audio recording
      await audioService.startRecording();

      // Start camera capture
      cameraService.startCapture();
    } catch (e) {
      _showError('녹음 시작 실패: $e');
      ref.read(appStateProvider.notifier).setMode(AppMode.idle);
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
      final audioFile = await audioService.stopRecording();
      final cameraFrames = await cameraService.stopAndGetKeyframes();

      if (audioFile == null) {
        _showError('녹음 파일이 없습니다');
        appState.setMode(AppMode.idle);
        return;
      }

      // Set processing mode
      appState.setMode(AppMode.processing);

      // Transcribe audio (optional - backend will do this)
      // For now, we'll send empty message and let backend transcribe
      final message = ''; // Backend will transcribe from audio

      // Send to backend
      final response = await apiService.sendChat(
        userId: widget.userId,
        message: message,
        voiceType: currentState.persona,
        cameraFrames: cameraFrames,
        audioFile: audioFile,
      );

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
      ref.read(appStateProvider.notifier).setMode(AppMode.idle);
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

          // 2. Persona toggle (top center)
          Positioned(
            top: 60,
            left: 0,
            right: 0,
            child: PersonaToggle(
              currentPersona: appState.persona,
              onChanged: (persona) {
                ref.read(appStateProvider.notifier).setPersona(persona);
              },
            ),
          ),

          // 3. Push-to-talk button (center)
          Center(
            child: PushToTalkButton(
              mode: appState.mode,
              onPressStart: _startRecording,
              onPressEnd: _stopRecordingAndSend,
            ),
          ),

          // 4. Response overlay (bottom 1/3)
          if (appState.lastResponse != null)
            ResponseOverlay(
              response: appState.lastResponse?.responseText,
              isPlaying: appState.isTTSPlaying,
              onDismiss: () {
                ref.read(appStateProvider.notifier).clearResponse();
                ref.read(appStateProvider.notifier).setMode(AppMode.idle);
              },
            ),
        ],
      ),
    );
  }
}
