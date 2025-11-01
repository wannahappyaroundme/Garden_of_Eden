/// App State Provider using Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/chat_models.dart';
import '../utils/constants.dart';

/// App State
class AppState {
  final AppMode mode;
  final PersonaType persona;
  final ChatResponse? lastResponse;
  final String? errorMessage;
  final bool isTTSPlaying;
  final int retryAttempt;
  final String? loadingMessage;
  final bool showPitfallWarning;
  final String? pitfallMessage;

  AppState({
    this.mode = AppMode.idle,
    this.persona = PersonaType.adam,
    this.lastResponse,
    this.errorMessage,
    this.isTTSPlaying = false,
    this.retryAttempt = 0,
    this.loadingMessage,
    this.showPitfallWarning = false,
    this.pitfallMessage,
  });

  AppState copyWith({
    AppMode? mode,
    PersonaType? persona,
    ChatResponse? lastResponse,
    String? errorMessage,
    bool? isTTSPlaying,
    int? retryAttempt,
    String? loadingMessage,
    bool? showPitfallWarning,
    String? pitfallMessage,
    bool clearError = false,
    bool clearResponse = false,
    bool clearLoading = false,
    bool clearPitfall = false,
  }) {
    return AppState(
      mode: mode ?? this.mode,
      persona: persona ?? this.persona,
      lastResponse: clearResponse ? null : (lastResponse ?? this.lastResponse),
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      isTTSPlaying: isTTSPlaying ?? this.isTTSPlaying,
      retryAttempt: retryAttempt ?? this.retryAttempt,
      loadingMessage: clearLoading ? null : (loadingMessage ?? this.loadingMessage),
      showPitfallWarning: clearPitfall ? false : (showPitfallWarning ?? this.showPitfallWarning),
      pitfallMessage: clearPitfall ? null : (pitfallMessage ?? this.pitfallMessage),
    );
  }
}

/// App State Notifier
class AppStateNotifier extends StateNotifier<AppState> {
  AppStateNotifier() : super(AppState());

  void setMode(AppMode mode) {
    state = state.copyWith(mode: mode);
  }

  void setPersona(PersonaType persona) {
    state = state.copyWith(persona: persona);
  }

  void setLastResponse(ChatResponse response) {
    state = state.copyWith(lastResponse: response);
  }

  void setError(String error) {
    state = state.copyWith(errorMessage: error);
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }

  void clearResponse() {
    state = state.copyWith(clearResponse: true);
  }

  void setTTSPlaying(bool playing) {
    state = state.copyWith(isTTSPlaying: playing);
  }

  void setRetryAttempt(int attempt) {
    state = state.copyWith(retryAttempt: attempt);
  }

  void setLoadingMessage(String message) {
    state = state.copyWith(loadingMessage: message);
  }

  void clearLoadingMessage() {
    state = state.copyWith(clearLoading: true);
  }

  void showPitfall(String message) {
    state = state.copyWith(
      showPitfallWarning: true,
      pitfallMessage: message,
    );
  }

  void hidePitfall() {
    state = state.copyWith(clearPitfall: true);
  }

  void reset() {
    state = AppState(persona: state.persona);
  }
}

/// Provider
final appStateProvider = StateNotifierProvider<AppStateNotifier, AppState>((ref) {
  return AppStateNotifier();
});
