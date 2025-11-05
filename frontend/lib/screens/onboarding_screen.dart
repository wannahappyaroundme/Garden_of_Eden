/// Onboarding Screen - Socratic Dialogue for Goal Discovery
library;

import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/camera_view.dart';
import '../widgets/push_to_talk_button.dart';
import '../widgets/loading_overlay.dart';
import '../providers/onboarding_provider.dart';
import '../providers/service_providers.dart';
import '../utils/constants.dart';
import '../screens/voice_first_screen.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  final PersonaType persona;

  const OnboardingScreen({
    super.key,
    required this.persona,
  });

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  bool _isRecording = false;

  @override
  void initState() {
    super.initState();
    _initializeOnboarding();
    _initializeCamera();
  }

  @override
  void dispose() {
    _disposeServices();
    super.dispose();
  }

  Future<void> _initializeOnboarding() async {
    final onboarding = ref.read(onboardingProvider.notifier);
    await onboarding.initialize();

    final state = ref.read(onboardingProvider);

    // If already completed, navigate to main screen
    if (state.isCompleted) {
      _navigateToMainScreen(state.userId!);
      return;
    }

    // If no active session, start new one
    if (state.sessionId == null) {
      await onboarding.startOnboarding(widget.persona);

      // Immediately play first question via TTS
      final newState = ref.read(onboardingProvider);
      if (newState.currentQuestion != null) {
        _playQuestionTTS(newState.currentQuestion!);
      }
    } else {
      // Resume existing session - play current question
      if (state.currentQuestion != null) {
        _playQuestionTTS(state.currentQuestion!);
      }
    }
  }

  Future<void> _initializeCamera() async {
    try {
      final cameraService = ref.read(cameraServiceProvider);
      await cameraService.initialize();
      if (mounted) setState(() {});
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

  Future<void> _playQuestionTTS(String questionText) async {
    // For onboarding, we just display text
    // Backend doesn't have dedicated TTS endpoint for onboarding questions
    // Text display is sufficient for Socratic dialogue
    // TTS can be added later if needed
  }

  Future<void> _startRecording() async {
    try {
      final audioService = ref.read(audioServiceProvider);

      setState(() => _isRecording = true);

      // Start audio recording
      await audioService.startRecording();
    } catch (e) {
      _showError('녹음 시작 실패: $e');
      setState(() => _isRecording = false);
    }
  }

  Future<void> _stopRecordingAndRespond() async {
    try {
      final audioService = ref.read(audioServiceProvider);
      final apiService = ref.read(apiServiceProvider);
      final onboarding = ref.read(onboardingProvider.notifier);

      setState(() => _isRecording = false);

      // Stop recording
      final audioFile = await audioService.stopRecording();

      if (audioFile == null) {
        _showError('녹음 파일이 없습니다');
        return;
      }

      // Transcribe audio to text
      String userResponse;
      try {
        userResponse = await apiService.transcribeAudio(
          audioFile: audioFile,
          language: 'ko',
        );

        if (userResponse.isEmpty) {
          _showError('음성 인식 결과가 없습니다');
          return;
        }
      } catch (e) {
        _showError('음성 인식 실패: ${e.toString()}');
        return;
      }

      // Send response to backend
      await onboarding.respondToQuestion(userResponse);

      // Check if onboarding completed
      final state = ref.read(onboardingProvider);
      if (state.isCompleted && state.userId != null) {
        _navigateToMainScreen(state.userId!);
      } else if (state.currentQuestion != null) {
        // Play next question via TTS
        _playQuestionTTS(state.currentQuestion!);
      }

      // Cleanup temp file
      await _cleanupTempFile(audioFile);
    } catch (e) {
      _showError('오류: $e');
      setState(() => _isRecording = false);
    }
  }

  Future<void> _cleanupTempFile(File file) async {
    try {
      if (await file.exists()) {
        await file.delete();
      }
    } catch (_) {}
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[700],
      ),
    );
  }

  void _navigateToMainScreen(String userId) {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => VoiceFirstScreen(userId: userId),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final onboardingState = ref.watch(onboardingProvider);
    final cameraService = ref.watch(cameraServiceProvider);

    return Scaffold(
      body: Stack(
        children: [
          // 1. Full-screen camera view
          CameraView(controller: cameraService.controller),

          // 2. Dark overlay for better text readability
          Container(
            color: Colors.black.withValues(alpha: 0.4),
          ),

          // 3. Onboarding content
          SafeArea(
            child: Column(
              children: [
                // Progress indicator
                _buildProgressIndicator(
                  onboardingState.currentStep,
                  onboardingState.totalSteps,
                ),

                const SizedBox(height: 32),

                // Persona indicator
                _buildPersonaIndicator(widget.persona),

                const Spacer(),

                // Current question display
                if (onboardingState.currentQuestion != null)
                  _buildQuestionDisplay(onboardingState.currentQuestion!),

                const SizedBox(height: 64),

                // Push-to-talk button
                PushToTalkButton(
                  mode: _isRecording ? AppMode.listening : AppMode.idle,
                  onPressStart: _startRecording,
                  onPressEnd: _stopRecordingAndRespond,
                ),

                const SizedBox(height: 100),
              ],
            ),
          ),

          // 4. Loading overlay
          if (onboardingState.isLoading)
            LoadingOverlay(
              message: '처리 중...',
            ),

          // 5. Error display
          if (onboardingState.errorMessage != null)
            Positioned(
              top: 100,
              left: 16,
              right: 16,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.red[700],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  onboardingState.errorMessage!,
                  style: const TextStyle(color: Colors.white),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator(int current, int total) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
      child: Column(
        children: [
          Row(
            children: List.generate(
              total,
              (index) => Expanded(
                child: Container(
                  height: 4,
                  margin: const EdgeInsets.symmetric(horizontal: 2),
                  decoration: BoxDecoration(
                    color: index < current
                        ? const Color(UIConstants.electricCyan)
                        : Colors.white.withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '질문 $current/$total',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: UIConstants.fontCaption,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPersonaIndicator(PersonaType persona) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: const Color(UIConstants.electricCyan),
          width: 2,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            persona == PersonaType.adam ? Icons.psychology : Icons.favorite,
            color: const Color(UIConstants.electricCyan),
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            persona.displayName,
            style: const TextStyle(
              color: Colors.white,
              fontSize: UIConstants.fontBody,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuestionDisplay(String question) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.2),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          const Icon(
            Icons.chat_bubble_outline,
            color: Color(UIConstants.electricCyan),
            size: 32,
          ),
          const SizedBox(height: 16),
          Text(
            question,
            style: const TextStyle(
              color: Colors.white,
              fontSize: UIConstants.fontBodyLarge,
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          Text(
            '버튼을 길게 눌러 답변해주세요',
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.6),
              fontSize: UIConstants.fontCaption,
            ),
          ),
        ],
      ),
    );
  }
}
