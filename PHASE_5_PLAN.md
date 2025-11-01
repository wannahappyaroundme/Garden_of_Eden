# 📋 Phase 5: UI/UX Polish Plan

**Status**: Ready to start
**Date**: 2025-11-02
**Goal**: Polish the UI/UX and add missing features

---

## 🎯 Phase 5 Objectives

Based on Phase 2 completion report, we need to add:

1. **Pitfall Warning UI Indicator** - Currently detection works but no visual indicator
2. **Profile Viewing Screen** - Show user profile, traits, and progress
3. **Settings Screen** - App configuration and preferences
4. **Retry Logic** - Handle failed network requests
5. **Better Loading States** - Improve user feedback
6. **Animation Polish** - Smooth transitions and better timing

---

## 📝 Detailed Tasks

### Task 1: Pitfall Warning UI Indicator

**Current State**: Backend detects pitfalls, sends `pitfall_warning_triggered: true`, but app doesn't show visual indicator

**To Implement**:
- Add warning banner when pitfall detected
- Amber/yellow color scheme (per design system)
- Animated slide-in from top
- Shows pitfall message prominently
- Auto-dismiss after 5 seconds
- Haptic feedback (vibration)

**Files to Create/Modify**:
- `lib/widgets/pitfall_warning_banner.dart` (new)
- `lib/screens/voice_first_screen.dart` (modify)
- `lib/providers/app_state_provider.dart` (add pitfall state)

**UI Design**:
```
┌─────────────────────────────────┐
│ ⚠️ 주의: 능력 함정 감지!          │
│ [Pitfall warning message here]  │
└─────────────────────────────────┘
```

---

### Task 2: Profile Viewing Screen

**Purpose**: Let users see their learned profile

**Features**:
- Show "One Thing" and "Core Pitfall"
- Display top personality traits with weights
- Show total conversations count
- Profile maturity indicator
- Recent emotional state
- Last updated timestamp

**Files to Create**:
- `lib/screens/profile_screen.dart`
- `lib/widgets/trait_card.dart`
- `lib/widgets/profile_header.dart`

**UI Design**:
```
Profile Screen
━━━━━━━━━━━━━━━━━━━━━━━━━
[Profile Icon]

One Thing:
  SNU HCI Lab 합격하기

Core Pitfall:
  능력 함정 - 여러 기술 분산 학습

━━━━━━━━━━━━━━━━━━━━━━━━━
Personality Traits:

[■■■■■■■■■□] perfectionist (0.87)
[■■■■■■■■■■] night_owl (0.93)
[■■■■■■■□□□] visual_learner (0.76)

━━━━━━━━━━━━━━━━━━━━━━━━━
Stats:
- Conversations: 15
- Profile Version: 5
- Maturity: Developing
- Last Updated: 2 hours ago
```

---

### Task 3: Settings Screen

**Features**:
- Switch persona preference (Adam/Eve default)
- Adjust TTS volume
- Toggle camera capture
- Clear conversation history
- About/Version info
- Privacy settings

**Files to Create**:
- `lib/screens/settings_screen.dart`
- `lib/widgets/setting_tile.dart`

**UI Design**:
```
Settings
━━━━━━━━━━━━━━━━━━━━━━━━━

Persona
  Default Persona: [Adam ▼]

Audio
  TTS Volume: [━━━━━○━━━━] 70%
  Auto-play TTS: [✓]

Camera
  Enable Camera: [✓]
  Frame Rate: 1 FPS

Privacy
  Clear History: [Tap]

About
  Version: 2.0.0
  Backend: Connected
```

---

### Task 4: Retry Logic for Failed Requests

**Current Issue**: If network fails, user must restart

**To Implement**:
- Automatic retry (up to 3 times)
- Exponential backoff (1s, 2s, 4s)
- Manual retry button
- Show retry attempt count
- Offline mode detection

**Files to Modify**:
- `lib/services/api_service.dart`
- `lib/screens/voice_first_screen.dart`
- `lib/providers/app_state_provider.dart`

**UI Design**:
```
┌─────────────────────────────────┐
│ 🔄 연결 실패 (시도 1/3)          │
│ [Retry] [Cancel]                │
└─────────────────────────────────┘
```

---

### Task 5: Better Loading States

**Current**: Blue spinner during processing, but no detail

**Improvements**:
- Show what's happening
  - "음성 인식 중..." (Transcribing)
  - "AI 응답 생성 중..." (Generating)
  - "음성 합성 중..." (TTS)
- Progress indicator
- Estimated time remaining
- Cancellable operations

**Files to Modify**:
- `lib/widgets/push_to_talk_button.dart`
- `lib/widgets/loading_overlay.dart` (new)

**UI Design**:
```
Processing...

[◐ Spinning]

음성 인식 중...
(Estimated: 2s remaining)

[Cancel]
```

---

### Task 6: Animation Polish

**Current Issues**:
- Some transitions feel abrupt
- Button state changes could be smoother
- Overlay appearance could be more polished

**Improvements**:
- Smooth state transitions
- Better timing curves
- Subtle micro-interactions
- Loading skeleton screens
- Pull-to-refresh gesture

**Files to Modify**:
- `lib/widgets/push_to_talk_button.dart`
- `lib/widgets/response_overlay.dart`
- `lib/screens/voice_first_screen.dart`

---

## 🎨 New Widgets to Create

### 1. PitfallWarningBanner
```dart
class PitfallWarningBanner extends StatelessWidget {
  final String message;
  final VoidCallback onDismiss;

  // Amber background
  // Slide in from top
  // Auto-dismiss after 5s
  // Haptic feedback
}
```

### 2. ProfileScreen
```dart
class ProfileScreen extends ConsumerWidget {
  // Displays user profile
  // Shows traits with progress bars
  // Stats and maturity
}
```

### 3. SettingsScreen
```dart
class SettingsScreen extends StatefulWidget {
  // App settings
  // Persona preference
  // Audio/Camera toggles
  // About info
}
```

### 4. LoadingOverlay
```dart
class LoadingOverlay extends StatelessWidget {
  final String message;
  final int? estimatedSeconds;
  final VoidCallback? onCancel;

  // Shows detailed loading state
  // Progress indicator
  // Cancellable
}
```

### 5. TraitCard
```dart
class TraitCard extends StatelessWidget {
  final String traitName;
  final double weight;

  // Shows trait with progress bar
  // Weight from 0.0 to 1.0
}
```

---

## 🔄 Modified Features

### Enhanced Push-to-Talk Button
- Add loading states with text
- Show processing step
- Better error feedback
- Haptic feedback on state change

### Enhanced Response Overlay
- Show speaker icon when TTS playing
- Add playback controls (pause/resume)
- Better markdown styling
- Code block support

### Enhanced App State
- Add `isRetrying` state
- Add `retryAttempt` counter
- Add `loadingMessage` for detailed feedback
- Add `pitfallWarning` state

---

## 📊 Success Criteria

Phase 5 is **COMPLETE** when:

1. ✅ Pitfall warning banner shows when triggered
2. ✅ Profile screen accessible and displays all info
3. ✅ Settings screen functional
4. ✅ Failed requests retry automatically
5. ✅ Loading states show detailed progress
6. ✅ All animations smooth and polished
7. ✅ No UI glitches or jarring transitions
8. ✅ User testing feedback positive

---

## 🎯 Implementation Order

### Week 1 (Priority 1)
1. **Day 1-2**: Retry logic (critical for reliability)
2. **Day 3-4**: Better loading states (improves UX)
3. **Day 5**: Pitfall warning UI (completes core feature)

### Week 2 (Priority 2)
4. **Day 1-2**: Profile screen (valuable feature)
5. **Day 3-4**: Settings screen (important for customization)
6. **Day 5**: Animation polish (final touch)

---

## 🛠️ Technical Approach

### Retry Logic Implementation
```dart
class ApiService {
  static const int maxRetries = 3;
  static const List<Duration> retryDelays = [
    Duration(seconds: 1),
    Duration(seconds: 2),
    Duration(seconds: 4),
  ];

  Future<T> _retryableRequest<T>(
    Future<T> Function() request,
  ) async {
    for (int attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await request();
      } catch (e) {
        if (attempt == maxRetries - 1) rethrow;
        await Future.delayed(retryDelays[attempt]);
      }
    }
    throw Exception('Max retries exceeded');
  }
}
```

### Pitfall Warning State
```dart
class AppState {
  final AppMode mode;
  final PersonaType persona;
  final ChatResponse? lastResponse;
  final String? errorMessage;
  final bool isTTSPlaying;
  final bool showPitfallWarning;  // NEW
  final String? pitfallMessage;    // NEW
  final int retryAttempt;          // NEW
  final String? loadingMessage;    // NEW
}
```

---

## 🎨 UI/UX Principles

1. **Feedback**: Always show what's happening
2. **Forgiveness**: Allow undo/retry
3. **Clarity**: Clear error messages
4. **Consistency**: Match design system
5. **Delight**: Subtle animations enhance experience

---

## 📱 Screen Flow Updates

### Current Flow
```
Permission → Main Screen → Record → Process → Respond
```

### Enhanced Flow
```
Permission → Main Screen → [Settings/Profile accessible]
  ↓
Record → Process (with detailed state) → Respond
  ↓
Error? → Retry automatically → Success or Manual Retry
  ↓
Pitfall? → Show warning banner → Continue
```

---

## 🧪 Testing Plan

### UI Tests
- [ ] Pitfall warning appears correctly
- [ ] Profile screen loads data
- [ ] Settings persist after app restart
- [ ] Retry works on network failure
- [ ] Loading states accurate
- [ ] Animations smooth (60fps)

### UX Tests
- [ ] First-time user can find profile
- [ ] Settings are discoverable
- [ ] Error recovery is clear
- [ ] Loading doesn't feel slow
- [ ] Pitfall warning is noticeable but not annoying

---

## 📚 Resources Needed

### Design Assets
- Pitfall warning icon (⚠️)
- Profile icon
- Settings icon
- Loading spinner variants

### External Libraries (if needed)
- `flutter_hooks` - For smoother state management
- `shimmer` - Loading skeleton screens
- `lottie` - Advanced animations

---

## 🎯 Quick Start for Phase 5

1. **Create branch**: `git checkout -b phase-5-ui-polish`
2. **Start with retry logic**: Most impactful for testing
3. **Add loading states**: Improves testing experience
4. **Build UI screens**: Profile and Settings
5. **Polish animations**: Final touches
6. **User testing**: Gather feedback

---

**Estimated Time**: 10-15 hours total (1-2 weeks)

**Dependencies**: Phase 4 testing complete

**Next Phase**: Phase 6 - Advanced Features

---

**Ready to make the app beautiful and user-friendly!** 🎨

화이팅! 💪
