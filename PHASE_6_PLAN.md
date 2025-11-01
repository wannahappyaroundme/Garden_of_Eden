# Phase 6: Integration & Polish

**Goal**: Wire up all Phase 5 UI components to the main screen, add navigation, improve user experience with smooth transitions and feedback.

---

## Tasks

### 1. ✅ Integration: Loading Overlay
**Priority**: High
**File**: `frontend/lib/screens/voice_first_screen.dart`

**What to do**:
- Show LoadingOverlay during `AppMode.processing`
- Display retry attempts using callback from API service
- Show loading messages for different stages:
  - "음성을 인식하는 중..." (Recognizing voice...)
  - "AI가 생각하는 중..." (AI is thinking...)
  - "응답을 생성하는 중..." (Generating response...)

**Integration Points**:
- Wrap Stack with LoadingOverlay when `appState.loadingMessage != null`
- Pass `appState.retryAttempt` to LoadingOverlay
- Use `onRetry` callback in `apiService.sendChat()` to update retry count

---

### 2. ✅ Integration: Pitfall Warning Banner
**Priority**: High
**File**: `frontend/lib/screens/voice_first_screen.dart`

**What to do**:
- Show PitfallWarningBanner when `appState.showPitfallWarning == true`
- Parse `ChatResponse.pitfallDetected` from backend
- Display pitfall message from response

**Integration Points**:
- Add PitfallWarningBanner to Stack (above all other widgets)
- Check `response.pitfallDetected` after getting response
- Call `appState.showPitfall(response.pitfallWarning)` if detected
- Auto-dismiss handled by widget itself

---

### 3. ✅ Navigation: Profile & Settings
**Priority**: High
**Files**:
- `frontend/lib/screens/voice_first_screen.dart`
- `frontend/lib/screens/profile_screen.dart`
- `frontend/lib/screens/settings_screen.dart`

**What to do**:
- Add top-right menu button (hamburger or gear icon)
- Create slide-in drawer or modal with navigation options:
  - My Profile
  - Settings
  - About
- Use Material PageRoute with custom transitions

**UI Design**:
```
┌─────────────────────────────────┐
│  [☰]              [👤]  [⚙️]  │  ← Top bar
│                                 │
│         Camera View             │
│                                 │
│      [Persona Toggle]           │
│                                 │
│    [Push-to-Talk Button]        │
└─────────────────────────────────┘
```

---

### 4. ✅ Enhanced Retry Feedback
**Priority**: Medium
**File**: `frontend/lib/screens/voice_first_screen.dart`

**What to do**:
- Wire `onRetry` callback from API service
- Update loading message: "재시도 중... (1/3)"
- Estimate time based on retry delays (1s, 2s, 4s)

**Example**:
```dart
await apiService.sendChat(
  // ... params
  onRetry: (attempt, error) {
    appState.setRetryAttempt(attempt);
    appState.setLoadingMessage('재시도 중... ($attempt/3)');
  },
);
```

---

### 5. ✅ Page Transitions
**Priority**: Low
**Files**: Create `frontend/lib/utils/page_transitions.dart`

**What to do**:
- Create custom PageRoute with slide transitions
- Slide from right for Settings
- Slide from bottom for Profile
- Fade for modals

**Code Structure**:
```dart
class SlidePageRoute extends PageRouteBuilder {
  final Widget page;
  final SlideDirection direction;

  SlidePageRoute({required this.page, required this.direction})
    : super(
        pageBuilder: (context, animation, secondaryAnimation) => page,
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          // Custom slide transition
        },
      );
}
```

---

### 6. ✅ Loading States Refinement
**Priority**: Medium
**File**: `frontend/lib/screens/voice_first_screen.dart`

**What to do**:
- Add stage-based loading messages:
  1. Listening → "녹음 중..."
  2. Processing → "음성을 인식하는 중..."
  3. API Call → "AI가 생각하는 중..."
  4. Responding → "응답을 생성하는 중..."
- Clear loading message when done

---

### 7. ✅ Error Handling Improvements
**Priority**: Medium
**File**: `frontend/lib/screens/voice_first_screen.dart`

**What to do**:
- Better error messages based on error type:
  - Network errors → "네트워크 연결을 확인해주세요"
  - Timeout → "서버 응답 시간 초과"
  - Permission denied → "권한이 필요합니다"
- Show error in LoadingOverlay instead of just SnackBar

---

## Implementation Order

1. **Loading Overlay Integration** (30 min)
   - Add to VoiceFirstScreen Stack
   - Wire to processing state
   - Test with mock delays

2. **Retry Feedback** (20 min)
   - Add onRetry callback
   - Update loading messages
   - Test retry logic

3. **Pitfall Banner Integration** (20 min)
   - Add to VoiceFirstScreen Stack
   - Parse pitfall from response
   - Test with mock pitfall

4. **Navigation Setup** (40 min)
   - Add top bar with icons
   - Create navigation menu
   - Wire to Profile/Settings screens
   - Test navigation flow

5. **Page Transitions** (30 min)
   - Create custom routes
   - Apply to all navigations
   - Test smoothness

6. **Polish & Testing** (30 min)
   - Test all integrations together
   - Verify state management
   - Test on device if possible

---

## Success Criteria

- ✅ LoadingOverlay shows during processing with retry count
- ✅ PitfallWarningBanner appears when pitfall detected
- ✅ Can navigate to Profile and Settings screens
- ✅ Smooth page transitions
- ✅ Loading messages update based on stage
- ✅ Retry feedback shows attempt count
- ✅ All features work together without conflicts
- ✅ No compilation errors
- ✅ Clean flutter analyze

---

## Files to Modify/Create

**Modify**:
1. `frontend/lib/screens/voice_first_screen.dart` - Main integration
2. `frontend/lib/providers/app_state_provider.dart` - May need tweaks

**Create**:
1. `frontend/lib/utils/page_transitions.dart` - Custom transitions
2. `frontend/lib/widgets/app_menu.dart` - Navigation menu (optional)

---

**Estimated Time**: 2-3 hours
**Dependencies**: Phase 5 complete ✅
