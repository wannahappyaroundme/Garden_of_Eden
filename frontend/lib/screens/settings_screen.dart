/// Settings Screen - User preferences and configuration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../providers/app_state_provider.dart';
import '../utils/constants.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  double _ttsVolume = 1.0;
  bool _cameraEnabled = true;
  String _appVersion = '';

  @override
  void initState() {
    super.initState();
    _loadVersion();
  }

  Future<void> _loadVersion() async {
    final packageInfo = await PackageInfo.fromPlatform();
    setState(() {
      _appVersion = packageInfo.version;
    });
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);

    return Scaffold(
      backgroundColor: const Color(UIConstants.pureBlack),
      appBar: AppBar(
        backgroundColor: const Color(UIConstants.deepBlack),
        title: const Text(
          'Settings',
          style: TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(UIConstants.spacingLG),
        children: [
          // Persona Settings
          _buildSection(
            title: 'Persona',
            icon: Icons.person_outline,
            children: [
              _buildPersonaTile(PersonaType.adam, appState.persona),
              _buildPersonaTile(PersonaType.eve, appState.persona),
            ],
          ),

          const SizedBox(height: UIConstants.spacingXL),

          // Audio Settings
          _buildSection(
            title: 'Audio',
            icon: Icons.volume_up,
            children: [
              _buildVolumeSlider(),
            ],
          ),

          const SizedBox(height: UIConstants.spacingXL),

          // Camera Settings
          _buildSection(
            title: 'Camera',
            icon: Icons.camera_alt,
            children: [
              _buildCameraToggle(),
            ],
          ),

          const SizedBox(height: UIConstants.spacingXL),

          // Data Management
          _buildSection(
            title: 'Data',
            icon: Icons.storage,
            children: [
              _buildClearHistoryButton(),
            ],
          ),

          const SizedBox(height: UIConstants.spacingXL),

          // About
          _buildSection(
            title: 'About',
            icon: Icons.info_outline,
            children: [
              _buildAboutInfo(),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required IconData icon,
    required List<Widget> children,
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
        Container(
          decoration: BoxDecoration(
            color: const Color(UIConstants.darkGrey),
            borderRadius: BorderRadius.circular(UIConstants.spacingMD),
          ),
          child: Column(children: children),
        ),
      ],
    );
  }

  Widget _buildPersonaTile(PersonaType persona, PersonaType currentPersona) {
    final isSelected = persona == currentPersona;

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: UIConstants.spacingLG,
        vertical: UIConstants.spacingSM,
      ),
      leading: Icon(
        persona == PersonaType.adam ? Icons.psychology : Icons.auto_awesome,
        color: isSelected
            ? const Color(UIConstants.electricCyan)
            : Colors.white54,
        size: 28,
      ),
      title: Text(
        persona.displayName,
        style: TextStyle(
          color: isSelected ? Colors.white : Colors.white70,
          fontSize: UIConstants.fontBodyLarge,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
      subtitle: Text(
        persona == PersonaType.adam
            ? 'Analytical and strategic coach'
            : 'Empathetic and supportive guide',
        style: TextStyle(
          color: Colors.white.withValues(alpha: 0.5),
          fontSize: UIConstants.fontCaption,
        ),
      ),
      trailing: isSelected
          ? const Icon(
              Icons.check_circle,
              color: Color(UIConstants.electricCyan),
            )
          : null,
      onTap: () {
        ref.read(appStateProvider.notifier).setPersona(persona);
      },
    );
  }

  Widget _buildVolumeSlider() {
    return Padding(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'TTS Volume',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: UIConstants.fontBody,
                ),
              ),
              Text(
                '${(_ttsVolume * 100).toInt()}%',
                style: const TextStyle(
                  color: Color(UIConstants.electricCyan),
                  fontSize: UIConstants.fontBody,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: UIConstants.spacingSM),
          SliderTheme(
            data: SliderThemeData(
              activeTrackColor: const Color(UIConstants.electricCyan),
              inactiveTrackColor: const Color(UIConstants.midGrey),
              thumbColor: const Color(UIConstants.electricCyan),
              overlayColor: const Color(UIConstants.electricCyan).withValues(alpha: 0.2),
              trackHeight: 4,
            ),
            child: Slider(
              value: _ttsVolume,
              min: 0.0,
              max: 1.0,
              divisions: 10,
              onChanged: (value) {
                setState(() {
                  _ttsVolume = value;
                });
                // TODO: Apply to TTS service
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCameraToggle() {
    return SwitchListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: UIConstants.spacingLG,
        vertical: UIConstants.spacingSM,
      ),
      title: const Text(
        'Enable Camera',
        style: TextStyle(
          color: Colors.white,
          fontSize: UIConstants.fontBody,
        ),
      ),
      subtitle: Text(
        _cameraEnabled
            ? 'Camera captures visual context'
            : 'Camera disabled - voice only',
        style: TextStyle(
          color: Colors.white.withValues(alpha: 0.5),
          fontSize: UIConstants.fontCaption,
        ),
      ),
      value: _cameraEnabled,
      activeThumbColor: const Color(UIConstants.electricCyan),
      activeTrackColor: const Color(UIConstants.electricCyan).withValues(alpha: 0.5),
      inactiveThumbColor: const Color(UIConstants.midGrey),
      inactiveTrackColor: const Color(UIConstants.darkGrey),
      onChanged: (value) {
        setState(() {
          _cameraEnabled = value;
        });
        // TODO: Apply to camera service
      },
    );
  }

  Widget _buildClearHistoryButton() {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: UIConstants.spacingLG,
        vertical: UIConstants.spacingSM,
      ),
      leading: const Icon(
        Icons.delete_outline,
        color: Colors.red,
        size: 28,
      ),
      title: const Text(
        'Clear Conversation History',
        style: TextStyle(
          color: Colors.white,
          fontSize: UIConstants.fontBody,
        ),
      ),
      subtitle: Text(
        'Delete all local conversation data',
        style: TextStyle(
          color: Colors.white.withValues(alpha: 0.5),
          fontSize: UIConstants.fontCaption,
        ),
      ),
      onTap: () {
        _showClearHistoryDialog();
      },
    );
  }

  Future<void> _showClearHistoryDialog() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(UIConstants.darkGrey),
        title: const Text(
          'Clear History?',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'This will delete all conversation history stored on this device. This action cannot be undone.',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text(
              'Cancel',
              style: TextStyle(color: Colors.white54),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(
              foregroundColor: Colors.red,
            ),
            child: const Text('Clear'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      // TODO: Implement clear history
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('History cleared'),
          backgroundColor: Color(UIConstants.stateResponding),
        ),
      );
    }
  }

  Widget _buildAboutInfo() {
    return Padding(
      padding: const EdgeInsets.all(UIConstants.spacingLG),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAboutRow('App Name', 'Project Eden V2'),
          const SizedBox(height: UIConstants.spacingSM),
          _buildAboutRow('Version', _appVersion.isNotEmpty ? _appVersion : 'Loading...'),
          const SizedBox(height: UIConstants.spacingSM),
          _buildAboutRow('Build', 'Mobile (Flutter)'),
          const SizedBox(height: UIConstants.spacingMD),
          Text(
            'An AI companion that learns and grows with you, helping you stay focused on your "One Thing".',
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.6),
              fontSize: UIConstants.fontCaption,
              height: 1.5,
            ),
          ),
          const SizedBox(height: UIConstants.spacingMD),
          Center(
            child: TextButton(
              onPressed: () {
                // TODO: Open GitHub or website
              },
              child: const Text(
                'Learn More',
                style: TextStyle(
                  color: Color(UIConstants.electricCyan),
                  fontSize: UIConstants.fontBody,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAboutRow(String label, String value) {
    return Row(
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
    );
  }
}
