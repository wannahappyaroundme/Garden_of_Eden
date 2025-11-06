import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'screens/voice_first_screen.dart';
import 'screens/onboarding_screen.dart';
import 'services/cache_service.dart';
import 'theme/app_theme.dart';
import 'utils/constants.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize cache service
  final cacheService = CacheService();
  await cacheService.initialize();

  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Colors.black,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(
    const ProviderScope(
      child: EdenApp(),
    ),
  );
}

class EdenApp extends StatelessWidget {
  const EdenApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Project Eden V2',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const PermissionHandler(),
    );
  }
}

/// Permission Handler Screen
class PermissionHandler extends StatefulWidget {
  const PermissionHandler({super.key});

  @override
  State<PermissionHandler> createState() => _PermissionHandlerState();
}

class _PermissionHandlerState extends State<PermissionHandler> {
  bool _isChecking = true;
  bool _hasCameraPermission = false;
  bool _hasMicrophonePermission = false;

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    final cameraStatus = await Permission.camera.status;
    final microphoneStatus = await Permission.microphone.status;

    setState(() {
      _hasCameraPermission = cameraStatus.isGranted;
      _hasMicrophonePermission = microphoneStatus.isGranted;
      _isChecking = false;
    });

    if (_hasCameraPermission && _hasMicrophonePermission) {
      _navigateToMain();
    }
  }

  Future<void> _requestPermissions() async {
    setState(() => _isChecking = true);

    final statuses = await [
      Permission.camera,
      Permission.microphone,
    ].request();

    final cameraGranted = statuses[Permission.camera]?.isGranted ?? false;
    final micGranted = statuses[Permission.microphone]?.isGranted ?? false;

    setState(() {
      _hasCameraPermission = cameraGranted;
      _hasMicrophonePermission = micGranted;
      _isChecking = false;
    });

    if (cameraGranted && micGranted) {
      _navigateToMain();
    }
  }

  Future<void> _navigateToMain() async {
    final cacheService = CacheService();

    // Check if onboarding is completed
    final isOnboardingCompleted = await cacheService.isOnboardingCompleted();
    final userId = await cacheService.loadUserId();

    if (!mounted) return;

    if (isOnboardingCompleted && userId != null) {
      // User has completed onboarding - go to main screen
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => VoiceFirstScreen(userId: userId),
        ),
      );
    } else {
      // User needs to complete onboarding - go directly to onboarding with Adam as default
      // Note: Adam and Eve only differ by voice gender now, selectable in settings
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => const OnboardingScreen(persona: PersonaType.adam),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isChecking) {
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: CircularProgressIndicator(color: Colors.white),
        ),
      );
    }

    if (_hasCameraPermission && _hasMicrophonePermission) {
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: CircularProgressIndicator(color: Colors.white),
        ),
      );
    }

    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.security,
                size: 80,
                color: Colors.white,
              ),
              const SizedBox(height: 32),
              const Text(
                '권한 필요',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              const Text(
                'Project Eden은 음성 대화와\n카메라 기능을 사용합니다.',
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 16,
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              _buildPermissionItem(
                icon: Icons.camera_alt,
                title: '카메라',
                granted: _hasCameraPermission,
              ),
              const SizedBox(height: 16),
              _buildPermissionItem(
                icon: Icons.mic,
                title: '마이크',
                granted: _hasMicrophonePermission,
              ),
              const SizedBox(height: 48),
              ElevatedButton(
                onPressed: _requestPermissions,
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 56),
                  backgroundColor: const Color(0xFF00D9FF),
                  foregroundColor: Colors.black,
                ),
                child: const Text(
                  '권한 허용',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPermissionItem({
    required IconData icon,
    required String title,
    required bool granted,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.white, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Icon(
            granted ? Icons.check_circle : Icons.circle_outlined,
            color: granted ? Colors.green : Colors.white54,
          ),
        ],
      ),
    );
  }
}
