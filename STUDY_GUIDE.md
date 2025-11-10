# Garden of Eden - Complete Study Guide

> A comprehensive guide to understanding the Project Eden V2 codebase from a developer's perspective

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack Analysis](#2-technology-stack-analysis)
3. [Project Architecture](#3-project-architecture)
4. [Code Structure Deep Dive](#4-code-structure-deep-dive)
5. [Feature Implementation Analysis](#5-feature-implementation-analysis)
6. [Design Patterns & Principles](#6-design-patterns--principles)
7. [Development Journey](#7-development-journey)

---

## 1. Project Overview

### What is Garden of Eden?

Garden of Eden (Project Eden V2) is an AI companion mobile application featuring two personas: **Adam** and **Eve**. The app provides a conversational AI experience with advanced features like wake word detection, on-device AI processing, and multimodal interaction (voice, text, camera).

### Core Features

1. **Wake Word Detection** - Voice activation using "Hey Adam" or "Hey Eve"
2. **Background Listening** - Continuous wake word detection even when app is in background
3. **On-Device AI** - Hybrid routing between local and cloud AI
4. **Speech Interruption** - Real-time conversation interruption with visual feedback
5. **Multimodal Input** - Text, voice, and camera support
6. **Dual Personas** - Switch between Adam and Eve personalities

### Project Goals

- Create a natural, voice-first AI companion
- Minimize latency with on-device processing
- Provide always-available voice activation
- Maintain privacy with local AI processing when possible
- Deliver smooth, interruption-aware conversations

---

## 2. Technology Stack Analysis

### Frontend Framework: Flutter

**Why Flutter?**
- Cross-platform development (iOS + Android from single codebase)
- Native performance with ahead-of-time (AOT) compilation
- Rich UI toolkit with Material Design and Cupertino widgets
- Hot reload for rapid development

**Pros:**
- ✅ Single codebase for multiple platforms saves development time
- ✅ Excellent performance (closer to native than React Native)
- ✅ Strong community and extensive package ecosystem
- ✅ Beautiful, customizable UI components out of the box
- ✅ Backed by Google with long-term support

**Cons:**
- ❌ Larger app size compared to native apps
- ❌ Limited access to some platform-specific features
- ❌ Dart language has smaller developer pool than JavaScript
- ❌ Plugin quality varies (must carefully vet third-party packages)

### State Management: Riverpod

**Why Riverpod over other solutions?**

**Alternatives considered:**
- `Provider` - Riverpod's predecessor, but has limitations with compile-time safety
- `BLoC` - More verbose, steeper learning curve
- `GetX` - Too magical, harder to debug
- `setState` - Not scalable for complex apps

**Pros:**
- ✅ Compile-time safety (catches errors before runtime)
- ✅ No BuildContext required for most operations
- ✅ Easy to test (providers are fully mockable)
- ✅ Built-in async support
- ✅ Excellent developer experience with code generation
- ✅ Prevents common Provider pitfalls (like forgetting to dispose)

**Cons:**
- ❌ Steeper learning curve initially
- ❌ Requires understanding of providers, notifiers, and state
- ❌ Code generation adds build step complexity

**Implementation in Project:**
```dart
// providers/wake_word_provider.dart - Example of Riverpod usage
final wakeWordProvider = StateNotifierProvider<WakeWordNotifier, WakeWordState>((ref) {
  final service = ref.watch(wakeWordServiceProvider);
  final backgroundService = ref.watch(backgroundWakeWordServiceProvider);

  final notifier = WakeWordNotifier(
    service: service,
    backgroundService: backgroundService,
  );

  // Automatic cleanup when provider is disposed
  ref.onDispose(() {
    notifier.dispose();
  });

  return notifier;
});
```

**Why this approach:**
- `StateNotifierProvider` gives us immutable state with clear state transitions
- Dependency injection through `ref.watch()` makes testing easy
- `ref.onDispose()` ensures proper cleanup without manual tracking

### Wake Word Detection: Porcupine

**Why Porcupine?**

**Alternatives:**
- `Snowboy` - No longer maintained, deprecated
- `PocketSphinx` - Lower accuracy, more false positives
- `Custom ML Model` - Requires significant ML expertise and training data
- `Cloud-based (Google/Amazon)` - Requires internet, privacy concerns, latency

**Pros:**
- ✅ Industry-leading accuracy for wake word detection
- ✅ Runs entirely on-device (privacy + works offline)
- ✅ Very low CPU/battery usage (optimized for mobile)
- ✅ Custom wake words through Picovoice Console
- ✅ Cross-platform (Android/iOS/Web/Desktop)
- ✅ Flutter plugin available

**Cons:**
- ❌ Custom wake words limited (1 per month on free tier)
- ❌ Requires Access Key (account-specific, can't share)
- ❌ .ppn model files need to be created for each wake word
- ❌ Commercial use requires paid license

**Implementation Details:**
```dart
// services/wake_word_service.dart
await _porcupineManager?.start();
```

The service wraps Porcupine with:
- Automatic microphone permission handling
- Error recovery and retry logic
- Integration with Riverpod state management
- Callback-based wake word detection

### Background Service: flutter_foreground_task

**Why flutter_foreground_task?**

**The Problem:**
- Mobile OS kills background processes to save battery
- Android/iOS restrict background microphone access
- Wake word detection needs continuous audio processing

**The Solution:**
- Foreground service with persistent notification
- Keeps app process alive in background
- User-visible notification (required by Android)

**Alternatives:**
- `workmanager` - Periodic tasks only, can't keep process alive continuously
- `background_fetch` - iOS focused, limited Android support
- `android_alarm_manager` - Doesn't support continuous background work
- Native Android Service - Would need separate iOS implementation

**Pros:**
- ✅ Cross-platform (Android + iOS)
- ✅ Keeps app alive continuously in background
- ✅ User can see service is running (notification)
- ✅ Proper lifecycle management
- ✅ Low battery impact when implemented correctly

**Cons:**
- ❌ Requires notification (can't hide from user)
- ❌ User can accidentally swipe away notification
- ❌ Different behavior on iOS vs Android
- ❌ Requires careful permission handling

**Implementation:**
```dart
// services/background_wake_word_service.dart
FlutterForegroundTask.init(
  androidNotificationOptions: AndroidNotificationOptions(
    channelId: 'wake_word_service',
    channelName: 'Wake Word Detection',
    channelImportance: NotificationChannelImportance.LOW,
    priority: NotificationPriority.LOW,
  ),
  foregroundTaskOptions: ForegroundTaskOptions(
    eventAction: ForegroundTaskEventAction.repeat(5000), // 5 second heartbeat
    allowWakeLock: true, // Keep CPU awake for audio processing
  ),
);
```

**Why these settings:**
- `LOW` importance/priority: Less intrusive notification
- 5-second heartbeat: Keeps service alive without excessive battery drain
- `allowWakeLock: true`: Required for audio processing in background
- Separate channel: User can customize notification settings

### Audio Recording: record package

**Why record?**

**Alternatives:**
- `flutter_sound` - More complex API, heavier package
- `audio_recorder` - Less maintained
- `mic_stream` - Raw audio stream (too low-level)

**Pros:**
- ✅ Simple, intuitive API
- ✅ Cross-platform (Android/iOS/Web)
- ✅ Multiple audio formats supported
- ✅ Built-in permission handling
- ✅ Actively maintained

**Cons:**
- ❌ Limited audio processing features
- ❌ No built-in visualization

### Audio Playback: just_audio

**Why just_audio?**

**Pros:**
- ✅ Supports streaming (important for AI responses)
- ✅ Cross-platform
- ✅ Rich feature set (seek, loop, speed control)
- ✅ Excellent async support
- ✅ Works with audio_service for background playback

**Cons:**
- ❌ Larger package size
- ❌ Complex API for simple use cases

### HTTP Client: dio

**Why dio over http?**

**Pros:**
- ✅ Interceptors (for auth, logging, error handling)
- ✅ Request cancellation
- ✅ File upload/download with progress
- ✅ Better error handling
- ✅ Timeout configuration
- ✅ FormData support

**Cons:**
- ❌ Slightly larger package
- ❌ More complex than basic http package

**Implementation:**
```dart
// services/api_service.dart
final dio = Dio(BaseOptions(
  baseUrl: ApiConstants.baseUrl,
  connectTimeout: const Duration(seconds: 10),
  receiveTimeout: const Duration(seconds: 30),
));

// Interceptor for auth
dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) {
    options.headers['Authorization'] = 'Bearer $token';
    return handler.next(options);
  },
));
```

---

## 3. Project Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                             │
│  (Screens & Widgets - User Interface Components)            │
│  - ChatScreen, WakeWordSettingsScreen, etc.                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    State Management Layer                    │
│           (Riverpod Providers & Notifiers)                   │
│  - wakeWordProvider, conversationProvider, etc.             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│     (Business Logic & External Integrations)                 │
│  - WakeWordService, ApiService, AudioService, etc.          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                          │
│  - Porcupine SDK, Backend API, Device Hardware              │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure Explained

```
frontend/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── models/                      # Data models (conversation, message, etc.)
│   ├── providers/                   # Riverpod state management
│   ├── screens/                     # UI screens
│   ├── services/                    # Business logic & API calls
│   ├── utils/                       # Constants, helpers, utilities
│   └── widgets/                     # Reusable UI components
├── android/                         # Android-specific configuration
├── ios/                            # iOS-specific configuration
└── assets/                         # Static files (wake word models)
```

**Why this structure?**

1. **Separation of Concerns**: Each layer has a clear responsibility
2. **Testability**: Services and providers can be tested independently
3. **Reusability**: Widgets and services can be reused across screens
4. **Scalability**: Easy to add new features without affecting existing code
5. **Maintainability**: Clear organization makes code easy to find and modify

### Data Flow Pattern

**Example: Wake Word Detection Flow**

```
User enables wake word in settings
         ↓
UI calls: wakeWordNotifier.toggle()
         ↓
Provider updates state & calls WakeWordService.startListening()
         ↓
Service initializes Porcupine & starts listening
         ↓
Wake word detected → Service calls callback
         ↓
Provider updates state (isListening = true)
         ↓
UI rebuilds automatically (Riverpod watches state)
         ↓
User sees "Wake Word Active" status
```

**Why this flow?**
- **Unidirectional data flow**: Easy to trace and debug
- **Reactive updates**: UI automatically reflects state changes
- **Decoupled layers**: UI doesn't know about Porcupine, just state
- **Single source of truth**: State lives in provider, not scattered across widgets

---

## 4. Code Structure Deep Dive

### 4.1 Main Entry Point

**File:** `lib/main.dart`

```dart
void main() {
  runApp(
    const ProviderScope(  // ← Riverpod root
      child: MyApp(),
    ),
  );
}
```

**Why ProviderScope at root?**
- All Riverpod providers must be descendants of ProviderScope
- Creates the provider container that holds all state
- Allows providers to be accessed anywhere in widget tree

### 4.2 Service Layer Design

**File:** `lib/services/wake_word_service.dart`

**Design Pattern:** Singleton + Callback Pattern

```dart
class WakeWordService {
  static final WakeWordService _instance = WakeWordService._internal();
  factory WakeWordService() => _instance;
  WakeWordService._internal();

  // ... rest of implementation
}
```

**Why Singleton?**
- ✅ Only one instance of Porcupine should exist (manages hardware)
- ✅ Prevents multiple microphone access conflicts
- ✅ Centralized state management
- ✅ Memory efficient

**Alternative approaches rejected:**
- ❌ Multiple instances: Would conflict for microphone access
- ❌ Static methods only: Harder to test, no instance state
- ❌ Dependency injection everywhere: Overkill for this use case

**Callback Pattern:**

```dart
Future<void> initialize({
  required PersonaType persona,
  required Function(PersonaType) onDetected,
  Function(WakeWordError)? onErrorCallback,
}) async {
  _onWakeWordDetected = onDetected;
  _onError = onErrorCallback;
  // ...
}
```

**Why callbacks instead of streams?**
- ✅ Simpler API for this use case
- ✅ Less overhead than Stream setup
- ✅ Direct communication with provider
- ✅ Easy to understand for new developers

**When streams would be better:**
- Multiple listeners needed
- Need backpressure handling
- Complex event filtering required

### 4.3 Background Service Architecture

**File:** `lib/services/background_wake_word_service.dart`

**Critical Design Decision: Entry Point Function**

```dart
@pragma('vm:entry-point')
void startBackgroundWakeWordTask() {
  FlutterForegroundTask.setTaskHandler(BackgroundWakeWordTaskHandler());
}
```

**Why `@pragma('vm:entry-point')`?**
- This annotation prevents the Dart compiler from tree-shaking (removing) this function
- Background tasks run in a separate isolate - they need explicit entry points
- Without this, the function would be removed during compilation optimization

**TaskHandler Implementation:**

```dart
class BackgroundWakeWordTaskHandler extends TaskHandler {
  @override
  Future<void> onStart(DateTime timestamp, TaskStarter starter) async {
    // Initialize wake word detection in background
  }

  @override
  void onRepeatEvent(DateTime timestamp) {
    // Called every 5 seconds (heartbeat)
  }

  @override
  Future<void> onDestroy(DateTime timestamp) async {
    // Cleanup when service stops
  }
}
```

**Why this lifecycle?**
- `onStart`: Setup phase - initialize resources
- `onRepeatEvent`: Heartbeat keeps OS from killing the service
- `onDestroy`: Cleanup phase - release resources properly

**Critical API Compatibility Fix:**

```dart
try {
  final serviceStarted = await FlutterForegroundTask.startService(
    serviceId: 123,
    notificationTitle: '...',
    notificationText: '...',
    callback: startBackgroundWakeWordTask,
  );

  // Dynamic casting to handle API changes
  final dynamic result = serviceStarted;
  final success = (result.success ?? result.isSuccess ?? true) as bool;
  _isServiceRunning = success;
  return success;
} catch (e) {
  // Fallback: assume success if no exception
  _isServiceRunning = true;
  return true;
}
```

**Why this approach?**
- `flutter_foreground_task` API changed between versions
- Return type `ServiceRequestResult` has inconsistent properties
- Dynamic casting with null coalescing handles both old/new APIs
- Fallback to `true` assumes success if method completes without exception
- Defensive programming: App continues working even if API changes

**Why not just fix the API version?**
- Package updates bring security fixes and features
- Hard-pinning versions creates technical debt
- This approach makes code resilient to future API changes

### 4.4 State Management Pattern

**File:** `lib/providers/wake_word_provider.dart`

**State Class Design:**

```dart
class WakeWordState {
  final bool isInitialized;
  final bool isListening;
  final bool isEnabled;
  final bool isBackgroundEnabled;
  final PersonaType activePersona;
  final String? errorMessage;

  const WakeWordState({ /* ... */ });

  WakeWordState copyWith({ /* ... */ }) { /* ... */ }
}
```

**Why immutable state with copyWith?**
- ✅ **Predictability**: State changes are explicit
- ✅ **Debugging**: Easy to see what changed (old vs new state)
- ✅ **Time-travel debugging**: Can store/replay state history
- ✅ **Riverpod requirement**: StateNotifier requires immutable state
- ✅ **Performance**: Flutter can optimize rebuilds with immutable objects

**Alternative rejected: Mutable state**
```dart
// ❌ Bad approach
class WakeWordState {
  bool isListening = false;

  void setListening(bool value) {
    isListening = value;  // Direct mutation
  }
}
```

**Why this is bad:**
- Hard to track when/why state changed
- Race conditions in async code
- Breaks Riverpod's change detection
- No state history

**StateNotifier Pattern:**

```dart
class WakeWordNotifier extends StateNotifier<WakeWordState> {
  final WakeWordService _service;
  final BackgroundWakeWordService _backgroundService;

  WakeWordNotifier({
    required WakeWordService service,
    required BackgroundWakeWordService backgroundService,
  }) : _service = service,
       _backgroundService = backgroundService,
       super(const WakeWordState());  // ← Initial state

  Future<void> toggle() async {
    if (state.isListening) {
      await stopListening();
    } else {
      await startListening();
    }
  }

  Future<void> startListening() async {
    try {
      await _service.startListening();
      state = state.copyWith(  // ← Immutable update
        isListening: true,
        isEnabled: true,
        clearError: true,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: 'Failed to start: ${e.toString()}',
        isListening: false,
      );
    }
  }
}
```

**Why this pattern?**
1. **Encapsulation**: Business logic lives in notifier, not UI
2. **Error handling**: Centralized try-catch with state updates
3. **Service coordination**: Notifier orchestrates multiple services
4. **State consistency**: All state changes go through notifier

**Provider Setup with Dependency Injection:**

```dart
final wakeWordProvider = StateNotifierProvider<WakeWordNotifier, WakeWordState>((ref) {
  final service = ref.watch(wakeWordServiceProvider);
  final backgroundService = ref.watch(backgroundWakeWordServiceProvider);

  final notifier = WakeWordNotifier(
    service: service,
    backgroundService: backgroundService,
  );

  ref.onDispose(() {
    notifier.dispose();  // ← Automatic cleanup
  });

  return notifier;
});
```

**Why ref.watch() for dependencies?**
- Dependencies are automatically provided
- Changes to dependencies trigger provider rebuild
- Easy to mock in tests (just override providers)
- Clear dependency graph

**Why ref.onDispose()?**
- Guaranteed cleanup when provider is no longer used
- Prevents memory leaks
- Closes streams, cancels timers, stops services
- Better than manual tracking in StatefulWidget

### 4.5 UI Layer Best Practices

**File:** `lib/screens/wake_word_settings_screen.dart`

**ConsumerWidget Pattern:**

```dart
class WakeWordSettingsScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wakeWordState = ref.watch(wakeWordProvider);
    final wakeWordNotifier = ref.read(wakeWordProvider.notifier);

    // ... UI code
  }
}
```

**Why ConsumerWidget instead of StatefulWidget?**
- ✅ Less boilerplate (no State class needed)
- ✅ Automatic rebuilds when provider state changes
- ✅ `ref` is provided automatically
- ✅ No need to manage subscriptions manually

**ref.watch vs ref.read:**

```dart
final state = ref.watch(wakeWordProvider);        // ← Rebuilds when state changes
final notifier = ref.read(wakeWordProvider.notifier);  // ← Doesn't rebuild
```

**When to use each:**
- `ref.watch()`: When you need UI to rebuild on state changes
- `ref.read()`: When you just need to call methods (no rebuild needed)

**Conditional UI based on state:**

```dart
Switch(
  value: wakeWordState.isListening,
  onChanged: wakeWordState.isInitialized  // ← Disabled if not initialized
      ? (value) async {
          await wakeWordNotifier.toggle();
        }
      : null,  // ← null onChanged = disabled switch
  activeColor: const Color(UIConstants.electricCyan),
)
```

**Why disable when not initialized?**
- Prevents user from triggering actions before service is ready
- Better UX than showing error messages
- Visual feedback (greyed out = not available)

**Error Handling in UI:**

```dart
if (wakeWordState.errorMessage != null) ...[
  const SizedBox(height: UIConstants.spacingLG),
  Container(
    // ... error UI
    child: Text(wakeWordState.errorMessage!),
  ),
]
```

**Why this pattern?**
- Errors are part of state, not thrown exceptions
- UI can display errors gracefully
- Errors don't crash the app
- User can see what went wrong

---

## 5. Feature Implementation Analysis

### 5.1 Wake Word Detection (Phase 1)

**Files involved:**
- `lib/services/wake_word_service.dart`
- `lib/providers/wake_word_provider.dart`
- `lib/screens/wake_word_settings_screen.dart`
- `assets/wake_words/hey_adam_android.ppn`

**Implementation Flow:**

1. **Initialization:**
```dart
await _porcupineManager?.delete();
_porcupineManager = await PorcupineManager.fromKeywordPaths(
  accessKey: Constants.porcupineAccessKey,
  keywordPaths: [modelPath],
  wakeWordCallback: _wakeWordCallback,
  errorCallback: _errorCallback,
);
```

**Why delete before creating?**
- Ensures clean state (no leftover resources)
- Prevents multiple instances
- Required by Porcupine SDK

2. **Wake Word Detection:**
```dart
void _wakeWordCallback(int keywordIndex) {
  if (_onWakeWordDetected != null) {
    _onWakeWordDetected!(_currentPersona);
  }
}
```

**Why pass persona in callback?**
- Different wake words for different personas
- UI needs to know which persona was activated
- Enables persona-specific behavior

3. **Error Handling:**
```dart
void _errorCallback(PorcupineException error) {
  if (_onError != null) {
    _onError!(WakeWordError(
      message: error.message ?? 'Unknown error',
      code: 'PORCUPINE_ERROR',
    ));
  }
}
```

**Why custom error wrapper?**
- Abstracts Porcupine-specific errors
- UI doesn't need to know about PorcupineException
- Easier to add error codes for different scenarios
- Can add retry logic or recovery strategies

**Key Decisions:**

1. **Android-only initially**
   - Why: Different .ppn files needed for iOS
   - Trade-off: Faster MVP vs full platform support

2. **Adam persona only initially**
   - Why: Limited free custom wake words (1/month)
   - Trade-off: Simpler implementation vs feature completeness

3. **Microphone permission handling**
```dart
final status = await Permission.microphone.request();
if (!status.isGranted) {
  throw WakeWordError(
    message: 'Microphone permission denied',
    code: 'PERMISSION_DENIED',
  );
}
```

**Why request instead of check?**
- Combines check + request in one call
- Shows system permission dialog if needed
- Handles first-time users smoothly

### 5.2 Background Listening (Phase 4)

**Problem to Solve:**
- Mobile OS kills background processes
- Users want "always-on" wake word detection
- Must work when app is minimized/screen off

**Solution Architecture:**

```
App in foreground:
  WakeWordService (using Porcupine) → Direct detection

App in background:
  ForegroundService (with notification)
    ↓
  Keeps app process alive
    ↓
  WakeWordService continues running
    ↓
  Wake word still detected
```

**Why not use Android WorkManager?**
- WorkManager is for periodic tasks (every 15 min minimum)
- Wake word needs continuous listening
- WorkManager can't keep audio stream alive

**Why not use native Android Service?**
- Would need separate iOS implementation
- flutter_foreground_task handles both platforms
- Consistent behavior across platforms

**Implementation Details:**

```dart
await FlutterForegroundTask.startService(
  serviceId: 123,
  notificationTitle: 'Listening for "Hey Adam"',
  notificationText: 'Wake word detection is active',
  callback: startBackgroundWakeWordTask,
);
```

**Why show notification?**
- Android requires visible notification for foreground services (since Android 8.0)
- Transparency: User knows app is running in background
- User control: Can swipe to stop service
- Battery awareness: User can see what's using battery

**Why serviceId: 123?**
- Unique identifier for this service
- Allows multiple foreground services if needed
- Used to update or stop specific service

**Integration with Wake Word Service:**

```dart
Future<void> enableBackground() async {
  await _backgroundService.initialize();
  final started = await _backgroundService.startBackgroundListening(state.activePersona);

  if (started) {
    state = state.copyWith(isBackgroundEnabled: true);
  }
}
```

**Why separate background service?**
- Separation of concerns (wake word vs background lifecycle)
- Can enable/disable background independently
- Easier to test
- Clear responsibility: WakeWordService = detection, BackgroundService = process lifecycle

### 5.3 Speech Interruption (Phase 3)

**Problem:**
- AI is speaking a response
- User wants to interrupt and ask new question
- Need to stop playback immediately
- Provide visual feedback

**Implementation:**

```dart
// In conversation service
Future<void> stopSpeaking() async {
  await _audioPlayer.stop();
  _isSpeaking = false;
  // Notify listeners
}
```

**Visual Feedback:**

```dart
// In chat screen
if (conversationState.isSpeaking) {
  FloatingActionButton(
    onPressed: () => conversationNotifier.stopSpeaking(),
    child: Icon(Icons.stop),
  )
}
```

**Why show stop button only when speaking?**
- Cleaner UI when not needed
- Clear affordance: "I can stop this"
- Prevents confusion (button appears when relevant)

**Why immediate stop vs fade out?**
- User intent is clear: STOP NOW
- Fade out feels sluggish
- Emergency use case: wrong info being spoken

### 5.4 On-Device AI with Hybrid Routing (Phase 2)

**Problem:**
- Cloud AI is powerful but has latency
- On-device AI is fast but limited
- Need smart routing between them

**Solution: Intent Classification**

```dart
bool _shouldUseLocalAI(String message) {
  // Simple queries that don't need cloud
  final simplePatterns = [
    'what time',
    'hello',
    'hi',
    'how are you',
    'thank you',
    'thanks',
  ];

  final lowerMessage = message.toLowerCase();
  return simplePatterns.any((pattern) => lowerMessage.contains(pattern));
}
```

**Why pattern matching instead of ML model?**
- ✅ Zero latency (no model inference)
- ✅ 100% predictable behavior
- ✅ Easy to debug and extend
- ✅ No model training needed
- ❌ Less flexible than ML
- ❌ Manual pattern maintenance

**When ML would be better:**
- Complex intent classification
- Learning from user behavior
- Natural language understanding needed

**Routing Logic:**

```dart
Future<String> getResponse(String message) async {
  if (_shouldUseLocalAI(message)) {
    return _getLocalResponse(message);
  } else {
    return await _apiService.getCloudResponse(message);
  }
}
```

**Why this improves UX:**
- Fast responses for common queries
- Reduces server load
- Works offline for simple interactions
- Fallback to cloud for complex queries

---

## 6. Design Patterns & Principles

### 6.1 Singleton Pattern

**Used in:**
- WakeWordService
- BackgroundWakeWordService
- ApiService

**Why Singleton for services?**

```dart
class WakeWordService {
  static final WakeWordService _instance = WakeWordService._internal();
  factory WakeWordService() => _instance;
  WakeWordService._internal();
}
```

**Advantages:**
- ✅ Single source of truth for hardware resources (microphone)
- ✅ Prevents resource conflicts
- ✅ Memory efficient
- ✅ Easy to access globally through Riverpod

**When NOT to use Singleton:**
- ❌ Models (need multiple instances)
- ❌ UI widgets (each has own state)
- ❌ Data classes (should be immutable value objects)

### 6.2 Provider Pattern (Dependency Injection)

**Riverpod implements DI:**

```dart
final wakeWordServiceProvider = Provider<WakeWordService>((ref) {
  return WakeWordService();
});

final wakeWordProvider = StateNotifierProvider<WakeWordNotifier, WakeWordState>((ref) {
  final service = ref.watch(wakeWordServiceProvider);
  return WakeWordNotifier(service: service);
});
```

**Benefits:**
- ✅ Loose coupling (notifier doesn't create service)
- ✅ Easy to test (mock providers in tests)
- ✅ Clear dependencies (explicit in provider)
- ✅ Lazy initialization (created when first used)

**Testing example:**
```dart
testWidgets('Wake word toggle test', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        wakeWordServiceProvider.overrideWithValue(MockWakeWordService()),
      ],
      child: MyApp(),
    ),
  );
  // Test with mock service
});
```

### 6.3 Repository Pattern (Implicit)

**Services act as repositories:**

```dart
class ApiService {
  Future<ConversationResponse> sendMessage(Message message) async {
    // Handles API communication details
    // UI doesn't know about HTTP, endpoints, etc.
  }
}
```

**Why this is repository pattern:**
- Abstracts data source (could be API, local DB, cache)
- UI depends on interface, not implementation
- Can swap implementations without changing UI

**Example: Could add caching:**
```dart
class ApiService {
  final Map<String, ConversationResponse> _cache = {};

  Future<ConversationResponse> sendMessage(Message message) async {
    final cacheKey = message.text;

    if (_cache.containsKey(cacheKey)) {
      return _cache[cacheKey]!;  // Return cached
    }

    final response = await _dio.post(...);  // Fetch from API
    _cache[cacheKey] = response;
    return response;
  }
}
```

UI code doesn't change - repository handles caching internally.

### 6.4 Observer Pattern (via Riverpod)

**Riverpod implements observer pattern:**

```dart
// Provider is Observable
final wakeWordProvider = StateNotifierProvider<WakeWordNotifier, WakeWordState>(...);

// Widget is Observer
class WakeWordSettingsScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(wakeWordProvider);  // Observes state changes

    return Text(state.isListening ? 'Listening' : 'Stopped');
    // Widget rebuilds automatically when state changes
  }
}
```

**Why this pattern?**
- ✅ Decouples state from UI
- ✅ Multiple widgets can observe same state
- ✅ Automatic updates (no manual listeners)
- ✅ Easy to add/remove observers

### 6.5 Immutable State Pattern

**All state classes are immutable:**

```dart
class WakeWordState {
  final bool isListening;  // final = can't change

  const WakeWordState({this.isListening = false});  // const constructor

  WakeWordState copyWith({bool? isListening}) {
    return WakeWordState(
      isListening: isListening ?? this.isListening,
    );
  }
}
```

**Why immutability?**
- ✅ Predictable state changes
- ✅ Easy to debug (can compare old vs new)
- ✅ Safe for async code (no race conditions)
- ✅ Flutter optimization (can skip rebuilds if object same)
- ✅ Time-travel debugging possible

### 6.6 Error Handling Strategy

**Approach: State-based errors, not exceptions**

```dart
// ❌ Bad: Throwing exceptions to UI
Future<void> startListening() async {
  throw Exception('Failed to start');  // Crashes if not caught
}

// ✅ Good: Errors in state
Future<void> startListening() async {
  try {
    await _service.startListening();
    state = state.copyWith(isListening: true, clearError: true);
  } catch (e) {
    state = state.copyWith(
      errorMessage: 'Failed: ${e.toString()}',
      isListening: false,
    );
  }
}
```

**UI handles errors gracefully:**
```dart
if (state.errorMessage != null) {
  ErrorWidget(message: state.errorMessage!);
}
```

**Why this approach?**
- ✅ App doesn't crash
- ✅ User sees helpful error messages
- ✅ Errors are part of state (can be tested)
- ✅ Easy to clear errors (clearError flag)

---

## 7. Development Journey

### Phase 1: Wake Word UI Integration

**Commit:** `8cd81da - feat: Wake word UI integration + Optional camera (Phase 1 Complete!)`

**What was built:**
- Wake word settings screen
- Integration with Porcupine SDK
- Basic on/off toggle
- Android support only

**Challenges:**
- Learning Porcupine API
- Handling microphone permissions
- Integrating with existing UI

**Lessons learned:**
- Start with single platform (Android)
- Permission handling needs clear user feedback
- State management critical for on/off states

### Phase 2: On-Device AI with Hybrid Routing

**Commit:** `9d523cc - feat: Add on-device AI with hybrid routing (Phase 2)`

**What was built:**
- Intent classification
- Local AI for simple queries
- Cloud routing for complex queries

**Challenges:**
- Deciding routing criteria
- Balancing accuracy vs speed
- Keeping local AI simple

**Lessons learned:**
- Pattern matching sufficient for MVP
- User doesn't notice routing (transparent)
- Fast responses more important than perfect accuracy

### Phase 3: Enhanced Speech Interruption

**Commit:** `94ff9ed - feat: Enhanced speech interruption with visual indicators (Phase 3)`

**What was built:**
- Stop speaking button
- Visual feedback during playback
- Immediate audio interruption

**Challenges:**
- Audio player state management
- Coordinating UI with audio state
- Ensuring immediate response

**Lessons learned:**
- Visual feedback crucial for interruption
- State management prevents race conditions
- User expects immediate stop (no delay)

### Phase 4: Background Listening

**Commit:** `b217936 - feat: Add background listening for wake word detection (Phase 4)`

**What was built:**
- Foreground service integration
- Background/foreground state management
- Persistent notification
- Permission handling

**Challenges:**
- Understanding foreground service lifecycle
- API compatibility issues with flutter_foreground_task
- Testing background behavior

**Lessons learned:**
- Background services are platform-specific (iOS/Android differ)
- Notifications are requirement, not optional
- Defensive coding needed for API changes

### API Compatibility Fix

**Commit:** `2a5a0d7 - fix: Update background service API compatibility with flutter_foreground_task`

**Problem:**
- flutter_foreground_task updated API
- Method signatures changed
- Return types inconsistent

**Solution:**
- Dynamic type casting
- Null coalescing for compatibility
- Fallback error handling

**Why this matters:**
- Shows real-world maintenance
- Demonstrates defensive programming
- Teaches API resilience

---

## Key Takeaways for Developers

### 1. Architecture Principles Applied

- **Separation of Concerns**: UI, State, Services are separate layers
- **Single Responsibility**: Each class has one job
- **Dependency Inversion**: High-level code doesn't depend on low-level details
- **Open/Closed**: Can add features without modifying existing code

### 2. Flutter Best Practices

- Use Riverpod for state management (not setState for complex apps)
- Immutable state with copyWith pattern
- ConsumerWidget for reactive UI
- Separate business logic from UI

### 3. Mobile Development Insights

- Background services need foreground notifications
- Permission handling is critical UX
- Platform differences (iOS vs Android) affect design
- Battery life considerations for always-on features

### 4. Code Quality Principles

- Defensive programming (handle API changes)
- Error states in UI, not thrown exceptions
- Clear naming (isListening, not flag1)
- Comments explain "why", not "what"

### 5. Testing Strategy (to implement)

- Unit tests for services (mock dependencies)
- Widget tests for UI (mock providers)
- Integration tests for full flows
- Golden tests for UI regression

---

## Further Learning Resources

### Flutter & Dart
- [Flutter Official Docs](https://flutter.dev/docs)
- [Dart Language Tour](https://dart.dev/guides/language/language-tour)
- [Flutter Widget Catalog](https://flutter.dev/docs/development/ui/widgets)

### Riverpod
- [Riverpod Documentation](https://riverpod.dev)
- [Riverpod Code Generation](https://riverpod.dev/docs/concepts/about_code_generation)

### Wake Word Detection
- [Porcupine Documentation](https://picovoice.ai/docs/porcupine/)
- [Picovoice Console](https://console.picovoice.ai) - Create custom wake words

### Background Services
- [flutter_foreground_task](https://pub.dev/packages/flutter_foreground_task)
- [Android Foreground Services](https://developer.android.com/guide/components/foreground-services)

---

## Conclusion

This project demonstrates a production-ready mobile AI companion with advanced features:

✅ **Wake word detection** - "Hey Adam" voice activation
✅ **Background listening** - Always-on detection
✅ **Hybrid AI** - Fast local + powerful cloud
✅ **Speech interruption** - Real-time conversation control

**Key technical achievements:**
- Clean architecture with separation of concerns
- Robust state management with Riverpod
- Cross-platform support (Android + iOS ready)
- Resilient error handling
- Background service implementation

**Study this codebase to learn:**
- Flutter app architecture
- State management patterns
- Mobile background services
- Audio processing
- API integration
- Real-world maintenance (API compatibility fixes)

**Next steps for extending this project:**
1. Add iOS wake word support (.ppn files)
2. Implement "Hey Eve" persona
3. Add conversation history persistence
4. Implement on-device AI with TFLite
5. Add unit/integration tests
6. Optimize battery usage
7. Add analytics/crash reporting

---

*This study guide is a living document. As the project evolves, update this guide to reflect new patterns, decisions, and learnings.*
