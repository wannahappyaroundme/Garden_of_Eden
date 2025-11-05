/// Goal Progress Tracking Models for Frontend
library;

import 'package:json_annotation/json_annotation.dart';

part 'goal_models.g.dart';

// ==================== Enums ====================

enum MetricType {
  @JsonValue('time')
  time,
  @JsonValue('count')
  count,
  @JsonValue('boolean')
  boolean,
  @JsonValue('rating')
  rating,
  @JsonValue('percentage')
  percentage,
  @JsonValue('custom')
  custom,
}

enum MoodRating {
  @JsonValue(1)
  veryLow,
  @JsonValue(2)
  low,
  @JsonValue(3)
  neutral,
  @JsonValue(4)
  good,
  @JsonValue(5)
  excellent,
}

enum InsightType {
  @JsonValue('achievement')
  achievement,
  @JsonValue('encouragement')
  encouragement,
  @JsonValue('concern')
  concern,
  @JsonValue('suggestion')
  suggestion,
}

// ==================== Goal Metric ====================

@JsonSerializable()
class GoalMetric {
  final String name;
  final double value;
  final String unit;
  @JsonKey(name: 'metric_type')
  final MetricType metricType;
  final DateTime timestamp;

  GoalMetric({
    required this.name,
    required this.value,
    required this.unit,
    this.metricType = MetricType.count,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  factory GoalMetric.fromJson(Map<String, dynamic> json) =>
      _$GoalMetricFromJson(json);

  Map<String, dynamic> toJson() => _$GoalMetricToJson(this);
}

// ==================== Milestone ====================

@JsonSerializable()
class Milestone {
  @JsonKey(name: 'milestone_id')
  final String milestoneId;
  final String description;
  @JsonKey(name: 'target_date')
  final DateTime? targetDate;
  @JsonKey(name: 'is_completed')
  final bool isCompleted;
  @JsonKey(name: 'completed_date')
  final DateTime? completedDate;
  final String? reward;
  final int order;

  Milestone({
    required this.milestoneId,
    required this.description,
    this.targetDate,
    this.isCompleted = false,
    this.completedDate,
    this.reward,
    this.order = 0,
  });

  factory Milestone.fromJson(Map<String, dynamic> json) =>
      _$MilestoneFromJson(json);

  Map<String, dynamic> toJson() => _$MilestoneToJson(this);

  int? get daysUntilTarget {
    if (targetDate == null) return null;
    final now = DateTime.now();
    final difference = targetDate!.difference(now);
    return difference.inDays;
  }

  Milestone copyWith({
    String? milestoneId,
    String? description,
    DateTime? targetDate,
    bool? isCompleted,
    DateTime? completedDate,
    String? reward,
    int? order,
  }) {
    return Milestone(
      milestoneId: milestoneId ?? this.milestoneId,
      description: description ?? this.description,
      targetDate: targetDate ?? this.targetDate,
      isCompleted: isCompleted ?? this.isCompleted,
      completedDate: completedDate ?? this.completedDate,
      reward: reward ?? this.reward,
      order: order ?? this.order,
    );
  }
}

// ==================== Progress Snapshot ====================

@JsonSerializable()
class ProgressSnapshot {
  @JsonKey(name: 'snapshot_id')
  final String snapshotId;
  final DateTime date;
  final List<GoalMetric> metrics;
  final String? reflection;
  @JsonKey(name: 'mood_rating')
  final MoodRating? moodRating;
  @JsonKey(name: 'photo_url')
  final String? photoUrl;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  ProgressSnapshot({
    required this.snapshotId,
    required this.date,
    this.metrics = const [],
    this.reflection,
    this.moodRating,
    this.photoUrl,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory ProgressSnapshot.fromJson(Map<String, dynamic> json) =>
      _$ProgressSnapshotFromJson(json);

  Map<String, dynamic> toJson() => _$ProgressSnapshotToJson(this);

  double? getMetricValue(String metricName) {
    try {
      return metrics.firstWhere((m) => m.name == metricName).value;
    } catch (_) {
      return null;
    }
  }
}

// ==================== Progress Trend ====================

@JsonSerializable()
class ProgressTrend {
  final String direction; // "improving", "declining", "stable"
  final double velocity;
  @JsonKey(name: 'consistency_score')
  final double consistencyScore;
  @JsonKey(name: 'best_streak')
  final int bestStreak;
  @JsonKey(name: 'current_streak')
  final int currentStreak;
  @JsonKey(name: 'total_entries')
  final int totalEntries;
  @JsonKey(name: 'avg_mood')
  final double? avgMood;

  ProgressTrend({
    required this.direction,
    required this.velocity,
    required this.consistencyScore,
    required this.bestStreak,
    required this.currentStreak,
    required this.totalEntries,
    this.avgMood,
  });

  factory ProgressTrend.fromJson(Map<String, dynamic> json) =>
      _$ProgressTrendFromJson(json);

  Map<String, dynamic> toJson() => _$ProgressTrendToJson(this);

  bool get isImproving => direction == 'improving';
  bool get isDeclining => direction == 'declining';
  bool get isStable => direction == 'stable';
}

// ==================== Goal Insight ====================

@JsonSerializable()
class GoalInsight {
  @JsonKey(name: 'type')
  final InsightType insightType;
  final String title;
  final String description;
  final bool actionable;
  final int priority;
  @JsonKey(name: 'generated_at')
  final DateTime generatedAt;

  GoalInsight({
    required this.insightType,
    required this.title,
    required this.description,
    this.actionable = false,
    this.priority = 0,
    DateTime? generatedAt,
  }) : generatedAt = generatedAt ?? DateTime.now();

  factory GoalInsight.fromJson(Map<String, dynamic> json) =>
      _$GoalInsightFromJson(json);

  Map<String, dynamic> toJson() => _$GoalInsightToJson(this);

  bool get isHighPriority => priority >= 2;
  bool get isMediumPriority => priority == 1;
  bool get isLowPriority => priority == 0;
}

// ==================== Goal Progress Tracker ====================

@JsonSerializable()
class GoalProgressTracker {
  @JsonKey(name: 'user_id')
  final String userId;
  @JsonKey(name: 'goal_id')
  final String goalId;
  @JsonKey(name: 'one_thing')
  final String oneThing;
  final String? description;

  @JsonKey(name: 'start_date')
  final DateTime startDate;
  @JsonKey(name: 'target_date')
  final DateTime? targetDate;

  final List<Milestone> milestones;
  final List<ProgressSnapshot> snapshots;

  @JsonKey(name: 'tracked_metrics')
  final List<String> trackedMetrics;
  @JsonKey(name: 'metric_units')
  final Map<String, String> metricUnits;

  @JsonKey(name: 'current_trend')
  final ProgressTrend? currentTrend;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;
  final int version;

  GoalProgressTracker({
    required this.userId,
    required this.goalId,
    required this.oneThing,
    this.description,
    required this.startDate,
    this.targetDate,
    this.milestones = const [],
    this.snapshots = const [],
    this.trackedMetrics = const [],
    this.metricUnits = const {},
    this.currentTrend,
    DateTime? createdAt,
    DateTime? updatedAt,
    this.version = 1,
  })  : createdAt = createdAt ?? DateTime.now(),
        updatedAt = updatedAt ?? DateTime.now();

  factory GoalProgressTracker.fromJson(Map<String, dynamic> json) =>
      _$GoalProgressTrackerFromJson(json);

  Map<String, dynamic> toJson() => _$GoalProgressTrackerToJson(this);

  double get completionPercentage {
    if (milestones.isEmpty) return 0.0;
    final completed = milestones.where((m) => m.isCompleted).length;
    return (completed / milestones.length) * 100;
  }

  int get daysSinceStart {
    final now = DateTime.now();
    return now.difference(startDate).inDays;
  }

  int? get daysUntilTarget {
    if (targetDate == null) return null;
    final now = DateTime.now();
    return targetDate!.difference(now).inDays;
  }

  List<Milestone> get upcomingMilestones {
    return milestones
        .where((m) => !m.isCompleted)
        .toList()
      ..sort((a, b) => a.order.compareTo(b.order));
  }

  List<Milestone> get completedMilestones {
    return milestones.where((m) => m.isCompleted).toList();
  }

  ProgressSnapshot? get mostRecentSnapshot {
    if (snapshots.isEmpty) return null;
    return snapshots.reduce(
      (a, b) => a.date.isAfter(b.date) ? a : b,
    );
  }
}

// ==================== API Response Models ====================

@JsonSerializable()
class GoalSummary {
  final String goal;
  @JsonKey(name: 'goal_id')
  final String goalId;
  @JsonKey(name: 'start_date')
  final String startDate;
  @JsonKey(name: 'target_date')
  final String? targetDate;
  @JsonKey(name: 'days_active')
  final int daysActive;
  @JsonKey(name: 'days_remaining')
  final int? daysRemaining;
  @JsonKey(name: 'completion_percentage')
  final double completionPercentage;
  @JsonKey(name: 'total_entries')
  final int totalEntries;
  final MilestonesSummary milestones;
  final ProgressTrend? trend;
  final List<GoalInsight> insights;
  @JsonKey(name: 'recent_snapshot')
  final ProgressSnapshot? recentSnapshot;

  GoalSummary({
    required this.goal,
    required this.goalId,
    required this.startDate,
    this.targetDate,
    required this.daysActive,
    this.daysRemaining,
    required this.completionPercentage,
    required this.totalEntries,
    required this.milestones,
    this.trend,
    this.insights = const [],
    this.recentSnapshot,
  });

  factory GoalSummary.fromJson(Map<String, dynamic> json) =>
      _$GoalSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$GoalSummaryToJson(this);
}

@JsonSerializable()
class MilestonesSummary {
  final int total;
  final int completed;
  final List<UpcomingMilestone> upcoming;

  MilestonesSummary({
    required this.total,
    required this.completed,
    this.upcoming = const [],
  });

  factory MilestonesSummary.fromJson(Map<String, dynamic> json) =>
      _$MilestonesSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$MilestonesSummaryToJson(this);

  double get completionPercentage {
    if (total == 0) return 0.0;
    return (completed / total) * 100;
  }
}

@JsonSerializable()
class UpcomingMilestone {
  final String id;
  final String description;
  @JsonKey(name: 'target_date')
  final String? targetDate;
  @JsonKey(name: 'days_until')
  final int? daysUntil;

  UpcomingMilestone({
    required this.id,
    required this.description,
    this.targetDate,
    this.daysUntil,
  });

  factory UpcomingMilestone.fromJson(Map<String, dynamic> json) =>
      _$UpcomingMilestoneFromJson(json);

  Map<String, dynamic> toJson() => _$UpcomingMilestoneToJson(this);
}

@JsonSerializable()
class ProgressHistoryResponse {
  @JsonKey(name: 'user_id')
  final String userId;
  final int days;
  @JsonKey(name: 'total_snapshots')
  final int totalSnapshots;
  final List<ProgressSnapshot> snapshots;

  ProgressHistoryResponse({
    required this.userId,
    required this.days,
    required this.totalSnapshots,
    required this.snapshots,
  });

  factory ProgressHistoryResponse.fromJson(Map<String, dynamic> json) =>
      _$ProgressHistoryResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ProgressHistoryResponseToJson(this);
}

@JsonSerializable()
class CreateGoalResponse {
  @JsonKey(name: 'goal_id')
  final String goalId;
  @JsonKey(name: 'one_thing')
  final String oneThing;
  final String? description;
  @JsonKey(name: 'start_date')
  final String startDate;
  @JsonKey(name: 'target_date')
  final String? targetDate;
  @JsonKey(name: 'milestones_count')
  final int milestonesCount;
  final bool created;

  CreateGoalResponse({
    required this.goalId,
    required this.oneThing,
    this.description,
    required this.startDate,
    this.targetDate,
    required this.milestonesCount,
    required this.created,
  });

  factory CreateGoalResponse.fromJson(Map<String, dynamic> json) =>
      _$CreateGoalResponseFromJson(json);

  Map<String, dynamic> toJson() => _$CreateGoalResponseToJson(this);
}

@JsonSerializable()
class RecordProgressResponse {
  final bool success;
  final String message;
  @JsonKey(name: 'recorded_at')
  final String recordedAt;

  RecordProgressResponse({
    required this.success,
    required this.message,
    required this.recordedAt,
  });

  factory RecordProgressResponse.fromJson(Map<String, dynamic> json) =>
      _$RecordProgressResponseFromJson(json);

  Map<String, dynamic> toJson() => _$RecordProgressResponseToJson(this);
}

// ==================== Request Models ====================

@JsonSerializable()
class RecordProgressRequest {
  final String? reflection;
  @JsonKey(name: 'mood_rating')
  final int? moodRating;
  final List<Map<String, dynamic>>? metrics;
  @JsonKey(name: 'photo_url')
  final String? photoUrl;

  RecordProgressRequest({
    this.reflection,
    this.moodRating,
    this.metrics,
    this.photoUrl,
  });

  factory RecordProgressRequest.fromJson(Map<String, dynamic> json) =>
      _$RecordProgressRequestFromJson(json);

  Map<String, dynamic> toJson() => _$RecordProgressRequestToJson(this);
}

@JsonSerializable()
class MetricsConfigRequest {
  final List<String> metrics;
  final Map<String, String> units;

  MetricsConfigRequest({
    required this.metrics,
    required this.units,
  });

  factory MetricsConfigRequest.fromJson(Map<String, dynamic> json) =>
      _$MetricsConfigRequestFromJson(json);

  Map<String, dynamic> toJson() => _$MetricsConfigRequestToJson(this);
}
