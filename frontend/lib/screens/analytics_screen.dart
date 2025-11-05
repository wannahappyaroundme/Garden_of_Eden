/// Analytics Dashboard Screen - Visualize progress patterns
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/constants.dart';

class AnalyticsScreen extends ConsumerStatefulWidget {
  final String userId;

  const AnalyticsScreen({
    super.key,
    required this.userId,
  });

  @override
  ConsumerState<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends ConsumerState<AnalyticsScreen> {
  int _selectedPeriod = 30; // days

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'Analytics',
          style: TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          PopupMenuButton<int>(
            icon: const Icon(Icons.calendar_today, color: Colors.white),
            onSelected: (value) {
              setState(() {
                _selectedPeriod = value;
              });
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 7, child: Text('Last 7 days')),
              const PopupMenuItem(value: 30, child: Text('Last 30 days')),
              const PopupMenuItem(value: 90, child: Text('Last 90 days')),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Period selector
            _buildPeriodInfo(),
            const SizedBox(height: UIConstants.spacingXL),

            // Statistics cards
            _buildStatisticsSection(),
            const SizedBox(height: UIConstants.spacingXL),

            // Pattern insights
            _buildPatternsSection(),
            const SizedBox(height: UIConstants.spacingXL),

            // Period comparison
            _buildComparisonSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildPeriodInfo() {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            Color(UIConstants.electricCyan),
            Color(0xFF0099CC),
          ],
        ),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Analysis Period',
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: UIConstants.fontCaption,
                ),
              ),
              const SizedBox(height: UIConstants.spacingSM),
              Text(
                'Last $_selectedPeriod days',
                style: const TextStyle(
                  color: Colors.black,
                  fontSize: UIConstants.fontTitle,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const Icon(
            Icons.analytics_outlined,
            color: Colors.black,
            size: 40,
          ),
        ],
      ),
    );
  }

  Widget _buildStatisticsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('Statistics', Icons.bar_chart),
        const SizedBox(height: UIConstants.spacingMD),

        // Placeholder for statistics - In production, fetch from API
        _buildStatCard(
          title: 'Average Mood',
          value: '4.2',
          subtitle: 'out of 5.0',
          icon: Icons.mood,
          color: Colors.green,
        ),
        const SizedBox(height: UIConstants.spacingMD),
        _buildStatCard(
          title: 'Consistency Score',
          value: '85%',
          subtitle: 'Very consistent',
          icon: Icons.trending_up,
          color: const Color(UIConstants.electricCyan),
        ),
        const SizedBox(height: UIConstants.spacingMD),
        _buildStatCard(
          title: 'Most Productive Day',
          value: 'Monday',
          subtitle: '5 entries',
          icon: Icons.star,
          color: Colors.orange,
        ),
      ],
    );
  }

  Widget _buildPatternsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('Patterns', Icons.pattern),
        const SizedBox(height: UIConstants.spacingMD),

        // Placeholder patterns
        _buildPatternCard(
          'Monday이(가) 가장 생산적입니다',
          Icons.calendar_today,
        ),
        const SizedBox(height: UIConstants.spacingSM),
        _buildPatternCard(
          '기분이 점차 개선되고 있습니다',
          Icons.trending_up,
        ),
        const SizedBox(height: UIConstants.spacingSM),
        _buildPatternCard(
          '7일 연속 기록 중입니다!',
          Icons.local_fire_department,
        ),
      ],
    );
  }

  Widget _buildComparisonSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('Period Comparison', Icons.compare_arrows),
        const SizedBox(height: UIConstants.spacingMD),

        Container(
          padding: const EdgeInsets.all(UIConstants.spacingLG),
          decoration: BoxDecoration(
            color: const Color(UIConstants.darkGrey),
            borderRadius: BorderRadius.circular(UIConstants.spacingMD),
          ),
          child: Column(
            children: [
              _buildComparisonRow('Mood', '+5.2%', true),
              const Divider(color: Color(UIConstants.midGrey)),
              _buildComparisonRow('Entries', '+20.0%', true),
              const Divider(color: Color(UIConstants.midGrey)),
              _buildComparisonRow('Overall', 'Improving', true),
            ],
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

  Widget _buildStatCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
        border: Border.all(
          color: color.withValues(alpha: 0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(UIConstants.spacingMD),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(UIConstants.spacingSM),
            ),
            child: Icon(
              icon,
              color: color,
              size: 28,
            ),
          ),
          const SizedBox(width: UIConstants.spacingMD),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: UIConstants.fontCaption,
                  ),
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
                  subtitle,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.5),
                    fontSize: UIConstants.fontCaption,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPatternCard(String text, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingMD),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingSM),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: const Color(UIConstants.electricCyan),
            size: 20,
          ),
          const SizedBox(width: UIConstants.spacingMD),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                color: Colors.white,
                fontSize: UIConstants.fontBody,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonRow(String label, String value, bool isPositive) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: UIConstants.spacingSM),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: UIConstants.fontBody,
            ),
          ),
          Row(
            children: [
              Text(
                value,
                style: TextStyle(
                  color: isPositive ? Colors.green : Colors.red,
                  fontSize: UIConstants.fontBody,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: UIConstants.spacingSM),
              Icon(
                isPositive ? Icons.arrow_upward : Icons.arrow_downward,
                color: isPositive ? Colors.green : Colors.red,
                size: 16,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
