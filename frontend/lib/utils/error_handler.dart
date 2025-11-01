/// Global error handler for the app
library;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'logger.dart';

/// Error types
enum ErrorType {
  network,
  permission,
  storage,
  camera,
  microphone,
  api,
  unknown,
}

/// App exception with context
class AppException implements Exception {
  final String message;
  final ErrorType type;
  final dynamic originalError;
  final StackTrace? stackTrace;

  AppException(
    this.message, {
    this.type = ErrorType.unknown,
    this.originalError,
    this.stackTrace,
  });

  @override
  String toString() => message;
}

/// Global error handler
class ErrorHandler {
  static final ErrorHandler _instance = ErrorHandler._internal();
  factory ErrorHandler() => _instance;
  ErrorHandler._internal();

  final Logger _logger = Logger();

  /// Initialize error handling
  void initialize() {
    // Catch Flutter framework errors
    FlutterError.onError = (FlutterErrorDetails details) {
      _logger.error(
        'Flutter Error',
        error: details.exception,
        stackTrace: details.stack,
      );

      if (kDebugMode) {
        FlutterError.presentError(details);
      }
    };

    // Catch async errors
    PlatformDispatcher.instance.onError = (error, stack) {
      _logger.error(
        'Async Error',
        error: error,
        stackTrace: stack,
      );
      return true;
    };
  }

  /// Handle app errors with user-friendly messages
  String handleError(dynamic error, {StackTrace? stackTrace}) {
    _logger.error('Handling error', error: error, stackTrace: stackTrace);

    if (error is AppException) {
      return _getErrorMessage(error.type, error.message);
    }

    // Parse common errors
    final errorString = error.toString().toLowerCase();

    if (errorString.contains('network') ||
        errorString.contains('socket') ||
        errorString.contains('connection')) {
      return _getErrorMessage(ErrorType.network);
    }

    if (errorString.contains('permission')) {
      return _getErrorMessage(ErrorType.permission);
    }

    if (errorString.contains('camera')) {
      return _getErrorMessage(ErrorType.camera);
    }

    if (errorString.contains('microphone') ||
        errorString.contains('audio') ||
        errorString.contains('record')) {
      return _getErrorMessage(ErrorType.microphone);
    }

    if (errorString.contains('storage') || errorString.contains('disk')) {
      return _getErrorMessage(ErrorType.storage);
    }

    return _getErrorMessage(ErrorType.unknown, error.toString());
  }

  /// Get user-friendly error message
  String _getErrorMessage(ErrorType type, [String? details]) {
    switch (type) {
      case ErrorType.network:
        return '네트워크 연결을 확인해주세요';
      case ErrorType.permission:
        return '필요한 권한이 허용되지 않았습니다';
      case ErrorType.storage:
        return '저장 공간이 부족합니다';
      case ErrorType.camera:
        return '카메라를 사용할 수 없습니다';
      case ErrorType.microphone:
        return '마이크를 사용할 수 없습니다';
      case ErrorType.api:
        return '서버와 통신 중 오류가 발생했습니다';
      case ErrorType.unknown:
        return details ?? '알 수 없는 오류가 발생했습니다';
    }
  }

  /// Show error snackbar
  void showError(BuildContext context, dynamic error) {
    final message = handleError(error);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[700],
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 4),
        action: SnackBarAction(
          label: '확인',
          textColor: Colors.white,
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
      ),
    );
  }

  /// Create app-specific exceptions
  static AppException networkError(String message, {dynamic originalError}) {
    return AppException(
      message,
      type: ErrorType.network,
      originalError: originalError,
    );
  }

  static AppException permissionError(String message, {dynamic originalError}) {
    return AppException(
      message,
      type: ErrorType.permission,
      originalError: originalError,
    );
  }

  static AppException storageError(String message, {dynamic originalError}) {
    return AppException(
      message,
      type: ErrorType.storage,
      originalError: originalError,
    );
  }

  static AppException cameraError(String message, {dynamic originalError}) {
    return AppException(
      message,
      type: ErrorType.camera,
      originalError: originalError,
    );
  }

  static AppException microphoneError(String message, {dynamic originalError}) {
    return AppException(
      message,
      type: ErrorType.microphone,
      originalError: originalError,
    );
  }

  static AppException apiError(String message, {dynamic originalError}) {
    return AppException(
      message,
      type: ErrorType.api,
      originalError: originalError,
    );
  }
}

/// Error boundary widget
class ErrorBoundary extends StatefulWidget {
  final Widget child;
  final Widget Function(Object error)? errorBuilder;

  const ErrorBoundary({
    super.key,
    required this.child,
    this.errorBuilder,
  });

  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}

class _ErrorBoundaryState extends State<ErrorBoundary> {
  Object? _error;

  @override
  void initState() {
    super.initState();
    ErrorHandler().initialize();
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return widget.errorBuilder?.call(_error!) ??
          _DefaultErrorWidget(error: _error!);
    }

    return widget.child;
  }
}

/// Default error widget
class _DefaultErrorWidget extends StatelessWidget {
  final Object error;

  const _DefaultErrorWidget({required this.error});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline,
                  color: Colors.red,
                  size: 64,
                ),
                const SizedBox(height: 24),
                const Text(
                  '오류가 발생했습니다',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  ErrorHandler().handleError(error),
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 16,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                ElevatedButton(
                  onPressed: () {
                    // Restart app (would need platform channel in real app)
                  },
                  child: const Text('앱 재시작'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
