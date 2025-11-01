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

  AppState({
    this.mode = AppMode.idle,
    this.persona = PersonaType.adam,
    this.lastResponse,
    this.errorMessage,
    this.isTTSPlaying = false,
  });

  AppState copyWith({
    AppMode? mode,
    PersonaType? persona,
    ChatResponse? lastResponse,
    String? errorMessage,
    bool? isTTSPlaying,
    bool clearError = false,
    bool clearResponse = false,
  }) {
    return AppState(
      mode: mode ?? this.mode,
      persona: persona ?? this.persona,
      lastResponse: clearResponse ? null : (lastResponse ?? this.lastResponse),
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      isTTSPlaying: isTTSPlaying ?? this.isTTSPlaying,
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

  void reset() {
    state = AppState(persona: state.persona);
  }
}

/// Provider
final appStateProvider = StateNotifierProvider<AppStateNotifier, AppState>((ref) {
  return AppStateNotifier();
});
