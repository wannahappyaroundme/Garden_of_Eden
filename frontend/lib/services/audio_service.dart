/// Audio Service for recording and playback
library;

import 'dart:io';
import 'dart:convert';
import 'package:record/record.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import '../utils/constants.dart';

class AudioService {
  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();

  String? _currentRecordingPath;
  bool _isRecording = false;
  bool _isPlaying = false;

  bool get isRecording => _isRecording;
  bool get isPlaying => _isPlaying;

  /// Start recording audio
  Future<void> startRecording() async {
    try {
      // Check permission
      if (!await _recorder.hasPermission()) {
        throw AudioException('마이크 권한이 필요합니다');
      }

      // Get temporary directory
      final tempDir = await getTemporaryDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      _currentRecordingPath = '${tempDir.path}/recording_$timestamp.m4a';

      // Start recording
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc,
          sampleRate: AudioConfig.sampleRate,
          bitRate: 128000,
        ),
        path: _currentRecordingPath!,
      );

      _isRecording = true;
    } catch (e) {
      throw AudioException('녹음 시작 실패: $e');
    }
  }

  /// Stop recording and return the file
  Future<File?> stopRecording() async {
    try {
      if (!_isRecording) return null;

      final path = await _recorder.stop();
      _isRecording = false;

      if (path != null && await File(path).exists()) {
        return File(path);
      }

      return null;
    } catch (e) {
      _isRecording = false;
      throw AudioException('녹음 중지 실패: $e');
    }
  }

  /// Play audio from file
  Future<void> playFromFile(File audioFile) async {
    try {
      await _player.setFilePath(audioFile.path);
      _isPlaying = true;

      await _player.play();

      // Listen for completion
      _player.playerStateStream.listen((state) {
        if (state.processingState == ProcessingState.completed) {
          _isPlaying = false;
        }
      });
    } catch (e) {
      _isPlaying = false;
      throw AudioException('재생 실패: $e');
    }
  }

  /// Play audio from base64 string
  Future<void> playFromBase64(String base64Audio) async {
    try {
      // Decode base64
      final bytes = base64Decode(base64Audio);

      // Save to temporary file
      final tempDir = await getTemporaryDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final tempFile = File('${tempDir.path}/tts_$timestamp.mp3');
      await tempFile.writeAsBytes(bytes);

      // Play
      await playFromFile(tempFile);

      // Clean up after playback
      _player.playerStateStream.listen((state) async {
        if (state.processingState == ProcessingState.completed) {
          try {
            await tempFile.delete();
          } catch (_) {}
        }
      });
    } catch (e) {
      throw AudioException('TTS 재생 실패: $e');
    }
  }

  /// Stop playback
  Future<void> stopPlayback() async {
    try {
      await _player.stop();
      _isPlaying = false;
    } catch (e) {
      throw AudioException('재생 중지 실패: $e');
    }
  }

  /// Pause playback
  Future<void> pausePlayback() async {
    try {
      await _player.pause();
    } catch (e) {
      throw AudioException('일시정지 실패: $e');
    }
  }

  /// Resume playback
  Future<void> resumePlayback() async {
    try {
      await _player.play();
    } catch (e) {
      throw AudioException('재개 실패: $e');
    }
  }

  /// Get current playback position
  Stream<Duration> get positionStream => _player.positionStream;

  /// Get total duration
  Duration? get duration => _player.duration;

  /// Dispose resources
  Future<void> dispose() async {
    await _recorder.dispose();
    await _player.dispose();

    // Clean up temporary recording file
    if (_currentRecordingPath != null) {
      try {
        final file = File(_currentRecordingPath!);
        if (await file.exists()) {
          await file.delete();
        }
      } catch (_) {}
    }
  }
}

/// Custom Audio Exception
class AudioException implements Exception {
  final String message;

  AudioException(this.message);

  @override
  String toString() => message;
}
