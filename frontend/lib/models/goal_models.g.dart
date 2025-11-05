// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'goal_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GoalMetric _$GoalMetricFromJson(Map<String, dynamic> json) => GoalMetric(
  name: json['name'] as String,
  value: (json['value'] as num).toDouble(),
  unit: json['unit'] as String,
  metricType:
      $enumDecodeNullable(_$MetricTypeEnumMap, json['metric_type']) ??
      MetricType.count,
  timestamp: json['timestamp'] == null
      ? null
      : DateTime.parse(json['timestamp'] as String),
);

Map<String, dynamic> _$GoalMetricToJson(GoalMetric instance) =>
    <String, dynamic>{
      'name': instance.name,
      'value': instance.value,
      'unit': instance.unit,
      'metric_type': _$MetricTypeEnumMap[instance.metricType]!,
      'timestamp': instance.timestamp.toIso8601String(),
    };

const _$MetricTypeEnumMap = {
  MetricType.time: 'time',
  MetricType.count: 'count',
  MetricType.boolean: 'boolean',
  MetricType.rating: 'rating',
  MetricType.percentage: 'percentage',
  MetricType.custom: 'custom',
};

Milestone _$MilestoneFromJson(Map<String, dynamic> json) => Milestone(
  milestoneId: json['milestone_id'] as String,
  description: json['description'] as String,
  targetDate: json['target_date'] == null
      ? null
      : DateTime.parse(json['target_date'] as String),
  isCompleted: json['is_completed'] as bool? ?? false,
  completedDate: json['completed_date'] == null
      ? null
      : DateTime.parse(json['completed_date'] as String),
  reward: json['reward'] as String?,
  order: (json['order'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$MilestoneToJson(Milestone instance) => <String, dynamic>{
  'milestone_id': instance.milestoneId,
  'description': instance.description,
  'target_date': instance.targetDate?.toIso8601String(),
  'is_completed': instance.isCompleted,
  'completed_date': instance.completedDate?.toIso8601String(),
  'reward': instance.reward,
  'order': instance.order,
};

ProgressSnapshot _$ProgressSnapshotFromJson(Map<String, dynamic> json) =>
    ProgressSnapshot(
      snapshotId: json['snapshot_id'] as String,
      date: DateTime.parse(json['date'] as String),
      metrics:
          (json['metrics'] as List<dynamic>?)
              ?.map((e) => GoalMetric.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      reflection: json['reflection'] as String?,
      moodRating: $enumDecodeNullable(_$MoodRatingEnumMap, json['mood_rating']),
      photoUrl: json['photo_url'] as String?,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$ProgressSnapshotToJson(ProgressSnapshot instance) =>
    <String, dynamic>{
      'snapshot_id': instance.snapshotId,
      'date': instance.date.toIso8601String(),
      'metrics': instance.metrics,
      'reflection': instance.reflection,
      'mood_rating': _$MoodRatingEnumMap[instance.moodRating],
      'photo_url': instance.photoUrl,
      'created_at': instance.createdAt.toIso8601String(),
    };

const _$MoodRatingEnumMap = {
  MoodRating.veryLow: 1,
  MoodRating.low: 2,
  MoodRating.neutral: 3,
  MoodRating.good: 4,
  MoodRating.excellent: 5,
};

ProgressTrend _$ProgressTrendFromJson(Map<String, dynamic> json) =>
    ProgressTrend(
      direction: json['direction'] as String,
      velocity: (json['velocity'] as num).toDouble(),
      consistencyScore: (json['consistency_score'] as num).toDouble(),
      bestStreak: (json['best_streak'] as num).toInt(),
      currentStreak: (json['current_streak'] as num).toInt(),
      totalEntries: (json['total_entries'] as num).toInt(),
      avgMood: (json['avg_mood'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$ProgressTrendToJson(ProgressTrend instance) =>
    <String, dynamic>{
      'direction': instance.direction,
      'velocity': instance.velocity,
      'consistency_score': instance.consistencyScore,
      'best_streak': instance.bestStreak,
      'current_streak': instance.currentStreak,
      'total_entries': instance.totalEntries,
      'avg_mood': instance.avgMood,
    };

GoalInsight _$GoalInsightFromJson(Map<String, dynamic> json) => GoalInsight(
  insightType: $enumDecode(_$InsightTypeEnumMap, json['type']),
  title: json['title'] as String,
  description: json['description'] as String,
  actionable: json['actionable'] as bool? ?? false,
  priority: (json['priority'] as num?)?.toInt() ?? 0,
  generatedAt: json['generated_at'] == null
      ? null
      : DateTime.parse(json['generated_at'] as String),
);

Map<String, dynamic> _$GoalInsightToJson(GoalInsight instance) =>
    <String, dynamic>{
      'type': _$InsightTypeEnumMap[instance.insightType]!,
      'title': instance.title,
      'description': instance.description,
      'actionable': instance.actionable,
      'priority': instance.priority,
      'generated_at': instance.generatedAt.toIso8601String(),
    };

const _$InsightTypeEnumMap = {
  InsightType.achievement: 'achievement',
  InsightType.encouragement: 'encouragement',
  InsightType.concern: 'concern',
  InsightType.suggestion: 'suggestion',
};

GoalProgressTracker _$GoalProgressTrackerFromJson(Map<String, dynamic> json) =>
    GoalProgressTracker(
      userId: json['user_id'] as String,
      goalId: json['goal_id'] as String,
      oneThing: json['one_thing'] as String,
      description: json['description'] as String?,
      startDate: DateTime.parse(json['start_date'] as String),
      targetDate: json['target_date'] == null
          ? null
          : DateTime.parse(json['target_date'] as String),
      milestones:
          (json['milestones'] as List<dynamic>?)
              ?.map((e) => Milestone.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      snapshots:
          (json['snapshots'] as List<dynamic>?)
              ?.map((e) => ProgressSnapshot.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      trackedMetrics:
          (json['tracked_metrics'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      metricUnits:
          (json['metric_units'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as String),
          ) ??
          const {},
      currentTrend: json['current_trend'] == null
          ? null
          : ProgressTrend.fromJson(
              json['current_trend'] as Map<String, dynamic>,
            ),
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
      version: (json['version'] as num?)?.toInt() ?? 1,
    );

Map<String, dynamic> _$GoalProgressTrackerToJson(
  GoalProgressTracker instance,
) => <String, dynamic>{
  'user_id': instance.userId,
  'goal_id': instance.goalId,
  'one_thing': instance.oneThing,
  'description': instance.description,
  'start_date': instance.startDate.toIso8601String(),
  'target_date': instance.targetDate?.toIso8601String(),
  'milestones': instance.milestones,
  'snapshots': instance.snapshots,
  'tracked_metrics': instance.trackedMetrics,
  'metric_units': instance.metricUnits,
  'current_trend': instance.currentTrend,
  'created_at': instance.createdAt.toIso8601String(),
  'updated_at': instance.updatedAt.toIso8601String(),
  'version': instance.version,
};

GoalSummary _$GoalSummaryFromJson(Map<String, dynamic> json) => GoalSummary(
  goal: json['goal'] as String,
  goalId: json['goal_id'] as String,
  startDate: json['start_date'] as String,
  targetDate: json['target_date'] as String?,
  daysActive: (json['days_active'] as num).toInt(),
  daysRemaining: (json['days_remaining'] as num?)?.toInt(),
  completionPercentage: (json['completion_percentage'] as num).toDouble(),
  totalEntries: (json['total_entries'] as num).toInt(),
  milestones: MilestonesSummary.fromJson(
    json['milestones'] as Map<String, dynamic>,
  ),
  trend: json['trend'] == null
      ? null
      : ProgressTrend.fromJson(json['trend'] as Map<String, dynamic>),
  insights:
      (json['insights'] as List<dynamic>?)
          ?.map((e) => GoalInsight.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  recentSnapshot: json['recent_snapshot'] == null
      ? null
      : ProgressSnapshot.fromJson(
          json['recent_snapshot'] as Map<String, dynamic>,
        ),
);

Map<String, dynamic> _$GoalSummaryToJson(GoalSummary instance) =>
    <String, dynamic>{
      'goal': instance.goal,
      'goal_id': instance.goalId,
      'start_date': instance.startDate,
      'target_date': instance.targetDate,
      'days_active': instance.daysActive,
      'days_remaining': instance.daysRemaining,
      'completion_percentage': instance.completionPercentage,
      'total_entries': instance.totalEntries,
      'milestones': instance.milestones,
      'trend': instance.trend,
      'insights': instance.insights,
      'recent_snapshot': instance.recentSnapshot,
    };

MilestonesSummary _$MilestonesSummaryFromJson(Map<String, dynamic> json) =>
    MilestonesSummary(
      total: (json['total'] as num).toInt(),
      completed: (json['completed'] as num).toInt(),
      upcoming:
          (json['upcoming'] as List<dynamic>?)
              ?.map(
                (e) => UpcomingMilestone.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const [],
    );

Map<String, dynamic> _$MilestonesSummaryToJson(MilestonesSummary instance) =>
    <String, dynamic>{
      'total': instance.total,
      'completed': instance.completed,
      'upcoming': instance.upcoming,
    };

UpcomingMilestone _$UpcomingMilestoneFromJson(Map<String, dynamic> json) =>
    UpcomingMilestone(
      id: json['id'] as String,
      description: json['description'] as String,
      targetDate: json['target_date'] as String?,
      daysUntil: (json['days_until'] as num?)?.toInt(),
    );

Map<String, dynamic> _$UpcomingMilestoneToJson(UpcomingMilestone instance) =>
    <String, dynamic>{
      'id': instance.id,
      'description': instance.description,
      'target_date': instance.targetDate,
      'days_until': instance.daysUntil,
    };

ProgressHistoryResponse _$ProgressHistoryResponseFromJson(
  Map<String, dynamic> json,
) => ProgressHistoryResponse(
  userId: json['user_id'] as String,
  days: (json['days'] as num).toInt(),
  totalSnapshots: (json['total_snapshots'] as num).toInt(),
  snapshots: (json['snapshots'] as List<dynamic>)
      .map((e) => ProgressSnapshot.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$ProgressHistoryResponseToJson(
  ProgressHistoryResponse instance,
) => <String, dynamic>{
  'user_id': instance.userId,
  'days': instance.days,
  'total_snapshots': instance.totalSnapshots,
  'snapshots': instance.snapshots,
};

CreateGoalResponse _$CreateGoalResponseFromJson(Map<String, dynamic> json) =>
    CreateGoalResponse(
      goalId: json['goal_id'] as String,
      oneThing: json['one_thing'] as String,
      description: json['description'] as String?,
      startDate: json['start_date'] as String,
      targetDate: json['target_date'] as String?,
      milestonesCount: (json['milestones_count'] as num).toInt(),
      created: json['created'] as bool,
    );

Map<String, dynamic> _$CreateGoalResponseToJson(CreateGoalResponse instance) =>
    <String, dynamic>{
      'goal_id': instance.goalId,
      'one_thing': instance.oneThing,
      'description': instance.description,
      'start_date': instance.startDate,
      'target_date': instance.targetDate,
      'milestones_count': instance.milestonesCount,
      'created': instance.created,
    };

RecordProgressResponse _$RecordProgressResponseFromJson(
  Map<String, dynamic> json,
) => RecordProgressResponse(
  success: json['success'] as bool,
  message: json['message'] as String,
  recordedAt: json['recorded_at'] as String,
);

Map<String, dynamic> _$RecordProgressResponseToJson(
  RecordProgressResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'message': instance.message,
  'recorded_at': instance.recordedAt,
};

RecordProgressRequest _$RecordProgressRequestFromJson(
  Map<String, dynamic> json,
) => RecordProgressRequest(
  reflection: json['reflection'] as String?,
  moodRating: (json['mood_rating'] as num?)?.toInt(),
  metrics: (json['metrics'] as List<dynamic>?)
      ?.map((e) => e as Map<String, dynamic>)
      .toList(),
  photoUrl: json['photo_url'] as String?,
);

Map<String, dynamic> _$RecordProgressRequestToJson(
  RecordProgressRequest instance,
) => <String, dynamic>{
  'reflection': instance.reflection,
  'mood_rating': instance.moodRating,
  'metrics': instance.metrics,
  'photo_url': instance.photoUrl,
};

MetricsConfigRequest _$MetricsConfigRequestFromJson(
  Map<String, dynamic> json,
) => MetricsConfigRequest(
  metrics: (json['metrics'] as List<dynamic>).map((e) => e as String).toList(),
  units: Map<String, String>.from(json['units'] as Map),
);

Map<String, dynamic> _$MetricsConfigRequestToJson(
  MetricsConfigRequest instance,
) => <String, dynamic>{'metrics': instance.metrics, 'units': instance.units};
