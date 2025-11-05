/// Onboarding State Provider using Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/chat_models.dart';
import '../services/api_service.dart';
import '../services/cache_service.dart';
import '../utils/user_id_generator.dart';
import '../utils/constants.dart';
import 'service_providers.dart';

/// Onboarding State
class OnboardingState {
  final String? sessionId;
  final String? userId;
  final int currentStep;
  final int totalSteps;
  final String? currentQuestion;
  final bool isCompleted;
  final bool isLoading;
  final String? errorMessage;
  final OnboardingResult? result;
  final PersonaType persona;

  OnboardingState({
    this.sessionId,
    this.userId,
    this.currentStep = 0,
    this.totalSteps = 6,
    this.currentQuestion,
    this.isCompleted = false,
    this.isLoading = false,
    this.errorMessage,
    this.result,
    this.persona = PersonaType.adam,
  });

  OnboardingState copyWith({
    String? sessionId,
    String? userId,
    int? currentStep,
    int? totalSteps,
    String? currentQuestion,
    bool? isCompleted,
    bool? isLoading,
    String? errorMessage,
    OnboardingResult? result,
    PersonaType? persona,
    bool clearError = false,
  }) {
    return OnboardingState(
      sessionId: sessionId ?? this.sessionId,
      userId: userId ?? this.userId,
      currentStep: currentStep ?? this.currentStep,
      totalSteps: totalSteps ?? this.totalSteps,
      currentQuestion: currentQuestion ?? this.currentQuestion,
      isCompleted: isCompleted ?? this.isCompleted,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      result: result ?? this.result,
      persona: persona ?? this.persona,
    );
  }
}

/// Onboarding State Notifier
class OnboardingNotifier extends StateNotifier<OnboardingState> {
  final ApiService _apiService;
  final CacheService _cacheService;

  OnboardingNotifier(this._apiService, this._cacheService) : super(OnboardingState());

  /// Initialize onboarding - Check if user has completed or resumed session
  Future<void> initialize() async {
    // Check if onboarding already completed
    final isCompleted = await _cacheService.isOnboardingCompleted();
    if (isCompleted) {
      state = state.copyWith(isCompleted: true);
      return;
    }

    // Check if there's a saved session to resume
    final savedSessionId = await _cacheService.loadOnboardingSessionId();
    if (savedSessionId != null) {
      // Try to resume session
      await _resumeSession(savedSessionId);
    }
  }

  /// Start new onboarding session
  Future<void> startOnboarding(PersonaType persona) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      // Generate or load user ID
      String userId = await _cacheService.loadUserId() ?? UserIdGenerator.generate();
      await _cacheService.saveUserId(userId);

      // Start onboarding session with backend
      final response = await _apiService.startOnboarding(
        userId: userId,
        persona: persona,
      );

      // Save session ID for resuming
      await _cacheService.saveOnboardingSessionId(response.sessionId);

      state = state.copyWith(
        sessionId: response.sessionId,
        userId: userId,
        currentStep: response.step ?? 1,
        totalSteps: response.totalSteps ?? 6,
        currentQuestion: response.question,
        isLoading: false,
        persona: persona,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '온보딩 시작 실패: ${e.toString()}',
      );
    }
  }

  /// Respond to onboarding question
  Future<void> respondToQuestion(String userResponse) async {
    if (state.sessionId == null) {
      state = state.copyWith(errorMessage: '세션 ID가 없습니다');
      return;
    }

    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final response = await _apiService.respondToOnboarding(
        sessionId: state.sessionId!,
        userResponse: userResponse,
      );

      if (response.completed) {
        // Onboarding completed!
        await _cacheService.setOnboardingCompleted(true);
        await _cacheService.clearOnboardingSessionId();

        state = state.copyWith(
          isCompleted: true,
          isLoading: false,
          result: response.result,
          currentQuestion: response.message,
        );
      } else {
        // Move to next question
        state = state.copyWith(
          currentStep: response.step ?? state.currentStep + 1,
          currentQuestion: response.question ?? response.message,
          isLoading: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '응답 전송 실패: ${e.toString()}',
      );
    }
  }

  /// Resume existing session
  Future<void> _resumeSession(String sessionId) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final status = await _apiService.getOnboardingStatus(sessionId);

      state = state.copyWith(
        sessionId: sessionId,
        currentStep: status['current_step'] ?? 1,
        isCompleted: status['completed'] ?? false,
        isLoading: false,
      );
    } catch (e) {
      // If resume fails, clear the saved session and start fresh
      await _cacheService.clearOnboardingSessionId();
      state = state.copyWith(isLoading: false, clearError: true);
    }
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  /// Reset onboarding (for testing)
  Future<void> reset() async {
    await _cacheService.setOnboardingCompleted(false);
    await _cacheService.clearOnboardingSessionId();
    state = OnboardingState();
  }
}

/// Onboarding Provider
final onboardingProvider = StateNotifierProvider<OnboardingNotifier, OnboardingState>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  final cacheService = CacheService(); // Singleton
  return OnboardingNotifier(apiService, cacheService);
});
