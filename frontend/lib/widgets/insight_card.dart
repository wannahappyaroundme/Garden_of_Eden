/// AI Insight Card Widget
library;

import 'package:flutter/material.dart';
import '../models/goal_models.dart';
import '../utils/constants.dart';

class InsightCard extends StatelessWidget {
  final GoalInsight insight;

  const InsightCard({
    super.key,
    required this.insight,
  });

  @override
  Widget build(BuildContext context) {
    final (icon, color) = _getInsightIconAndColor();

    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingMD),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
        border: Border.all(
          color: color.withValues(alpha: 0.3),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with icon and priority
          Row(
            children: [
              Icon(
                icon,
                color: color,
                size: 20,
              ),
              const SizedBox(width: UIConstants.spacingSM),
              Expanded(
                child: Text(
                  insight.title,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.9),
                    fontSize: UIConstants.fontBody,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (insight.isHighPriority)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: UIConstants.spacingSM,
                    vertical: UIConstants.spacingMicro,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'HIGH',
                    style: TextStyle(
                      color: Colors.red,
                      fontSize: UIConstants.fontLabel,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: UIConstants.spacingSM),

          // Description
          Text(
            insight.description,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.7),
              fontSize: UIConstants.fontBody,
              height: 1.5,
            ),
          ),

          // Actionable indicator
          if (insight.actionable) ...[
            const SizedBox(height: UIConstants.spacingSM),
            Row(
              children: [
                Icon(
                  Icons.lightbulb,
                  size: 14,
                  color: color,
                ),
                const SizedBox(width: UIConstants.spacingXS),
                Text(
                  'Actionable',
                  style: TextStyle(
                    color: color,
                    fontSize: UIConstants.fontCaption,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  (IconData, Color) _getInsightIconAndColor() {
    switch (insight.insightType) {
      case InsightType.achievement:
        return (Icons.emoji_events, const Color(0xFFFFD700)); // Gold
      case InsightType.encouragement:
        return (Icons.favorite, const Color(UIConstants.electricCyan));
      case InsightType.concern:
        return (Icons.warning_amber_rounded, const Color(UIConstants.statePitfall));
      case InsightType.suggestion:
        return (Icons.tips_and_updates, const Color(0xFF9C27B0)); // Purple
    }
  }
}
