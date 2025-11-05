/// Voice Settings Screen - Customize voice and persona
library;

import 'package:flutter/material.dart';
import '../utils/constants.dart';

class VoiceSettingsScreen extends StatefulWidget {
  final String userId;

  const VoiceSettingsScreen({
    super.key,
    required this.userId,
  });

  @override
  State<VoiceSettingsScreen> createState() => _VoiceSettingsScreenState();
}

class _VoiceSettingsScreenState extends State<VoiceSettingsScreen> {
  String _selectedVoice = 'default';
  double _speed = 1.0;
  double _pitch = 1.0;
  double _volume = 1.0;

  // Persona traits
  int _empathy = 3;
  int _directness = 3;
  int _formality = 2;
  int _encouragement = 4;

  final Map<String, String> _availableVoices = {
    'default': 'Default',
    'female_gentle': 'Gentle Female',
    'male_confident': 'Confident Male',
    'neutral_calm': 'Calm Neutral',
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'Voice Settings',
          style: TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          TextButton(
            onPressed: _saveSettings,
            child: const Text(
              'Save',
              style: TextStyle(
                color: Color(UIConstants.electricCyan),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Voice Selection
            _buildSectionHeader('Voice Type', Icons.record_voice_over),
            const SizedBox(height: UIConstants.spacingMD),
            _buildVoiceSelector(),
            const SizedBox(height: UIConstants.spacingXL),

            // Voice Parameters
            _buildSectionHeader('Voice Parameters', Icons.tune),
            const SizedBox(height: UIConstants.spacingMD),
            _buildVoiceParameters(),
            const SizedBox(height: UIConstants.spacingXL),

            // Persona Traits
            _buildSectionHeader('Persona Traits', Icons.psychology),
            const SizedBox(height: UIConstants.spacingMD),
            _buildPersonaTraits(),
            const SizedBox(height: UIConstants.spacingXL),

            // Test Voice Button
            Center(
              child: ElevatedButton.icon(
                onPressed: _testVoice,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Test Voice'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(UIConstants.electricCyan),
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(
                    horizontal: UIConstants.spacingXL,
                    vertical: UIConstants.spacingMD,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
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

  Widget _buildVoiceSelector() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        children: _availableVoices.entries.map((entry) {
          return RadioListTile<String>(
            value: entry.key,
            groupValue: _selectedVoice,
            onChanged: (value) {
              setState(() {
                _selectedVoice = value!;
              });
            },
            title: Text(
              entry.value,
              style: const TextStyle(color: Colors.white),
            ),
            activeColor: const Color(UIConstants.electricCyan),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildVoiceParameters() {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        children: [
          _buildSlider(
            'Speed',
            _speed,
            0.5,
            2.0,
            (value) => setState(() => _speed = value),
          ),
          const SizedBox(height: UIConstants.spacingMD),
          _buildSlider(
            'Pitch',
            _pitch,
            0.5,
            2.0,
            (value) => setState(() => _pitch = value),
          ),
          const SizedBox(height: UIConstants.spacingMD),
          _buildSlider(
            'Volume',
            _volume,
            0.5,
            2.0,
            (value) => setState(() => _volume = value),
          ),
        ],
      ),
    );
  }

  Widget _buildPersonaTraits() {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        children: [
          _buildTraitSlider(
            'Empathy',
            _empathy,
            Icons.favorite,
            (value) => setState(() => _empathy = value),
          ),
          const SizedBox(height: UIConstants.spacingMD),
          _buildTraitSlider(
            'Directness',
            _directness,
            Icons.arrow_forward,
            (value) => setState(() => _directness = value),
          ),
          const SizedBox(height: UIConstants.spacingMD),
          _buildTraitSlider(
            'Formality',
            _formality,
            Icons.work_outline,
            (value) => setState(() => _formality = value),
          ),
          const SizedBox(height: UIConstants.spacingMD),
          _buildTraitSlider(
            'Encouragement',
            _encouragement,
            Icons.emoji_events,
            (value) => setState(() => _encouragement = value),
          ),
        ],
      ),
    );
  }

  Widget _buildSlider(
    String label,
    double value,
    double min,
    double max,
    ValueChanged<double> onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: UIConstants.fontBody,
              ),
            ),
            Text(
              value.toStringAsFixed(1),
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: UIConstants.fontBody,
              ),
            ),
          ],
        ),
        Slider(
          value: value,
          min: min,
          max: max,
          divisions: 30,
          activeColor: const Color(UIConstants.electricCyan),
          inactiveColor: const Color(UIConstants.midGrey),
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _buildTraitSlider(
    String label,
    int value,
    IconData icon,
    ValueChanged<int> onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: const Color(UIConstants.electricCyan), size: 20),
            const SizedBox(width: UIConstants.spacingSM),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: UIConstants.fontBody,
              ),
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: UIConstants.spacingMD,
                vertical: UIConstants.spacingSM,
              ),
              decoration: BoxDecoration(
                color: const Color(UIConstants.midGrey),
                borderRadius: BorderRadius.circular(UIConstants.spacingSM),
              ),
              child: Text(
                '$value / 5',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        Slider(
          value: value.toDouble(),
          min: 1,
          max: 5,
          divisions: 4,
          activeColor: const Color(UIConstants.electricCyan),
          inactiveColor: const Color(UIConstants.midGrey),
          onChanged: (val) => onChanged(val.round()),
        ),
      ],
    );
  }

  void _testVoice() {
    // TODO: Implement voice testing
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Voice test will play with current settings'),
        backgroundColor: Color(UIConstants.electricCyan),
      ),
    );
  }

  void _saveSettings() {
    // TODO: Implement save to backend
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Settings saved successfully!'),
        backgroundColor: Color(UIConstants.electricCyan),
      ),
    );
    Navigator.pop(context);
  }
}
