/// Simple logging utility for the app
library;

import 'package:flutter/foundation.dart';

/// Log levels
enum LogLevel {
  debug,
  info,
  warning,
  error,
}

/// Logger class
class Logger {
  static final Logger _instance = Logger._internal();
  factory Logger() => _instance;
  Logger._internal();

  /// Log debug message
  void debug(String message, {Map<String, dynamic>? data}) {
    _log(LogLevel.debug, message, data: data);
  }

  /// Log info message
  void info(String message, {Map<String, dynamic>? data}) {
    _log(LogLevel.info, message, data: data);
  }

  /// Log warning message
  void warning(String message, {Map<String, dynamic>? data}) {
    _log(LogLevel.warning, message, data: data);
  }

  /// Log error message
  void error(
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    _log(
      LogLevel.error,
      message,
      error: error,
      stackTrace: stackTrace,
      data: data,
    );
  }

  /// Internal log method
  void _log(
    LogLevel level,
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    // Only log in debug mode for now
    if (!kDebugMode && level != LogLevel.error) {
      return;
    }

    final timestamp = DateTime.now().toIso8601String();
    final levelStr = level.name.toUpperCase().padRight(7);

    // Base log message
    final logMessage = '[$timestamp] $levelStr: $message';

    // Print based on level
    switch (level) {
      case LogLevel.debug:
        debugPrint('🔍 $logMessage');
        break;
      case LogLevel.info:
        debugPrint('ℹ️  $logMessage');
        break;
      case LogLevel.warning:
        debugPrint('⚠️  $logMessage');
        break;
      case LogLevel.error:
        debugPrint('❌ $logMessage');
        break;
    }

    // Print additional data
    if (data != null && data.isNotEmpty) {
      debugPrint('   Data: $data');
    }

    // Print error details
    if (error != null) {
      debugPrint('   Error: $error');
    }

    // Print stack trace for errors
    if (stackTrace != null && level == LogLevel.error) {
      debugPrint('   Stack trace:');
      final lines = stackTrace.toString().split('\n').take(10);
      for (final line in lines) {
        debugPrint('   $line');
      }
    }
  }

  /// Log app lifecycle events
  void logAppLifecycle(String event) {
    info('App lifecycle: $event');
  }

  /// Log user action
  void logUserAction(String action, {Map<String, dynamic>? data}) {
    info('User action: $action', data: data);
  }

  /// Log API call
  void logApiCall(
    String endpoint, {
    String method = 'GET',
    int? statusCode,
    int? durationMs,
  }) {
    info(
      'API call: $method $endpoint',
      data: {
        'statusCode': statusCode,
        'durationMs': durationMs,
      },
    );
  }

  /// Log performance metric
  void logPerformance(String metric, int valueMs) {
    info('Performance: $metric', data: {'durationMs': valueMs});
  }
}
