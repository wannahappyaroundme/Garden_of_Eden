/// Service Providers using Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../services/camera_service.dart';

/// API Service Provider
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

/// Audio Service Provider
final audioServiceProvider = Provider<AudioService>((ref) {
  return AudioService();
});

/// Camera Service Provider
final cameraServiceProvider = Provider<CameraService>((ref) {
  return CameraService();
});
