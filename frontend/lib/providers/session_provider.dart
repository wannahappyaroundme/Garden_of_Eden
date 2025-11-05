/// Session State Provider using Riverpod
library;

import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/chat_models.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';
import 'service_providers.dart';

/// Session State
class SessionState {
  final SessionInfo? currentSession;
  final bool isActive;
  final bool isLoading;
  final String? errorMessage;
  final int turnCount;
  final DateTime? lastActivity;

  SessionState({
    this.currentSession,
    this.isActive = false,
    this.isLoading = false,
    this.errorMessage,
    this.turnCount = 0,
    this.lastActivity,
  });

  SessionState copyWith({
    SessionInfo? currentSession,
    bool? isActive,
    bool? isLoading,
    String? errorMessage,
    int? turnCount,
    DateTime? lastActivity,
    bool clearError = false,
    bool clearSession = false,
  }) {
    return SessionState(
      currentSession: clearSession ? null : (currentSession ?? this.currentSession),
      isActive: isActive ?? this.isActive,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      turnCount: turnCount ?? this.turnCount,
      lastActivity: lastActivity ?? this.lastActivity,
    );
  }

  bool get needsRefresh {
    if (currentSession == null) return false;
    return currentSession!.needsRefresh();
  }
}

/// Session State Notifier
class SessionNotifier extends StateNotifier<SessionState> {
  final ApiService _apiService;
  Timer? _refreshTimer;

  SessionNotifier(this._apiService) : super(SessionState()) {
    _startRefreshTimer();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  /// Start session refresh timer (checks every minute)
  void _startRefreshTimer() {
    _refreshTimer = Timer.periodic(const Duration(minutes: 1), (_) {
      if (state.needsRefresh && state.currentSession != null) {
        _autoRefreshSession();
      }
    });
  }

  /// Auto-refresh session if close to expiration
  Future<void> _autoRefreshSession() async {
    if (state.currentSession == null) return;

    try {
      // Create new session with same user/persona
      final newSession = await _apiService.createSession(
        userId: state.currentSession!.userId,
        persona: PersonaType.values.firstWhere(
          (p) => p.name == state.currentSession!.persona,
          orElse: () => PersonaType.adam,
        ),
      );

      state = state.copyWith(
        currentSession: newSession,
        isActive: true,
        lastActivity: DateTime.now(),
      );
    } catch (e) {
      // Silent fail - user will create new session on next message
      state = state.copyWith(clearSession: true, isActive: false);
    }
  }

  /// Initialize - Check for existing active session
  Future<void> initialize(String userId) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final activeSession = await _apiService.getUserActiveSession(userId);

      if (activeSession != null && !activeSession.isExpired) {
        state = state.copyWith(
          currentSession: activeSession,
          isActive: true,
          turnCount: activeSession.turnCount,
          lastActivity: activeSession.lastActivity,
          isLoading: false,
        );
      } else {
        state = state.copyWith(isLoading: false, isActive: false);
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '세션 초기화 실패: ${e.toString()}',
      );
    }
  }

  /// Create new session
  Future<SessionInfo?> createSession({
    required String userId,
    required PersonaType persona,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final session = await _apiService.createSession(
        userId: userId,
        persona: persona,
      );

      state = state.copyWith(
        currentSession: session,
        isActive: true,
        turnCount: 0,
        lastActivity: DateTime.now(),
        isLoading: false,
      );

      return session;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '세션 생성 실패: ${e.toString()}',
      );
      return null;
    }
  }

  /// Get current session ID (create if needed)
  Future<String?> getOrCreateSessionId({
    required String userId,
    required PersonaType persona,
  }) async {
    // If session exists and is active, return it
    if (state.currentSession != null && !state.currentSession!.isExpired) {
      return state.currentSession!.sessionId;
    }

    // Otherwise create new session
    final session = await createSession(userId: userId, persona: persona);
    return session?.sessionId;
  }

  /// Update session after conversation turn
  void incrementTurnCount() {
    state = state.copyWith(
      turnCount: state.turnCount + 1,
      lastActivity: DateTime.now(),
    );
  }

  /// Close current session
  Future<void> closeSession({String reason = 'User ended conversation'}) async {
    if (state.currentSession == null) return;

    try {
      await _apiService.closeSession(
        sessionId: state.currentSession!.sessionId,
        reason: reason,
      );

      state = state.copyWith(
        clearSession: true,
        isActive: false,
        turnCount: 0,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: '세션 종료 실패: ${e.toString()}',
      );
    }
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  /// Reset session state
  void reset() {
    state = SessionState();
  }
}

/// Session Provider
final sessionProvider = StateNotifierProvider<SessionNotifier, SessionState>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return SessionNotifier(apiService);
});
