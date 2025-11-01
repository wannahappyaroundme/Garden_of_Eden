/// Trait Card Widget - Shows personality trait with weight
library;

import 'package:flutter/material.dart';
import '../utils/constants.dart';

class TraitCard extends StatelessWidget {
  final String traitName;
  final double weight;

  const TraitCard({
    super.key,
    required this.traitName,
    required this.weight,
  });

  @override
  Widget build(BuildContext context) {
    // Format trait name (replace underscore with space, capitalize)
    final displayName = traitName
        .replaceAll('_', ' ')
        .split(' ')
        .map((word) => word.isEmpty
            ? ''
            : word[0].toUpperCase() + word.substring(1).toLowerCase())
        .join(' ');

    // Calculate percentage
    final percentage = (weight * 100).toInt();

    // Choose color based on weight
    Color barColor;
    if (weight >= 0.8) {
      barColor = const Color(UIConstants.stateResponding); // Green
    } else if (weight >= 0.6) {
      barColor = const Color(UIConstants.electricCyan); // Cyan
    } else if (weight >= 0.4) {
      barColor = const Color(UIConstants.stateProcessing); // Blue
    } else {
      barColor = const Color(UIConstants.lightGrey); // Grey
    }

    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingMD),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Trait name and weight
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  displayName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: UIConstants.fontBody,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Text(
                '$percentage%',
                style: TextStyle(
                  color: barColor,
                  fontSize: UIConstants.fontBody,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          const SizedBox(height: UIConstants.spacingSM),

          // Progress bar
          ClipRRect(
            borderRadius: BorderRadius.circular(UIConstants.spacingMicro),
            child: LinearProgressIndicator(
              value: weight,
              minHeight: 8,
              backgroundColor: Colors.white.withValues(alpha: 0.1),
              valueColor: AlwaysStoppedAnimation<Color>(barColor),
            ),
          ),
        ],
      ),
    );
  }
}
