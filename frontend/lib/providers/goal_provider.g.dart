// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'goal_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$hasGoalHash() => r'a1309566ad842bed93870d822d27206c2bba2d16';

/// Check if user has a goal
///
/// Copied from [hasGoal].
@ProviderFor(hasGoal)
final hasGoalProvider = AutoDisposeProvider<bool>.internal(
  hasGoal,
  name: r'hasGoalProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$hasGoalHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef HasGoalRef = AutoDisposeProviderRef<bool>;
String _$completionPercentageHash() =>
    r'c28db3d13a342b74779287d8ab009e933f83d48f';

/// Get completion percentage
///
/// Copied from [completionPercentage].
@ProviderFor(completionPercentage)
final completionPercentageProvider = AutoDisposeProvider<double>.internal(
  completionPercentage,
  name: r'completionPercentageProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$completionPercentageHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef CompletionPercentageRef = AutoDisposeProviderRef<double>;
String _$upcomingMilestonesHash() =>
    r'68223fcdd590e964a4b2b18e636f27c976f867bc';

/// Get upcoming milestones
///
/// Copied from [upcomingMilestones].
@ProviderFor(upcomingMilestones)
final upcomingMilestonesProvider =
    AutoDisposeProvider<List<UpcomingMilestone>>.internal(
      upcomingMilestones,
      name: r'upcomingMilestonesProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$upcomingMilestonesHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef UpcomingMilestonesRef = AutoDisposeProviderRef<List<UpcomingMilestone>>;
String _$highPriorityInsightsHash() =>
    r'339bf145003e63c6e404331c8255514ca094544e';

/// Get high priority insights
///
/// Copied from [highPriorityInsights].
@ProviderFor(highPriorityInsights)
final highPriorityInsightsProvider =
    AutoDisposeProvider<List<GoalInsight>>.internal(
      highPriorityInsights,
      name: r'highPriorityInsightsProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$highPriorityInsightsHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef HighPriorityInsightsRef = AutoDisposeProviderRef<List<GoalInsight>>;
String _$currentStreakHash() => r'bca7ca1afd03b914507b4734a98624623d03aadd';

/// Get current streak
///
/// Copied from [currentStreak].
@ProviderFor(currentStreak)
final currentStreakProvider = AutoDisposeProvider<int>.internal(
  currentStreak,
  name: r'currentStreakProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$currentStreakHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef CurrentStreakRef = AutoDisposeProviderRef<int>;
String _$daysUntilTargetHash() => r'f50db2c0a881298306b0ff4ba99bfc68f9986ed4';

/// Get days until target
///
/// Copied from [daysUntilTarget].
@ProviderFor(daysUntilTarget)
final daysUntilTargetProvider = AutoDisposeProvider<int?>.internal(
  daysUntilTarget,
  name: r'daysUntilTargetProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$daysUntilTargetHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef DaysUntilTargetRef = AutoDisposeProviderRef<int?>;
String _$trendDirectionHash() => r'7b83075c1d57461c1b44313b3be57f881711c209';

/// Get progress trend direction
///
/// Copied from [trendDirection].
@ProviderFor(trendDirection)
final trendDirectionProvider = AutoDisposeProvider<String>.internal(
  trendDirection,
  name: r'trendDirectionProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$trendDirectionHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef TrendDirectionRef = AutoDisposeProviderRef<String>;
String _$goalProgressHash() => r'cf23f0ad82b23c3e82c84eeeb21d923345eab9c2';

/// See also [GoalProgress].
@ProviderFor(GoalProgress)
final goalProgressProvider =
    AutoDisposeNotifierProvider<GoalProgress, GoalState>.internal(
      GoalProgress.new,
      name: r'goalProgressProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$goalProgressHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$GoalProgress = AutoDisposeNotifier<GoalState>;
String _$progressEntryHash() => r'89a56c298d13f2095678edc340eec74ab4cddb85';

/// See also [ProgressEntry].
@ProviderFor(ProgressEntry)
final progressEntryProvider =
    AutoDisposeNotifierProvider<ProgressEntry, ProgressEntryState>.internal(
      ProgressEntry.new,
      name: r'progressEntryProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$progressEntryHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$ProgressEntry = AutoDisposeNotifier<ProgressEntryState>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
