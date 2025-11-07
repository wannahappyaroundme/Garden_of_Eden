/// Voice Settings Screen - Customize voice and persona
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/constants.dart';
import '../providers/service_providers.dart';

class VoiceSettingsScreen extends ConsumerStatefulWidget {
  final String userId;

  const VoiceSettingsScreen({
    super.key,
    required this.userId,
  });

  @override
  ConsumerState<VoiceSettingsScreen> createState() => _VoiceSettingsScreenState();
}

class _VoiceSettingsScreenState extends ConsumerState<VoiceSettingsScreen> {
  bool _isLoading = true;
  bool _isSaving = false;

  String _selectedVoice = 'Neural2-C';  // Default to Adam's voice
  PersonaType _voiceGender = PersonaType.adam;  // Adam (male) or Eve (female)
  double _speed = 1.0;
  double _pitch = 1.0;
  double _volume = 1.0;

  // Persona traits
  int _empathy = 3;
  int _directness = 3;
  int _formality = 2;
  int _encouragement = 4;

  // Google Cloud TTS Neural2 Korean voices
  final Map<String, String> _adamVoices = {
    'Neural2-C': 'Adam (Deep, Stable)',
  };

  final Map<String, String> _eveVoices = {
    'Neural2-A': 'Eve - Bright & Friendly',
    'Neural2-B': 'Eve - Soft & Calm',
  };

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() => _isLoading = true);

    try {
      final apiService = ref.read(apiServiceProvider);
      final settings = await apiService.getVoiceSettings(widget.userId);

      setState(() {
        _selectedVoice = settings['voice_type'] ?? 'default';
        _speed = (settings['speed'] ?? 1.0).toDouble();
        _pitch = (settings['pitch'] ?? 1.0).toDouble();
        _volume = (settings['volume'] ?? 1.0).toDouble();

        // Parse voice gender from persona field
        final persona = settings['persona'] ?? 'adam';
        _voiceGender = persona == 'eve' ? PersonaType.eve : PersonaType.adam;

        // Persona traits
        if (settings['persona_traits'] != null) {
          final traits = settings['persona_traits'] as Map<String, dynamic>;
          _empathy = (traits['empathy'] ?? 3).toInt();
          _directness = (traits['directness'] ?? 3).toInt();
          _formality = (traits['formality'] ?? 2).toInt();
          _encouragement = (traits['encouragement'] ?? 4).toInt();
        }

        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load settings: $e'),
            backgroundColor: Colors.red[700],
          ),
        );
      }
    }
  }

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
          if (_isSaving)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  color: Color(UIConstants.electricCyan),
                  strokeWidth: 2,
                ),
              ),
            )
          else
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
                  // Voice Gender Selection (Adam/Eve)
                  _buildSectionHeader('Voice Gender', Icons.wc),
                  const SizedBox(height: UIConstants.spacingMD),
                  _buildVoiceGenderSelector(),
                  const SizedBox(height: UIConstants.spacingXL),

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

  Widget _buildVoiceGenderSelector() {
    return Container(
      padding: const EdgeInsets.all(UIConstants.spacingMD),
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Row(
        children: [
          Expanded(
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _voiceGender = PersonaType.adam;
                  // Set default Adam voice when switching
                  _selectedVoice = 'Neural2-C';
                });
              },
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: UIConstants.spacingMD),
                decoration: BoxDecoration(
                  color: _voiceGender == PersonaType.adam
                      ? const Color(UIConstants.electricCyan)
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(UIConstants.spacingSM),
                  border: Border.all(
                    color: _voiceGender == PersonaType.adam
                        ? const Color(UIConstants.electricCyan)
                        : const Color(UIConstants.midGrey),
                    width: 2,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.male,
                      color: _voiceGender == PersonaType.adam
                          ? Colors.black
                          : Colors.white,
                      size: 32,
                    ),
                    const SizedBox(height: UIConstants.spacingXS),
                    Text(
                      'Adam (Male)',
                      style: TextStyle(
                        color: _voiceGender == PersonaType.adam
                            ? Colors.black
                            : Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: UIConstants.spacingMD),
          Expanded(
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _voiceGender = PersonaType.eve;
                  // Set default Eve voice when switching (Neural2-A bright)
                  _selectedVoice = 'Neural2-A';
                });
              },
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: UIConstants.spacingMD),
                decoration: BoxDecoration(
                  color: _voiceGender == PersonaType.eve
                      ? const Color(UIConstants.electricCyan)
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(UIConstants.spacingSM),
                  border: Border.all(
                    color: _voiceGender == PersonaType.eve
                        ? const Color(UIConstants.electricCyan)
                        : const Color(UIConstants.midGrey),
                    width: 2,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.female,
                      color: _voiceGender == PersonaType.eve
                          ? Colors.black
                          : Colors.white,
                      size: 32,
                    ),
                    const SizedBox(height: UIConstants.spacingXS),
                    Text(
                      'Eve (Female)',
                      style: TextStyle(
                        color: _voiceGender == PersonaType.eve
                            ? Colors.black
                            : Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVoiceSelector() {
    // Choose voice map based on selected gender
    final voiceMap = _voiceGender == PersonaType.adam ? _adamVoices : _eveVoices;

    return Container(
      decoration: BoxDecoration(
        color: const Color(UIConstants.darkGrey),
        borderRadius: BorderRadius.circular(UIConstants.spacingMD),
      ),
      child: Column(
        children: voiceMap.entries.map((entry) {
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
            subtitle: _voiceGender == PersonaType.eve
                ? Text(
                    _getVoiceDescription(entry.key),
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.6),
                      fontSize: UIConstants.fontCaption,
                    ),
                  )
                : null,
            activeColor: const Color(UIConstants.electricCyan),
          );
        }).toList(),
      ),
    );
  }

  String _getVoiceDescription(String voiceCode) {
    switch (voiceCode) {
      case 'Neural2-A':
        return 'Energetic and warm tone, perfect for encouragement';
      case 'Neural2-B':
        return 'Gentle and soothing tone, ideal for reflection';
      default:
        return '';
    }
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

  Future<void> _saveSettings() async {
    setState(() => _isSaving = true);

    try {
      final apiService = ref.read(apiServiceProvider);

      // Prepare settings data
      final settings = {
        'voice_type': _selectedVoice,
        'speed': _speed,
        'pitch': _pitch,
        'volume': _volume,
        'persona': _voiceGender.name,  // 'adam' or 'eve'
        'persona_traits': {
          'empathy': _empathy,
          'directness': _directness,
          'formality': _formality,
          'encouragement': _encouragement,
        },
      };

      // Save to backend
      await apiService.updateVoiceSettings(widget.userId, settings);

      setState(() => _isSaving = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Settings saved successfully!'),
            backgroundColor: Color(UIConstants.electricCyan),
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      setState(() => _isSaving = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save settings: $e'),
            backgroundColor: Colors.red[700],
          ),
        );
      }
    }
  }
}
