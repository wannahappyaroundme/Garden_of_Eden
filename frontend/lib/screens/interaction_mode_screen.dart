/// Interaction Mode Settings Screen
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/constants.dart';
import '../providers/service_providers.dart';

class InteractionModeScreen extends ConsumerStatefulWidget {
  final String userId;

  const InteractionModeScreen({
    super.key,
    required this.userId,
  });

  @override
  ConsumerState<InteractionModeScreen> createState() =>
      _InteractionModeScreenState();
}

class _InteractionModeScreenState extends ConsumerState<InteractionModeScreen> {
  String _currentMode = 'ai_led'; // Default
  bool _isLoading = true;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _loadCurrentMode();
  }

  Future<void> _loadCurrentMode() async {
    setState(() => _isLoading = true);

    try {
      final apiService = ref.read(apiServiceProvider);
      final mode = await apiService.getInteractionMode(widget.userId);

      setState(() {
        _currentMode = mode;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        _showError('모드 로드 실패: ${e.toString()}');
      }
    }
  }

  Future<void> _saveMode(String newMode) async {
    if (_isSaving || newMode == _currentMode) return;

    setState(() => _isSaving = true);

    try {
      final apiService = ref.read(apiServiceProvider);
      await apiService.updateInteractionMode(widget.userId, newMode);

      setState(() {
        _currentMode = newMode;
        _isSaving = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('모드가 저장되었습니다'),
            backgroundColor: Color(UIConstants.electricCyan),
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      setState(() => _isSaving = false);
      if (mounted) {
        _showError('모드 저장 실패: ${e.toString()}');
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[700],
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          '대화 모드',
          style: TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                color: Color(UIConstants.electricCyan),
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(UIConstants.spacingLG),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header description
                  Text(
                    '대화 스타일을 선택하세요',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.8),
                      fontSize: UIConstants.fontBody,
                    ),
                  ),
                  const SizedBox(height: UIConstants.spacingSM),
                  Text(
                    'AI와의 대화 방식을 선택할 수 있습니다. 언제든지 변경할 수 있습니다.',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.6),
                      fontSize: UIConstants.fontCaption,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: UIConstants.spacingXL),

                  // AI-Led Mode Card
                  _buildModeCard(
                    mode: 'ai_led',
                    title: 'AI 주도 모드',
                    subtitle: 'AI가 질문하고, 내가 답변',
                    description:
                        'AI 멘토가 적극적으로 질문을 던지며 당신의 생각을 이끌어냅니다. '
                        '깊은 자기 성찰과 통찰을 위한 소크라테스식 대화를 선호한다면 이 모드를 추천합니다.',
                    icon: Icons.psychology,
                    iconColor: const Color(UIConstants.electricCyan),
                    isSelected: _currentMode == 'ai_led',
                    examples: [
                      '예시: "오늘 힘들었어요" → AI: "무엇이 가장 힘들었나요? 그 순간에 어떤 생각이 들었나요?"',
                    ],
                  ),
                  const SizedBox(height: UIConstants.spacingLG),

                  // User-Led Mode Card
                  _buildModeCard(
                    mode: 'user_led',
                    title: '사용자 주도 모드',
                    subtitle: '내가 질문하고, AI가 답변',
                    description:
                        '당신이 궁금한 것을 물어보면 AI 멘토가 조언과 통찰을 제공합니다. '
                        '필요할 때 자유롭게 질문하고 답을 얻고 싶다면 이 모드를 추천합니다.',
                    icon: Icons.question_answer,
                    iconColor: Colors.purple,
                    isSelected: _currentMode == 'user_led',
                    examples: [
                      '예시: "이 상황에서 어떻게 해야 할까요?" → AI: [조언 제공] "더 이야기하고 싶은 부분이 있나요?"',
                    ],
                  ),

                  const SizedBox(height: UIConstants.spacingXL),

                  // Save indicator
                  if (_isSaving)
                    const Center(
                      child: CircularProgressIndicator(
                        color: Color(UIConstants.electricCyan),
                      ),
                    ),
                ],
              ),
            ),
    );
  }

  Widget _buildModeCard({
    required String mode,
    required String title,
    required String subtitle,
    required String description,
    required IconData icon,
    required Color iconColor,
    required bool isSelected,
    required List<String> examples,
  }) {
    return InkWell(
      onTap: _isSaving ? null : () => _saveMode(mode),
      borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      child: Container(
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        decoration: BoxDecoration(
          color: const Color(UIConstants.darkGrey),
          borderRadius: BorderRadius.circular(UIConstants.spacingMD),
          border: Border.all(
            color: isSelected
                ? iconColor
                : Colors.white.withValues(alpha: 0.2),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Icon
                Container(
                  padding: const EdgeInsets.all(UIConstants.spacingMD),
                  decoration: BoxDecoration(
                    color: iconColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(UIConstants.spacingSM),
                  ),
                  child: Icon(
                    icon,
                    color: iconColor,
                    size: 28,
                  ),
                ),
                const SizedBox(width: UIConstants.spacingMD),

                // Title and subtitle
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: UIConstants.fontBody,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: UIConstants.spacingXS),
                      Text(
                        subtitle,
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.7),
                          fontSize: UIConstants.fontCaption,
                        ),
                      ),
                    ],
                  ),
                ),

                // Selection indicator
                if (isSelected)
                  Icon(
                    Icons.check_circle,
                    color: iconColor,
                    size: 28,
                  )
                else
                  Icon(
                    Icons.circle_outlined,
                    color: Colors.white.withValues(alpha: 0.3),
                    size: 28,
                  ),
              ],
            ),

            const SizedBox(height: UIConstants.spacingMD),

            // Description
            Text(
              description,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
                fontSize: UIConstants.fontCaption,
                height: 1.5,
              ),
            ),

            const SizedBox(height: UIConstants.spacingMD),

            // Examples
            ...examples.map((example) => Padding(
                  padding: const EdgeInsets.only(
                    top: UIConstants.spacingXS,
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.lightbulb_outline,
                        color: iconColor.withValues(alpha: 0.6),
                        size: 16,
                      ),
                      const SizedBox(width: UIConstants.spacingXS),
                      Expanded(
                        child: Text(
                          example,
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.6),
                            fontSize: UIConstants.fontCaption,
                            height: 1.4,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }
}
