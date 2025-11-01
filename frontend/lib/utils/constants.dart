/// Constants for Project Eden V2 Mobile App
library;

/// App Modes
enum AppMode {
  idle,
  listening,
  processing,
  responding,
}

/// Persona Types
enum PersonaType {
  adam,
  eve;

  String get displayName => name[0].toUpperCase() + name.substring(1);
}

/// API Configuration
class ApiConfig {
  static const String baseUrl = 'http://192.168.219.109:8000';  // Local IP for device testing
  static const String chatEndpoint = '/api/v2/chat';
  static const String profileEndpoint = '/api/v2/profile';
  static const String sttEndpoint = '/api/v2/stt';

  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}

/// Camera Configuration
class CameraConfig {
  static const int captureIntervalMs = 1000;  // 1 FPS
  static const int maxKeyframes = 8;
  static const int imageQuality = 85;
  static const int maxImageWidth = 1024;
  static const int maxImageHeight = 1024;
}

/// Audio Configuration
class AudioConfig {
  static const int sampleRate = 16000;
  static const Duration maxRecordingDuration = Duration(minutes: 5);
}

/// UI Constants
class UIConstants {
  // Colors
  static const pureBlack = 0xFF000000;
  static const deepBlack = 0xFF0A0A0A;
  static const darkGrey = 0xFF1A1A1A;
  static const midGrey = 0xFF404040;
  static const lightGrey = 0xFF808080;
  static const offWhite = 0xFFF5F5F5;
  static const pureWhite = 0xFFFFFFFF;

  // Accent Color
  static const electricCyan = 0xFF00D9FF;

  // State Colors
  static const stateListening = 0xFFFF3B30;  // Red
  static const stateProcessing = 0xFF007AFF;  // Blue
  static const stateResponding = 0xFF34C759;  // Green
  static const statePitfall = 0xFFFFCC00;     // Amber

  // Spacing (8pt grid)
  static const double spacingMicro = 4.0;
  static const double spacingXS = 8.0;
  static const double spacingSM = 12.0;
  static const double spacingMD = 16.0;
  static const double spacingLG = 24.0;
  static const double spacingXL = 32.0;
  static const double spacingXXL = 48.0;
  static const double spacingXXXL = 64.0;

  // Button Sizes
  static const double pushToTalkButtonSize = 120.0;
  static const double pushToTalkIconSize = 60.0;

  // Animation Durations
  static const Duration animInstant = Duration(milliseconds: 100);
  static const Duration animQuick = Duration(milliseconds: 200);
  static const Duration animMedium = Duration(milliseconds: 300);
  static const Duration animSlow = Duration(milliseconds: 500);
  static const Duration animSlower = Duration(milliseconds: 700);

  // Typography
  static const double fontDisplay = 32.0;
  static const double fontHeadline = 24.0;
  static const double fontTitle = 20.0;
  static const double fontBodyLarge = 17.0;
  static const double fontBody = 15.0;
  static const double fontCaption = 13.0;
  static const double fontLabel = 11.0;

  // Response Overlay
  static const double responseOverlayHeightRatio = 0.33;  // 1/3 of screen
  static const Duration responseAutoHideDuration = Duration(seconds: 3);
}

/// Error Messages
class ErrorMessages {
  static const String permissionDenied = '권한이 필요합니다';
  static const String cameraError = '카메라 오류가 발생했습니다';
  static const String microphoneError = '마이크 오류가 발생했습니다';
  static const String networkError = '네트워크 연결을 확인해주세요';
  static const String serverError = '서버 오류가 발생했습니다';
  static const String unknownError = '알 수 없는 오류가 발생했습니다';
}
