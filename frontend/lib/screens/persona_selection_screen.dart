/// Persona Selection Screen - Choose Adam or Eve
library;

import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../screens/onboarding_screen.dart';

class PersonaSelectionScreen extends StatelessWidget {
  const PersonaSelectionScreen({super.key});

  void _selectPersona(BuildContext context, PersonaType persona) {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => OnboardingScreen(persona: persona),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Title
              const Text(
                'Garden of Eden',
                style: TextStyle(
                  color: Color(UIConstants.electricCyan),
                  fontSize: UIConstants.fontDisplay,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              const Text(
                'Choose Your Mentor',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: UIConstants.fontHeadline,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                '당신의 성장을 도와줄 멘토를 선택하세요',
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.7),
                  fontSize: UIConstants.fontBody,
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 64),

              // Adam Card
              _buildPersonaCard(
                context: context,
                persona: PersonaType.adam,
                icon: Icons.psychology,
                title: 'Adam',
                subtitle: 'Socratic Questioner',
                description:
                    'Guides through thoughtful questions\nHelps discover answers within yourself',
                color: const Color(0xFF4A90E2),
              ),

              const SizedBox(height: 24),

              // Eve Card
              _buildPersonaCard(
                context: context,
                persona: PersonaType.eve,
                icon: Icons.favorite,
                title: 'Eve',
                subtitle: 'Encouraging Catalyst',
                description:
                    'Nurtures growth with warmth\nCelebrates progress and potential',
                color: const Color(0xFFE24A8D),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPersonaCard({
    required BuildContext context,
    required PersonaType persona,
    required IconData icon,
    required String title,
    required String subtitle,
    required String description,
    required Color color,
  }) {
    return GestureDetector(
      onTap: () => _selectPersona(context, persona),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: color.withValues(alpha: 0.5),
            width: 2,
          ),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: color,
              size: 64,
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: TextStyle(
                color: color,
                fontSize: UIConstants.fontHeadline,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.9),
                fontSize: UIConstants.fontBody,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              description,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: UIConstants.fontCaption,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
