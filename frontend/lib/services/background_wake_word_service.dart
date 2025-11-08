/// Background Wake Word Service - Keeps wake word detection running in background
library;

import 'dart:async';
import 'dart:isolate';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import '../utils/constants.dart';

/// Background wake word task handler
@pragma('vm:entry-point')
void startBackgroundWakeWordTask() {
  FlutterForegroundTask.setTaskHandler(BackgroundWakeWordTaskHandler());
}

/// Task handler for background wake word detection
class BackgroundWakeWordTaskHandler extends TaskHandler {
  SendPort? _sendPort;
  int _eventCount = 0;

  @override
  void onStart(DateTime timestamp, SendPort? sendPort) async {
    _sendPort = sendPort;

    // Initialize wake word detection in background
    // Note: Porcupine automatically continues listening in background
    // This foreground service just keeps the app alive

    _sendPort?.send('Background wake word service started');
  }

  @override
  void onRepeatEvent(DateTime timestamp, SendPort? sendPort) async {
    // This is called every few seconds (configured in NotificationOptions)
    // We use it to keep the service alive and monitor status

    _eventCount++;

    // Send heartbeat to foreground
    _sendPort?.send({
      'status': 'listening',
      'timestamp': timestamp.toIso8601String(),
      'eventCount': _eventCount,
    });
  }

  @override
  void onDestroy(DateTime timestamp, SendPort? sendPort) async {
    // Clean up when service is stopped
    _sendPort?.send('Background wake word service stopped');
  }

  @override
  void onNotificationButtonPressed(String id) {
    // Handle notification button presses
    if (id == 'stop_listening') {
      FlutterForegroundTask.stopService();
    }
  }

  @override
  void onNotificationPressed() {
    // Handle notification tap - bring app to foreground
    FlutterForegroundTask.launchApp('/');
  }
}

/// Background wake word service manager
class BackgroundWakeWordService {
  static final BackgroundWakeWordService _instance = BackgroundWakeWordService._internal();
  factory BackgroundWakeWordService() => _instance;
  BackgroundWakeWordService._internal();

  bool _isServiceRunning = false;
  ReceivePort? _receivePort;

  /// Initialize the background service
  Future<void> initialize() async {
    // Initialize foreground task
    FlutterForegroundTask.init(
      androidNotificationOptions: AndroidNotificationOptions(
        id: 123,
        channelId: 'wake_word_service',
        channelName: 'Wake Word Detection',
        channelDescription: 'Listening for "Hey Adam" wake word',
        channelImportance: NotificationChannelImportance.LOW,
        priority: NotificationPriority.LOW,
        iconData: const NotificationIconData(
          resType: ResourceType.mipmap,
          resPrefix: ResourcePrefix.ic,
          name: 'launcher',
        ),
        buttons: [
          const NotificationButton(
            id: 'stop_listening',
            text: 'Stop Listening',
          ),
        ],
      ),
      iosNotificationOptions: const IOSNotificationOptions(
        showNotification: true,
        playSound: false,
      ),
      foregroundTaskOptions: const ForegroundTaskOptions(
        interval: 5000, // 5 seconds heartbeat
        isOnceEvent: false,
        autoRunOnBoot: false,
        allowWakeLock: true,
        allowWifiLock: false,
      ),
    );
  }

  /// Start background listening
  Future<bool> startBackgroundListening(PersonaType persona) async {
    // Check if service is already running
    if (_isServiceRunning) {
      return true;
    }

    // Request notification permission (required for foreground service)
    final notificationPermission = await FlutterForegroundTask.checkNotificationPermission();
    if (notificationPermission != NotificationPermission.granted) {
      await FlutterForegroundTask.requestNotificationPermission();
    }

    // Start foreground service
    final serviceStarted = await FlutterForegroundTask.startService(
      notificationTitle: persona == PersonaType.adam ? 'Listening for "Hey Adam"' : 'Listening for "Hey Eve"',
      notificationText: 'Wake word detection is active',
      callback: startBackgroundWakeWordTask,
    );

    if (serviceStarted) {
      _isServiceRunning = true;

      // Setup receive port to get messages from background
      _receivePort = await FlutterForegroundTask.receivePort;
      _receivePort?.listen((message) {
        print('[Background Wake Word] $message');
      });
    }

    return serviceStarted;
  }

  /// Stop background listening
  Future<bool> stopBackgroundListening() async {
    if (!_isServiceRunning) {
      return true;
    }

    final stopped = await FlutterForegroundTask.stopService();

    if (stopped) {
      _isServiceRunning = false;
      _receivePort?.close();
      _receivePort = null;
    }

    return stopped;
  }

  /// Check if service is running
  bool get isRunning => _isServiceRunning;

  /// Update notification (e.g., when persona changes)
  Future<void> updateNotification(PersonaType persona) async {
    if (!_isServiceRunning) return;

    await FlutterForegroundTask.updateService(
      notificationTitle: persona == PersonaType.adam ? 'Listening for "Hey Adam"' : 'Listening for "Hey Eve"',
      notificationText: 'Wake word detection is active',
    );
  }
}
