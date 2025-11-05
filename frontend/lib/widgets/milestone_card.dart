/// Milestone Card Widget
library;

import 'package:flutter/material.dart';
import '../models/goal_models.dart';
import '../utils/constants.dart';

class MilestoneCard extends StatelessWidget {
  final UpcomingMilestone milestone;
  final VoidCallback? onToggle;

  const MilestoneCard({
    super.key,
    required this.milestone,
    this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    final daysUntil = milestone.daysUntil;
    final isOverdue = daysUntil != null && daysUntil < 0;
    final isUrgent = daysUntil != null && daysUntil > 0 && daysUntil <= 7;

    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingMD),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
        border: Border.all(
          color: isOverdue
              ? Colors.red.withValues(alpha: 0.5)
              : isUrgent
                  ? const Color(UIConstants.electricCyan).withValues(alpha: 0.5)
                  : Colors.transparent,
          width: 2,
        ),
      ),
      child: Row(
        children: [
          // Checkbox (if toggleable)
          if (onToggle != null)
            GestureDetector(
              onTap: onToggle,
              child: Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: const Color(UIConstants.electricCyan),
                    width: 2,
                  ),
                ),
              ),
            ),
          if (onToggle != null) const SizedBox(width: UIConstants.spacingMD),

          // Milestone content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  milestone.description,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.9),
                    fontSize: UIConstants.fontBody,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (milestone.targetDate != null) ...[
                  const SizedBox(height: UIConstants.spacingXS),
                  Text(
                    _formatTargetDate(milestone.targetDate!, daysUntil),
                    style: TextStyle(
                      color: isOverdue
                          ? Colors.red
                          : isUrgent
                              ? const Color(UIConstants.electricCyan)
                              : Colors.white.withValues(alpha: 0.6),
                      fontSize: UIConstants.fontCaption,
                    ),
                  ),
                ],
              ],
            ),
          ),

          // Days indicator
          if (daysUntil != null)
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: UIConstants.spacingSM,
                vertical: UIConstants.spacingXS,
              ),
              decoration: BoxDecoration(
                color: isOverdue
                    ? Colors.red.withValues(alpha: 0.2)
                    : isUrgent
                        ? const Color(UIConstants.electricCyan).withValues(alpha: 0.2)
                        : const Color(UIConstants.midGrey),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                isOverdue
                    ? '${-daysUntil}일 지남'
                    : '$daysUntil일',
                style: TextStyle(
                  color: isOverdue
                      ? Colors.red
                      : isUrgent
                          ? const Color(UIConstants.electricCyan)
                          : Colors.white.withValues(alpha: 0.8),
                  fontSize: UIConstants.fontCaption,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
        ],
      ),
    );
  }

  String _formatTargetDate(String targetDate, int? daysUntil) {
    try {
      final date = DateTime.parse(targetDate);
      return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    } catch (_) {
      return targetDate;
    }
  }
}
