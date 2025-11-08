/// Camera Service for 1 FPS capture and keyframe selection
library;

import 'dart:io';
import 'dart:async';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image/image.dart' as img;
import '../models/chat_models.dart';
import '../utils/constants.dart';

export 'dart:typed_data' show Uint8List;

class CameraService {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  Timer? _captureTimer;
  final List<CameraFrame> _capturedFrames = [];

  bool _isInitialized = false;
  bool _isCapturing = false;

  bool get isInitialized => _isInitialized;
  bool get isCapturing => _isCapturing;
  CameraController? get controller => _controller;

  /// Initialize camera
  Future<void> initialize() async {
    try {
      // Get available cameras
      _cameras = await availableCameras();

      if (_cameras == null || _cameras!.isEmpty) {
        throw CameraException('사용 가능한 카메라가 없습니다');
      }

      // Use back camera (index 0 is usually back camera)
      final camera = _cameras!.first;

      // Create controller
      _controller = CameraController(
        camera,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );

      // Initialize controller
      await _controller!.initialize();
      _isInitialized = true;
    } catch (e) {
      throw CameraException('카메라 초기화 실패: $e');
    }
  }

  /// Capture a single photo (no continuous capture)
  void startCapture() {
    if (!_isInitialized || _isCapturing) return;

    _isCapturing = true;
    _capturedFrames.clear();

    // Capture one photo immediately
    _captureFrame();
  }

  /// Stop capturing and return the single photo
  Future<List<File>> stopAndGetKeyframes() async {
    if (!_isCapturing) return [];

    _isCapturing = false;

    // Return the single captured photo
    if (_capturedFrames.isEmpty) return [];

    // Convert to file
    final files = await _saveKeyframesToFiles(_capturedFrames);

    // Clear captured frames
    _capturedFrames.clear();

    return files;
  }

  /// Capture a single frame
  Future<void> _captureFrame() async {
    if (!_isInitialized || _controller == null) return;

    try {
      // Take picture
      final image = await _controller!.takePicture();

      // Read and compress image
      final imageBytes = await File(image.path).readAsBytes();
      final compressedBytes = await _compressImage(imageBytes);

      // Store frame
      _capturedFrames.add(CameraFrame(
        imageBytes: compressedBytes,
        timestamp: DateTime.now(),
      ));

      // Delete temporary file
      await File(image.path).delete();
    } catch (e) {
      // Silently fail - don't stop capturing
      // Error is logged but not thrown to avoid stopping capture
    }
  }

  /// Compress image to reduce size
  Future<Uint8List> _compressImage(List<int> imageBytes) async {
    try {
      // Decode image
      final image = img.decodeImage(Uint8List.fromList(imageBytes));
      if (image == null) return Uint8List.fromList(imageBytes);

      // Resize if too large
      img.Image resized = image;
      if (image.width > CameraConfig.maxImageWidth ||
          image.height > CameraConfig.maxImageHeight) {
        resized = img.copyResize(
          image,
          width: image.width > image.height
              ? CameraConfig.maxImageWidth
              : null,
          height: image.height > image.width
              ? CameraConfig.maxImageHeight
              : null,
        );
      }

      // Encode as JPEG with quality
      final compressed = img.encodeJpg(
        resized,
        quality: CameraConfig.imageQuality,
      );

      return Uint8List.fromList(compressed);
    } catch (e) {
      // If compression fails, return original
      return Uint8List.fromList(imageBytes);
    }
  }

  /// Save keyframes to temporary files
  Future<List<File>> _saveKeyframesToFiles(List<CameraFrame> keyframes) async {
    final tempDir = await getTemporaryDirectory();
    final files = <File>[];

    for (int i = 0; i < keyframes.length; i++) {
      final timestamp = keyframes[i].timestamp.millisecondsSinceEpoch;
      final file = File('${tempDir.path}/frame_${timestamp}_$i.jpg');
      await file.writeAsBytes(keyframes[i].imageBytes);
      files.add(file);
    }

    return files;
  }

  /// Dispose camera
  Future<void> dispose() async {
    _captureTimer?.cancel();
    _captureTimer = null;
    _isCapturing = false;

    if (_controller != null) {
      await _controller!.dispose();
      _controller = null;
    }

    _isInitialized = false;
    _capturedFrames.clear();
  }
}

/// Custom Camera Exception
class CameraException implements Exception {
  final String message;

  CameraException(this.message);

  @override
  String toString() => message;
}
