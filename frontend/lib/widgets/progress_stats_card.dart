/// Progress Statistics Card Widget
library;

import 'package:flutter/material.dart';
import '../models/goal_models.dart';
import '../utils/constants.dart';

class ProgressStatsCard extends StatelessWidget {
  final double completionPercentage;
  final int daysActive;
  final int? daysRemaining;
  final int totalEntries;
  final ProgressTrend? trend;

  const ProgressStatsCard({
    super.key,
    required this.completionPercentage,
    required this.daysActive,
    this.daysRemaining,
    required this.totalEntries,
    this.trend,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingLG),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Progress Overview',
            style: TextStyle(
              color: Colors.white,
              fontSize: UIConstants.fontTitle,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: UIConstants.spacingLG),

          // Progress bar
          _buildProgressBar(),

          const SizedBox(height: UIConstants.spacingLG),

          // Stats grid
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  icon: Icons.calendar_today,
                  label: 'Days Active',
                  value: '$daysActive',
                ),
              ),
              Expanded(
                child: _buildStatItem(
                  icon: Icons.edit_note,
                  label: 'Entries',
                  value: '$totalEntries',
                ),
              ),
            ],
          ),

          if (trend != null) ...[
            const SizedBox(height: UIConstants.spacingLG),
            _buildTrendSection(trend!),
          ],
        ],
      ),
    );
  }

  Widget _buildProgressBar() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${completionPercentage.toStringAsFixed(1)}% Complete',
              style: const TextStyle(
                color: Color(UIConstants.electricCyan),
                fontSize: UIConstants.fontBody,
                fontWeight: FontWeight.w600,
              ),
            ),
            if (daysRemaining != null)
              Text(
                '$daysRemaining days left',
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.6),
                  fontSize: UIConstants.fontCaption,
                ),
              ),
          ],
        ),
        const SizedBox(height: UIConstants.spacingSM),
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: LinearProgressIndicator(
            value: completionPercentage / 100,
            minHeight: 12,
            backgroundColor: const Color(UIConstants.midGrey),
            valueColor: const AlwaysStoppedAnimation<Color>(
              Color(UIConstants.electricCyan),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: const Color(UIConstants.electricCyan),
          size: 32,
        ),
        const SizedBox(height: UIConstants.spacingXS),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: UIConstants.fontHeadline,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.6),
            fontSize: UIConstants.fontCaption,
          ),
        ),
      ],
    );
  }

  Widget _buildTrendSection(ProgressTrend trend) {
    final (trendIcon, trendColor, trendText) = _getTrendInfo(trend.direction);

    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingMD),
      decoration: BoxDecoration(
        color: const Color(UIConstants.midGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        children: [
          // Trend direction
          Row(
            children: [
              Icon(
                trendIcon,
                color: trendColor,
                size: 20,
              ),
              const SizedBox(width: UIConstants.spacingSM),
              Text(
                trendText,
                style: TextStyle(
                  color: trendColor,
                  fontSize: UIConstants.fontBody,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),

          const SizedBox(height: UIConstants.spacingMD),

          // Streaks
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildTrendStat(
                icon: Icons.local_fire_department,
                label: 'Current Streak',
                value: '${trend.currentStreak}',
                color: trend.currentStreak > 0
                    ? const Color(0xFFFF6B35)
                    : Colors.white54,
              ),
              _buildTrendStat(
                icon: Icons.military_tech,
                label: 'Best Streak',
                value: '${trend.bestStreak}',
                color: const Color(0xFFFFD700),
              ),
              _buildTrendStat(
                icon: Icons.speed,
                label: 'Consistency',
                value: '${(trend.consistencyScore * 100).toInt()}%',
                color: const Color(UIConstants.electricCyan),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTrendStat({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: color,
          size: 24,
        ),
        const SizedBox(height: UIConstants.spacingXS),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: UIConstants.fontBody,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.6),
            fontSize: UIConstants.fontLabel,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  (IconData, Color, String) _getTrendInfo(String direction) {
    switch (direction) {
      case 'improving':
        return (
          Icons.trending_up,
          const Color(0xFF4CAF50),
          'Improving Trend',
        );
      case 'declining':
        return (
          Icons.trending_down,
          const Color(0xFFF44336),
          'Needs Attention',
        );
      case 'stable':
      default:
        return (
          Icons.trending_flat,
          const Color(UIConstants.electricCyan),
          'Stable Progress',
        );
    }
  }
}
