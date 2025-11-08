/// Wake Word Provider using Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/wake_word_service.dart';
import '../services/background_wake_word_service.dart';
import '../utils/constants.dart';

/// Wake Word State
class WakeWordState {
  final bool isInitialized;
  final bool isListening;
  final bool isEnabled;
  final bool isBackgroundEnabled;
  final PersonaType activePersona;
  final String? errorMessage;

  const WakeWordState({
    this.isInitialized = false,
    this.isListening = false,
    this.isEnabled = false,
    this.isBackgroundEnabled = false,
    this.activePersona = PersonaType.adam,
    this.errorMessage,
  });

  WakeWordState copyWith({
    bool? isInitialized,
    bool? isListening,
    bool? isEnabled,
    bool? isBackgroundEnabled,
    PersonaType? activePersona,
    String? errorMessage,
    bool clearError = false,
  }) {
    return WakeWordState(
      isInitialized: isInitialized ?? this.isInitialized,
      isListening: isListening ?? this.isListening,
      isEnabled: isEnabled ?? this.isEnabled,
      isBackgroundEnabled: isBackgroundEnabled ?? this.isBackgroundEnabled,
      activePersona: activePersona ?? this.activePersona,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

/// Wake Word Notifier
class WakeWordNotifier extends StateNotifier<WakeWordState> {
  final WakeWordService _service;
  final BackgroundWakeWordService _backgroundService;
  final Function(PersonaType)? onWakeWordDetected;

  WakeWordNotifier({
    required WakeWordService service,
    required BackgroundWakeWordService backgroundService,
    this.onWakeWordDetected,
  })  : _service = service,
        _backgroundService = backgroundService,
        super(const WakeWordState());

  /// Initialize wake word detection
  Future<void> initialize(PersonaType persona) async {
    try {
      await _service.initialize(
        persona: persona,
        onDetected: (detectedPersona) {
          if (onWakeWordDetected != null) {
            onWakeWordDetected!(detectedPersona);
          }
        },
        onErrorCallback: (error) {
          state = state.copyWith(
            errorMessage: error.message,
            isListening: false,
          );
        },
      );

      state = state.copyWith(
        isInitialized: true,
        activePersona: persona,
        clearError: true,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
        isInitialized: false,
      );
    }
  }

  /// Start listening for wake word
  Future<void> startListening() async {
    if (!state.isInitialized || state.isListening) {
      return;
    }

    try {
      await _service.startListening();
      state = state.copyWith(
        isListening: true,
        isEnabled: true,
        clearError: true,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: 'Failed to start wake word: ${e.toString()}',
        isListening: false,
      );
    }
  }

  /// Stop listening for wake word
  Future<void> stopListening() async {
    if (!state.isListening) {
      return;
    }

    try {
      await _service.stopListening();
      state = state.copyWith(
        isListening: false,
        clearError: true,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: 'Failed to stop wake word: ${e.toString()}',
      );
    }
  }

  /// Toggle wake word on/off
  Future<void> toggle() async {
    if (state.isListening) {
      await stopListening();
    } else {
      await startListening();
    }
  }

  /// Switch persona (currently not supported - only Adam on Android)
  Future<void> switchPersona(PersonaType persona) async {
    if (persona != PersonaType.adam) {
      state = state.copyWith(
        errorMessage: 'Currently only Adam persona is supported for wake word',
      );
      return;
    }

    // If same persona, do nothing
    if (state.activePersona == persona) {
      return;
    }

    // Stop current listening
    await stopListening();

    // Reinitialize with new persona
    await initialize(persona);

    // Restart if it was enabled before
    if (state.isEnabled) {
      await startListening();
    }
  }

  /// Enable background listening
  Future<void> enableBackground() async {
    if (!state.isInitialized) {
      state = state.copyWith(
        errorMessage: 'Wake word must be initialized first',
      );
      return;
    }

    try {
      // Initialize background service
      await _backgroundService.initialize();

      // Start background listening
      final started = await _backgroundService.startBackgroundListening(state.activePersona);

      if (started) {
        state = state.copyWith(
          isBackgroundEnabled: true,
          clearError: true,
        );
      } else {
        state = state.copyWith(
          errorMessage: 'Failed to start background listening',
        );
      }
    } catch (e) {
      state = state.copyWith(
        errorMessage: 'Background error: ${e.toString()}',
      );
    }
  }

  /// Disable background listening
  Future<void> disableBackground() async {
    if (!state.isBackgroundEnabled) {
      return;
    }

    try {
      await _backgroundService.stopBackgroundListening();
      state = state.copyWith(
        isBackgroundEnabled: false,
        clearError: true,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: 'Failed to stop background: ${e.toString()}',
      );
    }
  }

  /// Toggle background listening
  Future<void> toggleBackground() async {
    if (state.isBackgroundEnabled) {
      await disableBackground();
    } else {
      await enableBackground();
    }
  }

  /// Clear error message
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  /// Dispose
  @override
  Future<void> dispose() async {
    await disableBackground();
    await _service.dispose();
    super.dispose();
  }
}

/// Wake Word Service Provider (singleton)
final wakeWordServiceProvider = Provider<WakeWordService>((ref) {
  return WakeWordService();
});

/// Background Wake Word Service Provider (singleton)
final backgroundWakeWordServiceProvider = Provider<BackgroundWakeWordService>((ref) {
  return BackgroundWakeWordService();
});

/// Wake Word State Provider
final wakeWordProvider = StateNotifierProvider<WakeWordNotifier, WakeWordState>((ref) {
  final service = ref.watch(wakeWordServiceProvider);
  final backgroundService = ref.watch(backgroundWakeWordServiceProvider);

  final notifier = WakeWordNotifier(
    service: service,
    backgroundService: backgroundService,
    // onWakeWordDetected will be set by the screen
  );

  ref.onDispose(() {
    notifier.dispose();
  });

  return notifier;
});
