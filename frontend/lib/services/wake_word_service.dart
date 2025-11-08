/// Wake Word Detection Service using Porcupine
library;

import 'dart:io' show Platform;
import 'package:porcupine_flutter/porcupine_manager.dart';
import 'package:porcupine_flutter/porcupine_error.dart';
import '../utils/constants.dart';

/// Wake word detection service for "Hey Adam" and "Hey Eve"
class WakeWordService {
  PorcupineManager? _porcupineManager;
  bool _isListening = false;
  PersonaType _activePersona = PersonaType.adam;

  // Callbacks
  Function(PersonaType)? onWakeWordDetected;
  Function(PorcupineException)? onError;

  /// Initialize the wake word service
  Future<void> initialize({
    required PersonaType persona,
    required Function(PersonaType) onDetected,
    Function(PorcupineException)? onErrorCallback,
  }) async {
    _activePersona = persona;
    onWakeWordDetected = onDetected;
    onError = onErrorCallback;

    try {
      // Get the appropriate wake word model file based on platform and persona
      final keywordPath = await _getKeywordPath(persona);

      // Create Porcupine manager
      _porcupineManager = await PorcupineManager.fromKeywordPaths(
        // Picovoice Access Key (you need to get this from Picovoice Console)
        // For now, using empty string - will need to be replaced
        'atzIyNSvFrv+IfmELJ0Kjt3+7O/aUr5vpCtCAXmeo+FzDZzYOn43Ew==',
        [keywordPath],
        _wakeWordCallback,
        errorCallback: _errorCallback,
      );

      // Wake word service initialized successfully
    } catch (e) {
      // Failed to initialize wake word service
      if (e is PorcupineException && onError != null) {
        onError!(e);
      }
    }
  }

  /// Get the appropriate keyword file path based on platform and persona
  Future<String> _getKeywordPath(PersonaType persona) async {
    // Currently only supporting Android + Hey Adam
    if (!Platform.isAndroid) {
      throw UnsupportedError('Wake word is currently only supported on Android');
    }

    if (persona != PersonaType.adam) {
      throw UnsupportedError('Wake word is currently only available for Adam persona');
    }

    return 'assets/wake_words/hey_adam_android.ppn';
  }

  /// Start listening for wake word
  Future<void> startListening() async {
    if (_isListening || _porcupineManager == null) {
      return;
    }

    try {
      await _porcupineManager!.start();
      _isListening = true;
      // Wake word listening started
    } catch (e) {
      // Failed to start wake word listening
      if (e is PorcupineException && onError != null) {
        onError!(e);
      }
    }
  }

  /// Stop listening for wake word
  Future<void> stopListening() async {
    if (!_isListening || _porcupineManager == null) {
      return;
    }

    try {
      await _porcupineManager!.stop();
      _isListening = false;
      // Wake word listening stopped
    } catch (e) {
      // Failed to stop wake word listening
    }
  }

  /// Switch active persona (changes the wake word)
  Future<void> switchPersona(PersonaType persona) async {
    if (persona == _activePersona) {
      return;
    }

    // Stop current listening
    await stopListening();

    // Dispose current manager
    await dispose();

    // Reinitialize with new persona
    await initialize(
      persona: persona,
      onDetected: onWakeWordDetected!,
      onErrorCallback: onError,
    );

    // Restart listening
    await startListening();
  }

  /// Callback when wake word is detected
  void _wakeWordCallback(int keywordIndex) {
    // Wake word detected - currently we only have one keyword per instance
    // (Hey Adam or Hey Eve) so keywordIndex will always be 0
    if (onWakeWordDetected != null) {
      onWakeWordDetected!(_activePersona);
    }
  }

  /// Callback for errors
  void _errorCallback(PorcupineException error) {
    // Wake word error occurred
    if (onError != null) {
      onError!(error);
    }
  }

  /// Dispose the service
  Future<void> dispose() async {
    await stopListening();

    if (_porcupineManager != null) {
      await _porcupineManager!.delete();
      _porcupineManager = null;
    }
  }

  /// Check if currently listening
  bool get isListening => _isListening;

  /// Get active persona
  PersonaType get activePersona => _activePersona;
}
