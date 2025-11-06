/// API Service for backend communication
library;

import 'dart:io';
import 'dart:convert';
import 'package:dio/dio.dart';
import '../models/chat_models.dart';
import '../models/goal_models.dart';
import '../utils/constants.dart';

class ApiService {
  late final Dio _dio;

  // Retry configuration
  static const int maxRetries = 3;
  static const List<Duration> retryDelays = [
    Duration(seconds: 1),
    Duration(seconds: 2),
    Duration(seconds: 4),
  ];

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

  /// Retry a request with exponential backoff
  Future<T> _retryableRequest<T>({
    required Future<T> Function() request,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    Exception? lastError;

    for (int attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await request();
      } on DioException catch (e) {
        lastError = _handleDioError(e);

        // Don't retry on client errors (4xx)
        if (e.response?.statusCode != null &&
            e.response!.statusCode! >= 400 &&
            e.response!.statusCode! < 500) {
          throw lastError;
        }

        // Last attempt - throw error
        if (attempt == maxRetries - 1) {
          throw lastError;
        }

        // Notify about retry
        if (onRetry != null) {
          onRetry(attempt + 1, lastError);
        }

        // Wait before retry
        await Future.delayed(retryDelays[attempt]);
      } catch (e) {
        lastError = ApiException('알 수 없는 오류: $e');
        if (attempt == maxRetries - 1) {
          throw lastError;
        }
        if (onRetry != null) {
          onRetry(attempt + 1, lastError);
        }
        await Future.delayed(retryDelays[attempt]);
      }
    }

    throw lastError ?? ApiException('최대 재시도 횟수를 초과했습니다');
  }

  /// Send chat message to backend (with retry)
  Future<ChatResponse> sendChat({
    required String userId,
    required String message,
    required PersonaType voiceType,
    String? sessionId,
    File? audioFile,
    List<File>? cameraFrames,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<ChatResponse>(
      request: () async {
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
      },
      onRetry: onRetry,
    );
  }

  /// Transcribe audio file to text (STT)
  Future<String> transcribeAudio({
    required File audioFile,
    String language = 'ko',
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<String>(
      request: () async {
        // Prepare form data
        final formData = FormData.fromMap({
          'language': language,
          'audio_file': await MultipartFile.fromFile(
            audioFile.path,
            filename: 'audio.m4a',
          ),
        });

        // Send request
        final response = await _dio.post(
          ApiConfig.sttEndpoint,
          data: formData,
        );

        // Extract transcription text from response
        final data = response.data as Map<String, dynamic>;
        return data['text'] as String;
      },
      onRetry: onRetry,
    );
  }

  /// Get user profile (with retry)
  Future<UserProfile> getProfile(String userId) async {
    return _retryableRequest<UserProfile>(
      request: () async {
        final response = await _dio.get('${ApiConfig.profileEndpoint}/$userId');
        return UserProfile.fromJson(response.data as Map<String, dynamic>);
      },
    );
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

  // ========== Onboarding API Methods ==========

  /// Start onboarding session
  Future<OnboardingResponse> startOnboarding({
    required String userId,
    required PersonaType persona,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<OnboardingResponse>(
      request: () async {
        final response = await _dio.post(
          ApiConfig.onboardingStartEndpoint,
          data: {
            'user_id': userId,
            'persona': persona.name,
          },
        );

        return OnboardingResponse.fromJson(response.data as Map<String, dynamic>);
      },
      onRetry: onRetry,
    );
  }

  /// Respond to onboarding question
  Future<OnboardingResponse> respondToOnboarding({
    required String sessionId,
    required String userResponse,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<OnboardingResponse>(
      request: () async {
        final response = await _dio.post(
          ApiConfig.onboardingRespondEndpoint,
          data: {
            'session_id': sessionId,
            'user_response': userResponse,
          },
        );

        return OnboardingResponse.fromJson(response.data as Map<String, dynamic>);
      },
      onRetry: onRetry,
    );
  }

  /// Get onboarding status
  Future<Map<String, dynamic>> getOnboardingStatus(String sessionId) async {
    return _retryableRequest<Map<String, dynamic>>(
      request: () async {
        final response = await _dio.get(
          '${ApiConfig.onboardingStatusEndpoint}/$sessionId',
        );

        return response.data as Map<String, dynamic>;
      },
    );
  }

  // ========== Session API Methods ==========

  /// Create new conversation session
  Future<SessionInfo> createSession({
    required String userId,
    required PersonaType persona,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<SessionInfo>(
      request: () async {
        final response = await _dio.post(
          ApiConfig.sessionCreateEndpoint,
          data: {
            'user_id': userId,
            'persona': persona.name,
          },
        );

        return SessionInfo.fromJson(response.data as Map<String, dynamic>);
      },
      onRetry: onRetry,
    );
  }

  /// Get session information by session ID
  Future<SessionInfo> getSessionInfo(String sessionId) async {
    return _retryableRequest<SessionInfo>(
      request: () async {
        final response = await _dio.get(
          '${ApiConfig.sessionInfoEndpoint}/$sessionId',
        );

        return SessionInfo.fromJson(response.data as Map<String, dynamic>);
      },
    );
  }

  /// Get user's active session (if any)
  Future<SessionInfo?> getUserActiveSession(String userId) async {
    return _retryableRequest<SessionInfo?>(
      request: () async {
        try {
          final response = await _dio.get(
            '${ApiConfig.sessionUserEndpoint}/$userId',
          );

          return SessionInfo.fromJson(response.data as Map<String, dynamic>);
        } on DioException catch (e) {
          // Return null if no active session (404)
          if (e.response?.statusCode == 404) {
            return null;
          }
          rethrow;
        }
      },
    );
  }

  /// Close an active session
  Future<void> closeSession({
    required String sessionId,
    String reason = 'User closed session',
  }) async {
    try {
      await _dio.post(
        '${ApiConfig.sessionCloseEndpoint}/$sessionId/close',
        data: {
          'reason': reason,
        },
      );
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // ========== Goal Progress API Methods ==========

  /// Create a new goal from user's One Thing
  Future<CreateGoalResponse> createGoal({
    required String userId,
    String? targetDate,
    String? description,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<CreateGoalResponse>(
      request: () async {
        final formData = FormData.fromMap({
          'user_id': userId,
          if (targetDate != null) 'target_date': targetDate,
          if (description != null) 'description': description,
        });

        final response = await _dio.post(
          ApiConfig.goalsCreateEndpoint,
          data: formData,
        );

        return CreateGoalResponse.fromJson(response.data as Map<String, dynamic>);
      },
      onRetry: onRetry,
    );
  }

  /// Get comprehensive goal summary with insights
  Future<GoalSummary> getGoalSummary(String userId) async {
    return _retryableRequest<GoalSummary>(
      request: () async {
        final response = await _dio.get('${ApiConfig.goalsEndpoint}/$userId');
        return GoalSummary.fromJson(response.data as Map<String, dynamic>);
      },
    );
  }

  /// Record progress snapshot
  Future<RecordProgressResponse> recordProgress({
    required String userId,
    String? reflection,
    int? moodRating,
    List<Map<String, dynamic>>? metrics,
    String? photoUrl,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<RecordProgressResponse>(
      request: () async {
        final formData = FormData.fromMap({
          if (reflection != null) 'reflection': reflection,
          if (moodRating != null) 'mood_rating': moodRating,
          if (metrics != null) 'metrics': jsonEncode(metrics),
          if (photoUrl != null) 'photo_url': photoUrl,
        });

        final response = await _dio.post(
          '${ApiConfig.goalsEndpoint}/$userId/progress',
          data: formData,
        );

        return RecordProgressResponse.fromJson(response.data as Map<String, dynamic>);
      },
      onRetry: onRetry,
    );
  }

  /// Add a custom milestone
  Future<Map<String, dynamic>> addMilestone({
    required String userId,
    required String description,
    String? targetDate,
    String? reward,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<Map<String, dynamic>>(
      request: () async {
        final formData = FormData.fromMap({
          'description': description,
          if (targetDate != null) 'target_date': targetDate,
          if (reward != null) 'reward': reward,
        });

        final response = await _dio.post(
          '${ApiConfig.goalsEndpoint}/$userId/milestones',
          data: formData,
        );

        return response.data as Map<String, dynamic>;
      },
      onRetry: onRetry,
    );
  }

  /// Update milestone completion status
  Future<Map<String, dynamic>> updateMilestoneStatus({
    required String userId,
    required String milestoneId,
    required bool isCompleted,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<Map<String, dynamic>>(
      request: () async {
        final formData = FormData.fromMap({
          'is_completed': isCompleted,
        });

        final response = await _dio.patch(
          '${ApiConfig.goalsEndpoint}/$userId/milestones/$milestoneId',
          data: formData,
        );

        return response.data as Map<String, dynamic>;
      },
      onRetry: onRetry,
    );
  }

  /// Configure tracked metrics for the goal
  Future<Map<String, dynamic>> setupTrackedMetrics({
    required String userId,
    required List<String> metricNames,
    required Map<String, String> metricUnits,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<Map<String, dynamic>>(
      request: () async {
        final config = {
          'metrics': metricNames,
          'units': metricUnits,
        };

        final formData = FormData.fromMap({
          'metrics_config': jsonEncode(config),
        });

        final response = await _dio.post(
          '${ApiConfig.goalsEndpoint}/$userId/setup-metrics',
          data: formData,
        );

        return response.data as Map<String, dynamic>;
      },
      onRetry: onRetry,
    );
  }

  /// Get progress history for last N days
  Future<ProgressHistoryResponse> getProgressHistory({
    required String userId,
    int days = 30,
  }) async {
    return _retryableRequest<ProgressHistoryResponse>(
      request: () async {
        final response = await _dio.get(
          '${ApiConfig.goalsEndpoint}/$userId/history',
          queryParameters: {'days': days},
        );

        return ProgressHistoryResponse.fromJson(response.data as Map<String, dynamic>);
      },
    );
  }

  /// Generate AI-powered insights about progress
  Future<List<GoalInsight>> generateInsights({
    required String userId,
    Function(int attempt, Exception error)? onRetry,
  }) async {
    return _retryableRequest<List<GoalInsight>>(
      request: () async {
        final response = await _dio.post(
          '${ApiConfig.goalsEndpoint}/$userId/insights',
        );

        final data = response.data as Map<String, dynamic>;
        final insightsData = data['insights'] as List<dynamic>;

        return insightsData
            .map((i) => GoalInsight.fromJson(i as Map<String, dynamic>))
            .toList();
      },
      onRetry: onRetry,
    );
  }

  // ==================== Voice Settings ====================

  /// Get voice settings for user
  Future<Map<String, dynamic>> getVoiceSettings(String userId) async {
    return await _retryableRequest(
      request: () async {
        final response = await _dio.get(
          '${ApiConfig.voiceSettingsEndpoint}/$userId/settings',
        );
        return response.data as Map<String, dynamic>;
      },
    );
  }

  /// Update voice settings for user
  Future<void> updateVoiceSettings(
    String userId,
    Map<String, dynamic> settings,
  ) async {
    return await _retryableRequest(
      request: () async {
        await _dio.put(
          '${ApiConfig.voiceSettingsEndpoint}/$userId/settings',
          data: settings,
        );
      },
    );
  }

  /// Get available voice options
  Future<List<dynamic>> getAvailableVoices() async {
    return await _retryableRequest(
      request: () async {
        final response = await _dio.get(ApiConfig.voiceAvailableEndpoint);
        return response.data as List<dynamic>;
      },
    );
  }

  /// Get persona trait configurations
  Future<Map<String, dynamic>> getPersonaTraits() async {
    return await _retryableRequest(
      request: () async {
        final response = await _dio.get(ApiConfig.voicePersonaTraitsEndpoint);
        return response.data as Map<String, dynamic>;
      },
    );
  }

  // ==================== Interaction Mode ====================

  /// Get user's interaction mode (ai_led or user_led)
  Future<String> getInteractionMode(String userId) async {
    return await _retryableRequest(
      request: () async {
        final response = await _dio.get(
          '${ApiConfig.interactionModeEndpoint}/$userId/interaction-mode',
        );
        return response.data['mode'] as String;
      },
    );
  }

  /// Update user's interaction mode
  Future<void> updateInteractionMode(String userId, String mode) async {
    return await _retryableRequest(
      request: () async {
        await _dio.put(
          '${ApiConfig.interactionModeEndpoint}/$userId/interaction-mode',
          data: {'mode': mode},
        );
      },
    );
  }

  // ==================== Notification Settings ====================

  /// Get notification settings for user
  Future<Map<String, dynamic>> getNotificationSettings(String userId) async {
    return await _retryableRequest(
      request: () async {
        final response = await _dio.get(
          '${ApiConfig.notificationSettingsEndpoint}/$userId/settings',
        );
        return response.data as Map<String, dynamic>;
      },
    );
  }

  /// Update notification settings for user
  Future<void> updateNotificationSettings(
    String userId,
    Map<String, dynamic> settings,
  ) async {
    return await _retryableRequest(
      request: () async {
        await _dio.put(
          '${ApiConfig.notificationSettingsEndpoint}/$userId/settings',
          data: settings,
        );
      },
    );
  }

  // ==================== Error Handling ====================

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
