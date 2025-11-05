/// Goal Progress Provider - State management for goal tracking
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/goal_models.dart';
import '../services/api_service.dart';
import 'service_providers.dart';

part 'goal_provider.g.dart';

// ==================== Goal State ====================

class GoalState {
  final GoalSummary? summary;
  final ProgressHistoryResponse? history;
  final List<GoalInsight> insights;
  final bool isLoading;
  final String? error;
  final DateTime? lastRefresh;

  GoalState({
    this.summary,
    this.history,
    this.insights = const [],
    this.isLoading = false,
    this.error,
    this.lastRefresh,
  });

  GoalState copyWith({
    GoalSummary? summary,
    ProgressHistoryResponse? history,
    List<GoalInsight>? insights,
    bool? isLoading,
    String? error,
    DateTime? lastRefresh,
  }) {
    return GoalState(
      summary: summary ?? this.summary,
      history: history ?? this.history,
      insights: insights ?? this.insights,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      lastRefresh: lastRefresh ?? this.lastRefresh,
    );
  }

  bool get hasGoal => summary != null;
  bool get needsRefresh {
    if (lastRefresh == null) return true;
    final now = DateTime.now();
    final difference = now.difference(lastRefresh!);
    return difference.inMinutes > 5; // Refresh every 5 minutes
  }
}

// ==================== Goal Progress Notifier ====================

@riverpod
class GoalProgress extends _$GoalProgress {
  ApiService get _api => ref.read(apiServiceProvider);

  @override
  GoalState build() {
    return GoalState();
  }

  // ==================== Goal Creation ====================

  /// Create a new goal from user's One Thing
  Future<bool> createGoal({
    required String userId,
    String? targetDate,
    String? description,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _api.createGoal(
        userId: userId,
        targetDate: targetDate,
        description: description,
      );

      // Immediately load the goal summary
      await loadGoalSummary(userId);

      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '목표 생성 실패: ${e.toString()}',
      );
      return false;
    }
  }

  // ==================== Goal Loading ====================

  /// Load goal summary with insights
  Future<void> loadGoalSummary(String userId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final summary = await _api.getGoalSummary(userId);

      state = state.copyWith(
        summary: summary,
        insights: summary.insights,
        isLoading: false,
        lastRefresh: DateTime.now(),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString().contains('404')
            ? '목표가 설정되지 않았습니다'
            : '목표를 불러오지 못했습니다: ${e.toString()}',
      );
    }
  }

  /// Load progress history
  Future<void> loadProgressHistory(String userId, {int days = 30}) async {
    try {
      final history = await _api.getProgressHistory(
        userId: userId,
        days: days,
      );

      state = state.copyWith(history: history);
    } catch (e) {
      // Don't show error for history load failure, just log
      print('Failed to load progress history: $e');
    }
  }

  /// Refresh all goal data
  Future<void> refresh(String userId) async {
    await Future.wait([
      loadGoalSummary(userId),
      loadProgressHistory(userId),
    ]);
  }

  // ==================== Progress Recording ====================

  /// Record daily progress snapshot
  Future<bool> recordProgress({
    required String userId,
    String? reflection,
    int? moodRating,
    List<Map<String, dynamic>>? metrics,
    String? photoUrl,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      await _api.recordProgress(
        userId: userId,
        reflection: reflection,
        moodRating: moodRating,
        metrics: metrics,
        photoUrl: photoUrl,
      );

      // Refresh goal data after recording
      await refresh(userId);

      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '진행 상황 기록 실패: ${e.toString()}',
      );
      return false;
    }
  }

  // ==================== Milestone Management ====================

  /// Toggle milestone completion status
  Future<bool> toggleMilestone({
    required String userId,
    required String milestoneId,
    required bool isCompleted,
  }) async {
    try {
      await _api.updateMilestoneStatus(
        userId: userId,
        milestoneId: milestoneId,
        isCompleted: isCompleted,
      );

      // Optimistically update UI
      if (state.summary != null) {
        // Reload to get accurate data
        await loadGoalSummary(userId);
      }

      return true;
    } catch (e) {
      state = state.copyWith(
        error: '마일스톤 업데이트 실패: ${e.toString()}',
      );
      return false;
    }
  }

  /// Add a custom milestone
  Future<bool> addMilestone({
    required String userId,
    required String description,
    String? targetDate,
    String? reward,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      await _api.addMilestone(
        userId: userId,
        description: description,
        targetDate: targetDate,
        reward: reward,
      );

      // Refresh goal data
      await loadGoalSummary(userId);

      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '마일스톤 추가 실패: ${e.toString()}',
      );
      return false;
    }
  }

  // ==================== Metrics Configuration ====================

  /// Setup tracked metrics
  Future<bool> setupMetrics({
    required String userId,
    required List<String> metricNames,
    required Map<String, String> metricUnits,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      await _api.setupTrackedMetrics(
        userId: userId,
        metricNames: metricNames,
        metricUnits: metricUnits,
      );

      // Refresh goal data
      await loadGoalSummary(userId);

      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '메트릭 설정 실패: ${e.toString()}',
      );
      return false;
    }
  }

  // ==================== AI Insights ====================

  /// Generate fresh AI insights
  Future<bool> generateInsights(String userId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final insights = await _api.generateInsights(userId: userId);

      state = state.copyWith(
        insights: insights,
        isLoading: false,
        lastRefresh: DateTime.now(),
      );

      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '인사이트 생성 실패: ${e.toString()}',
      );
      return false;
    }
  }

  // ==================== Helpers ====================

  /// Clear error message
  void clearError() {
    state = state.copyWith(error: null);
  }

  /// Clear all goal data (e.g., on logout)
  void clear() {
    state = GoalState();
  }
}

// ==================== Quick Access Providers ====================

/// Check if user has a goal
@riverpod
bool hasGoal(HasGoalRef ref) {
  final goalState = ref.watch(goalProgressProvider);
  return goalState.hasGoal;
}

/// Get completion percentage
@riverpod
double completionPercentage(CompletionPercentageRef ref) {
  final goalState = ref.watch(goalProgressProvider);
  return goalState.summary?.completionPercentage ?? 0.0;
}

/// Get upcoming milestones
@riverpod
List<UpcomingMilestone> upcomingMilestones(UpcomingMilestonesRef ref) {
  final goalState = ref.watch(goalProgressProvider);
  return goalState.summary?.milestones.upcoming ?? [];
}

/// Get high priority insights
@riverpod
List<GoalInsight> highPriorityInsights(HighPriorityInsightsRef ref) {
  final goalState = ref.watch(goalProgressProvider);
  return goalState.insights.where((i) => i.isHighPriority).toList();
}

/// Get current streak
@riverpod
int currentStreak(CurrentStreakRef ref) {
  final goalState = ref.watch(goalProgressProvider);
  return goalState.summary?.trend?.currentStreak ?? 0;
}

/// Get days until target
@riverpod
int? daysUntilTarget(DaysUntilTargetRef ref) {
  final goalState = ref.watch(goalProgressProvider);
  return goalState.summary?.daysRemaining;
}

/// Get progress trend direction
@riverpod
String trendDirection(TrendDirectionRef ref) {
  final goalState = ref.watch(goalProgressProvider);
  return goalState.summary?.trend?.direction ?? 'stable';
}

// ==================== Progress Entry Form State ====================

class ProgressEntryState {
  final String? reflection;
  final int? moodRating;
  final List<GoalMetric> metrics;
  final String? photoUrl;

  ProgressEntryState({
    this.reflection,
    this.moodRating,
    this.metrics = const [],
    this.photoUrl,
  });

  ProgressEntryState copyWith({
    String? reflection,
    int? moodRating,
    List<GoalMetric>? metrics,
    String? photoUrl,
  }) {
    return ProgressEntryState(
      reflection: reflection ?? this.reflection,
      moodRating: moodRating ?? this.moodRating,
      metrics: metrics ?? this.metrics,
      photoUrl: photoUrl ?? this.photoUrl,
    );
  }

  bool get isValid => reflection != null || metrics.isNotEmpty;

  List<Map<String, dynamic>> get metricsJson {
    return metrics.map((m) => {
      'name': m.name,
      'value': m.value,
      'unit': m.unit,
      'metric_type': m.metricType.name,
    }).toList();
  }
}

@riverpod
class ProgressEntry extends _$ProgressEntry {
  @override
  ProgressEntryState build() {
    return ProgressEntryState();
  }

  void setReflection(String reflection) {
    state = state.copyWith(reflection: reflection);
  }

  void setMoodRating(int rating) {
    state = state.copyWith(moodRating: rating);
  }

  void addMetric(GoalMetric metric) {
    state = state.copyWith(
      metrics: [...state.metrics, metric],
    );
  }

  void removeMetric(int index) {
    final metrics = List<GoalMetric>.from(state.metrics);
    metrics.removeAt(index);
    state = state.copyWith(metrics: metrics);
  }

  void setPhotoUrl(String url) {
    state = state.copyWith(photoUrl: url);
  }

  void clear() {
    state = ProgressEntryState();
  }
}
