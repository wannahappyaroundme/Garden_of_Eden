/// Goal Progress Screen - Track and visualize goal progress
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/goal_models.dart';
import '../providers/goal_provider.dart';
import '../utils/constants.dart';
import '../widgets/milestone_card.dart';
import '../widgets/insight_card.dart';
import '../widgets/progress_stats_card.dart';

class GoalScreen extends ConsumerStatefulWidget {
  final String userId;

  const GoalScreen({
    super.key,
    required this.userId,
  });

  @override
  ConsumerState<GoalScreen> createState() => _GoalScreenState();
}

class _GoalScreenState extends ConsumerState<GoalScreen> {
  @override
  void initState() {
    super.initState();
    // Load goal data on init
    Future.microtask(() {
      ref.read(goalProgressProvider.notifier).loadGoalSummary(widget.userId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final goalState = ref.watch(goalProgressProvider);

    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'My Goal',
          style: TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: () {
              ref.read(goalProgressProvider.notifier).refresh(widget.userId);
            },
          ),
          IconButton(
            icon: const Icon(Icons.add, color: Colors.white),
            onPressed: () => _showRecordProgressDialog(),
          ),
        ],
      ),
      body: goalState.isLoading && !goalState.hasGoal
          ? const Center(
              child: CircularProgressIndicator(
                color: Color(UIConstants.electricCyan),
              ),
            )
          : goalState.error != null && !goalState.hasGoal
              ? _buildErrorState(goalState.error!)
              : !goalState.hasGoal
                  ? _buildNoGoalState()
                  : _buildGoalView(goalState),
    );
  }

  Widget _buildNoGoalState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(UIConstants.spacingXXL),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: const Color(UIConstants.darkGrey),
                borderRadius: BorderRadius.circular(60),
              ),
              child: const Icon(
                Icons.flag_outlined,
                size: 60,
                color: Color(UIConstants.electricCyan),
              ),
            ),
            const SizedBox(height: UIConstants.spacingXXL),
            const Text(
              '아직 목표가 설정되지 않았습니다',
              style: TextStyle(
                color: Colors.white,
                fontSize: UIConstants.fontHeadline,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: UIConstants.spacingMD),
            Text(
              '프로필의 "One Thing"으로부터\n목표를 생성할 수 있습니다',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: UIConstants.fontBody,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: UIConstants.spacingXXL),
            ElevatedButton.icon(
              onPressed: () => _showCreateGoalDialog(),
              icon: const Icon(Icons.add),
              label: const Text('목표 생성하기'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(UIConstants.electricCyan),
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(
                  horizontal: UIConstants.spacingXL,
                  vertical: UIConstants.spacingMD,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(UIConstants.spacingXL),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: UIConstants.spacingLG),
            Text(
              error,
              style: const TextStyle(
                color: Colors.white,
                fontSize: UIConstants.fontBody,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: UIConstants.spacingXL),
            ElevatedButton(
              onPressed: () {
                ref.read(goalProgressProvider.notifier).clearError();
                ref.read(goalProgressProvider.notifier).loadGoalSummary(widget.userId);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(UIConstants.electricCyan),
                foregroundColor: Colors.black,
              ),
              child: const Text('다시 시도'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGoalView(GoalState state) {
    final summary = state.summary!;

    return RefreshIndicator(
      onRefresh: () => ref.read(goalProgressProvider.notifier).refresh(widget.userId),
      color: const Color(UIConstants.electricCyan),
      backgroundColor: const Color(UIConstants.deepBlack),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Goal Header
            _buildGoalHeader(summary),

            const SizedBox(height: UIConstants.spacingXXL),

            // Progress Stats
            ProgressStatsCard(
              completionPercentage: summary.completionPercentage,
              daysActive: summary.daysActive,
              daysRemaining: summary.daysRemaining,
              totalEntries: summary.totalEntries,
              trend: summary.trend,
            ),

            const SizedBox(height: UIConstants.spacingXL),

            // Insights Section
            if (state.insights.isNotEmpty) ...[
              _buildSectionHeader('AI Insights', Icons.lightbulb_outline),
              const SizedBox(height: UIConstants.spacingMD),
              ...state.insights.take(3).map((insight) => Padding(
                    padding: const EdgeInsets.only(bottom: UIConstants.spacingMD),
                    child: InsightCard(insight: insight),
                  )),
              const SizedBox(height: UIConstants.spacingXL),
            ],

            // Upcoming Milestones
            if (summary.milestones.upcoming.isNotEmpty) ...[
              _buildSectionHeader('Upcoming Milestones', Icons.flag_rounded),
              const SizedBox(height: UIConstants.spacingMD),
              ...summary.milestones.upcoming.map((milestone) => Padding(
                    padding: const EdgeInsets.only(bottom: UIConstants.spacingMD),
                    child: MilestoneCard(
                      milestone: milestone,
                      onToggle: null, // View only for now
                    ),
                  )),
              const SizedBox(height: UIConstants.spacingXL),
            ],

            // Recent Activity
            if (summary.recentSnapshot != null) ...[
              _buildSectionHeader('Recent Activity', Icons.history),
              const SizedBox(height: UIConstants.spacingMD),
              _buildRecentSnapshot(summary.recentSnapshot!),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildGoalHeader(GoalSummary summary) {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            Color(UIConstants.electricCyan),
            Color(0xFF0099CC),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(UIConstants.spacingLG),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'One Thing',
            style: TextStyle(
              color: Colors.black54,
              fontSize: UIConstants.fontCaption,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: UIConstants.spacingSM),
          Text(
            summary.goal,
            style: const TextStyle(
              color: Colors.black,
              fontSize: UIConstants.fontHeadline,
              fontWeight: FontWeight.bold,
              height: 1.3,
            ),
          ),
          const SizedBox(height: UIConstants.spacingLG),
          Row(
            children: [
              _buildHeaderStat(
                '${summary.completionPercentage.toStringAsFixed(0)}%',
                'Complete',
              ),
              const SizedBox(width: UIConstants.spacingXL),
              if (summary.daysRemaining != null)
                _buildHeaderStat(
                  '${summary.daysRemaining}',
                  'Days Left',
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderStat(String value, String label) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: const TextStyle(
            color: Colors.black,
            fontSize: UIConstants.fontTitle,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.black54,
            fontSize: UIConstants.fontCaption,
          ),
        ),
      ],
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(
          icon,
          color: const Color(UIConstants.electricCyan),
          size: 24,
        ),
        const SizedBox(width: UIConstants.spacingSM),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: UIConstants.fontTitle,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildRecentSnapshot(ProgressSnapshot snapshot) {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                _formatDate(snapshot.date),
                style: const TextStyle(
                  color: Color(UIConstants.electricCyan),
                  fontSize: UIConstants.fontBody,
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (snapshot.moodRating != null)
                _buildMoodIndicator(snapshot.moodRating!),
            ],
          ),
          if (snapshot.reflection != null) ...[
            const SizedBox(height: UIConstants.spacingMD),
            Text(
              snapshot.reflection!,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.9),
                fontSize: UIConstants.fontBody,
                height: 1.5,
              ),
            ),
          ],
          if (snapshot.metrics.isNotEmpty) ...[
            const SizedBox(height: UIConstants.spacingMD),
            Wrap(
              spacing: UIConstants.spacingSM,
              runSpacing: UIConstants.spacingSM,
              children: snapshot.metrics.map((metric) {
                return Chip(
                  label: Text(
                    '${metric.name}: ${metric.value} ${metric.unit}',
                    style: const TextStyle(fontSize: UIConstants.fontCaption),
                  ),
                  backgroundColor: const Color(UIConstants.midGrey),
                  labelStyle: const TextStyle(color: Colors.white),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMoodIndicator(MoodRating mood) {
    final moodEmoji = {
      MoodRating.veryLow: '😞',
      MoodRating.low: '😕',
      MoodRating.neutral: '😐',
      MoodRating.good: '😊',
      MoodRating.excellent: '😄',
    };

    return Text(
      moodEmoji[mood] ?? '😐',
      style: const TextStyle(fontSize: 24),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return '오늘';
    } else if (difference.inDays == 1) {
      return '어제';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}일 전';
    } else {
      return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    }
  }

  // ==================== Dialogs ====================

  void _showCreateGoalDialog() {
    final targetDateController = TextEditingController();
    DateTime? selectedDate;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          '목표 생성',
          style: TextStyle(color: Colors.white),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              '프로필의 "One Thing"으로부터 목표를 생성합니다.',
              style: TextStyle(color: Colors.white70),
            ),
            const SizedBox(height: UIConstants.spacingLG),
            TextField(
              controller: targetDateController,
              decoration: const InputDecoration(
                labelText: '목표 달성 날짜 (선택사항)',
                labelStyle: TextStyle(color: Colors.white70),
                hintText: 'YYYY-MM-DD',
                hintStyle: TextStyle(color: Colors.white38),
                enabledBorder: UnderlineInputBorder(
                  borderSide: BorderSide(color: Colors.white38),
                ),
                focusedBorder: UnderlineInputBorder(
                  borderSide: BorderSide(color: Color(UIConstants.electricCyan)),
                ),
              ),
              style: const TextStyle(color: Colors.white),
              readOnly: true,
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: DateTime.now().add(const Duration(days: 90)),
                  firstDate: DateTime.now(),
                  lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
                );
                if (date != null) {
                  selectedDate = date;
                  targetDateController.text = '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
                }
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              final success = await ref.read(goalProgressProvider.notifier).createGoal(
                    userId: widget.userId,
                    targetDate: selectedDate?.toIso8601String().split('T')[0],
                  );

              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('목표가 성공적으로 생성되었습니다!'),
                    backgroundColor: Color(UIConstants.electricCyan),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(UIConstants.electricCyan),
              foregroundColor: Colors.black,
            ),
            child: const Text('생성'),
          ),
        ],
      ),
    );
  }

  void _showRecordProgressDialog() {
    if (!ref.read(goalProgressProvider).hasGoal) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('먼저 목표를 생성해주세요')),
      );
      return;
    }

    final reflectionController = TextEditingController();
    int? selectedMood;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          backgroundColor: const Color(UIConstants.deepBlack),
          title: const Text(
            '진행 상황 기록',
            style: TextStyle(color: Colors.white),
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: reflectionController,
                  decoration: const InputDecoration(
                    labelText: '오늘의 성찰',
                    labelStyle: TextStyle(color: Colors.white70),
                    hintText: '오늘 무엇을 했나요?',
                    hintStyle: TextStyle(color: Colors.white38),
                    enabledBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Colors.white38),
                    ),
                    focusedBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Color(UIConstants.electricCyan)),
                    ),
                  ),
                  style: const TextStyle(color: Colors.white),
                  maxLines: 3,
                ),
                const SizedBox(height: UIConstants.spacingLG),
                const Text(
                  '기분',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: UIConstants.fontCaption,
                  ),
                ),
                const SizedBox(height: UIConstants.spacingSM),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: List.generate(5, (index) {
                    final mood = index + 1;
                    final emojis = ['😞', '😕', '😐', '😊', '😄'];
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          selectedMood = mood;
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.all(UIConstants.spacingSM),
                        decoration: BoxDecoration(
                          color: selectedMood == mood
                              ? const Color(UIConstants.electricCyan)
                              : const Color(UIConstants.darkGrey),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          emojis[index],
                          style: const TextStyle(fontSize: 24),
                        ),
                      ),
                    );
                  }),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('취소'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                final success = await ref.read(goalProgressProvider.notifier).recordProgress(
                      userId: widget.userId,
                      reflection: reflectionController.text.isEmpty ? null : reflectionController.text,
                      moodRating: selectedMood,
                    );

                if (success && mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('진행 상황이 기록되었습니다!'),
                      backgroundColor: Color(UIConstants.electricCyan),
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(UIConstants.electricCyan),
                foregroundColor: Colors.black,
              ),
              child: const Text('기록'),
            ),
          ],
        ),
      ),
    );
  }
}
