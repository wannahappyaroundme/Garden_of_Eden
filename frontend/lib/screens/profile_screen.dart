/// Profile Screen - Shows user's learned profile
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/chat_models.dart';
import '../providers/profile_provider.dart';
import '../providers/session_provider.dart';
import '../utils/constants.dart';
import '../widgets/trait_card.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  final String userId;

  const ProfileScreen({
    super.key,
    required this.userId,
  });

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    // Load profile on init
    Future.microtask(() {
      ref.read(profileProvider.notifier).loadProfile(widget.userId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final profileState = ref.watch(profileProvider);

    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'My Profile',
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
              ref.read(profileProvider.notifier).loadProfile(widget.userId);
            },
          ),
        ],
      ),
      body: profileState.when(
        data: (profile) {
          if (profile == null) {
            return _buildNewUserMessage();
          }
          return _buildProfile(profile);
        },
        loading: () => const Center(
          child: CircularProgressIndicator(
            color: Color(UIConstants.electricCyan),
          ),
        ),
        error: (error, stack) => Center(
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
                const Text(
                  '프로필을 불러오지 못했습니다',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: UIConstants.fontTitle,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: UIConstants.spacingSM),
                Text(
                  _formatError(error),
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: UIConstants.fontBody,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: UIConstants.spacingXL),
                ElevatedButton(
                  onPressed: () {
                    ref.read(profileProvider.notifier).loadProfile(widget.userId);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(UIConstants.electricCyan),
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(
                      horizontal: UIConstants.spacingXL,
                      vertical: UIConstants.spacingMD,
                    ),
                  ),
                  child: const Text('다시 시도'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNewUserMessage() {
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
                Icons.person_outline,
                size: 60,
                color: Color(UIConstants.electricCyan),
              ),
            ),
            const SizedBox(height: UIConstants.spacingXXL),
            const Text(
              '아직 프로필이 생성되지 않았습니다',
              style: TextStyle(
                color: Colors.white,
                fontSize: UIConstants.fontHeadline,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: UIConstants.spacingMD),
            Text(
              'AI와 대화를 시작하면\n자동으로 프로필이 학습됩니다',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: UIConstants.fontBody,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: UIConstants.spacingXXL),
            ElevatedButton.icon(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.arrow_back),
              label: const Text('대화 화면으로 돌아가기'),
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

  Widget _buildProfile(UserProfile profile) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Profile header
          _buildProfileHeader(profile),

          const SizedBox(height: UIConstants.spacingXXL),

          // One Thing section
          _buildSection(
            title: 'One Thing',
            icon: Icons.flag_rounded,
            child: _buildInfoCard(
              profile.oneThing ?? '아직 설정되지 않았습니다',
              Colors.white,
            ),
          ),

          const SizedBox(height: UIConstants.spacingXL),

          // Core Pitfall section
          _buildSection(
            title: 'Core Pitfall',
            icon: Icons.warning_amber_rounded,
            child: _buildInfoCard(
              profile.corePitfall ?? '아직 발견되지 않았습니다',
              const Color(UIConstants.statePitfall),
            ),
          ),

          const SizedBox(height: UIConstants.spacingXXL),

          // Personality Traits
          _buildSection(
            title: 'Personality Traits',
            icon: Icons.psychology_rounded,
            child: Column(
              children: profile.topTraits.isEmpty
                  ? [
                      const Text(
                        '아직 학습된 특성이 없습니다.\n더 많은 대화를 나눠보세요!',
                        style: TextStyle(
                          color: Colors.white54,
                          fontSize: UIConstants.fontBody,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ]
                  : profile.topTraits
                      .map((trait) => Padding(
                            padding: const EdgeInsets.only(
                              bottom: UIConstants.spacingMD,
                            ),
                            child: TraitCard(
                              traitName: trait.name,
                              weight: trait.weight,
                            ),
                          ))
                      .toList(),
            ),
          ),

          const SizedBox(height: UIConstants.spacingXXL),

          // Session Info section
          _buildSessionSection(),

          const SizedBox(height: UIConstants.spacingXL),

          // Stats section
          _buildStatsSection(profile),
        ],
      ),
    );
  }

  Widget _buildSessionSection() {
    final sessionState = ref.watch(sessionProvider);

    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingLG),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.timer,
                color: Color(UIConstants.electricCyan),
                size: 24,
              ),
              const SizedBox(width: UIConstants.spacingSM),
              const Text(
                'Session Status',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: UIConstants.fontTitle,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: UIConstants.spacingMD),

          if (sessionState.currentSession != null) ...[
            _buildStatRow('Session ID', '${sessionState.currentSession!.sessionId.substring(0, 8)}...'),
            _buildStatRow('Persona', sessionState.currentSession!.persona),
            _buildStatRow('Turn Count', '${sessionState.turnCount}'),
            _buildStatRow('Status', sessionState.currentSession!.isExpired ? 'Expired' : 'Active'),
            if (sessionState.lastActivity != null)
              _buildStatRow('Last Activity', _formatDateTime(sessionState.lastActivity!)),

            const SizedBox(height: UIConstants.spacingMD),

            ElevatedButton(
              onPressed: () {
                ref.read(sessionProvider.notifier).closeSession(
                      reason: 'User closed from profile',
                    );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red[700],
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 48),
              ),
              child: const Text('End Session'),
            ),
          ] else ...[
            Text(
              'No active session',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: UIConstants.fontBody,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildProfileHeader(UserProfile profile) {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingLG),
      ),
      child: Row(
        children: [
          // Profile icon
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: const Color(UIConstants.electricCyan),
              borderRadius: BorderRadius.circular(40),
            ),
            child: const Icon(
              Icons.person,
              size: 40,
              color: Colors.black,
            ),
          ),
          const SizedBox(width: UIConstants.spacingLG),

          // Profile info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  profile.userId,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: UIConstants.fontHeadline,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: UIConstants.spacingMicro),
                Text(
                  'Version ${profile.profileVersion} • ${profile.profileMaturity}',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: UIConstants.fontBody,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required IconData icon,
    required Widget child,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
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
        ),
        const SizedBox(height: UIConstants.spacingMD),
        child,
      ],
    );
  }

  Widget _buildInfoCard(String text, Color accentColor) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
        border: Border.all(
          color: accentColor.withValues(alpha: 0.3),
          width: 2,
        ),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: Colors.white.withValues(alpha: 0.9),
          fontSize: UIConstants.fontBody,
          height: 1.5,
        ),
      ),
    );
  }

  Widget _buildStatsSection(UserProfile profile) {
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
            'Statistics',
            style: TextStyle(
              color: Colors.white,
              fontSize: UIConstants.fontTitle,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: UIConstants.spacingMD),

          _buildStatRow('Total Conversations', '${profile.totalConversations}'),
          _buildStatRow('Profile Version', '${profile.profileVersion}'),
          _buildStatRow('Maturity', profile.profileMaturity),
          if (profile.recentEmotionalState != null)
            _buildStatRow('Recent Emotional State', profile.recentEmotionalState!),
          _buildStatRow(
            'Last Updated',
            _formatDateTime(profile.lastUpdated),
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: UIConstants.spacingSM),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.7),
              fontSize: UIConstants.fontBody,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: UIConstants.fontBody,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return '방금 전';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}분 전';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}시간 전';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}일 전';
    } else {
      return '${dateTime.year}-${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')}';
    }
  }

  String _formatError(Object error) {
    final errorStr = error.toString().toLowerCase();

    if (errorStr.contains('socket') || errorStr.contains('network') || errorStr.contains('connection')) {
      return '네트워크 연결을 확인해주세요';
    } else if (errorStr.contains('timeout')) {
      return '서버 응답 시간이 초과되었습니다';
    } else if (errorStr.contains('404') || errorStr.contains('not found')) {
      return '프로필 데이터를 찾을 수 없습니다';
    } else if (errorStr.contains('500') || errorStr.contains('server')) {
      return '서버 오류가 발생했습니다';
    } else {
      return '오류: ${error.toString()}';
    }
  }
}
