/// API Service for backend communication
library;

import 'dart:io';
import 'package:dio/dio.dart';
import '../models/chat_models.dart';
import '../utils/constants.dart';

class ApiService {
  late final Dio _dio;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectionTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      headers: {
        'Accept': 'application/json',
      },
    ));

    // Add interceptors for logging
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      error: true,
    ));
  }

  /// Send chat message to backend
  Future<ChatResponse> sendChat({
    required String userId,
    required String message,
    required PersonaType voiceType,
    String? sessionId,
    File? audioFile,
    List<File>? cameraFrames,
  }) async {
    try {
      // Prepare form data
      final formData = FormData.fromMap({
        'user_id': userId,
        'message': message,
        'voice_type': voiceType.name,
        if (sessionId != null) 'session_id': sessionId,
      });

      // Add audio file if provided
      if (audioFile != null) {
        formData.files.add(MapEntry(
          'audio_file',
          await MultipartFile.fromFile(
            audioFile.path,
            filename: 'audio.m4a',
          ),
        ));
      }

      // Add camera frames if provided
      if (cameraFrames != null && cameraFrames.isNotEmpty) {
        for (var frame in cameraFrames) {
          formData.files.add(MapEntry(
            'camera_frames',
            await MultipartFile.fromFile(
              frame.path,
              filename: 'frame_${DateTime.now().millisecondsSinceEpoch}.jpg',
            ),
          ));
        }
      }

      // Send request
      final response = await _dio.post(
        ApiConfig.chatEndpoint,
        data: formData,
      );

      // Parse response
      return ChatResponse.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _handleDioError(e);
    } catch (e) {
      throw ApiException('알 수 없는 오류가 발생했습니다: $e');
    }
  }

  /// Get user profile
  Future<UserProfile> getProfile(String userId) async {
    try {
      final response = await _dio.get('${ApiConfig.profileEndpoint}/$userId');
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// Update user profile
  Future<UserProfile> updateProfile({
    required String userId,
    String? oneThing,
    String? coreIdentity,
    String? coreMotivation,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (oneThing != null) data['one_thing'] = oneThing;
      if (coreIdentity != null) data['core_identity'] = coreIdentity;
      if (coreMotivation != null) data['core_motivation'] = coreMotivation;

      final response = await _dio.patch(
        '${ApiConfig.profileEndpoint}/$userId',
        data: data,
      );

      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// Handle Dio errors
  ApiException _handleDioError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(ErrorMessages.networkError);

      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        if (statusCode == 404) {
          return ApiException('리소스를 찾을 수 없습니다');
        } else if (statusCode == 500) {
          return ApiException(ErrorMessages.serverError);
        }
        return ApiException('서버 오류: $statusCode');

      case DioExceptionType.cancel:
        return ApiException('요청이 취소되었습니다');

      case DioExceptionType.connectionError:
        return ApiException(ErrorMessages.networkError);

      default:
        return ApiException(ErrorMessages.unknownError);
    }
  }
}

/// Custom API Exception
class ApiException implements Exception {
  final String message;

  ApiException(this.message);

  @override
  String toString() => message;
}
