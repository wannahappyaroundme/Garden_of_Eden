# Phase 2: Flutter Mobile App - Implementation Plan

## Current Status: IN PROGRESS ⏳

### ✅ Completed (Step 1-3)
1. ✅ Flutter project created (`flutter create`)
2. ✅ Dependencies added to pubspec.yaml
3. ✅ Project structure created (models, providers, services, screens, widgets, theme, utils)
4. ✅ Constants file created (`utils/constants.dart`)
5. ✅ Data models created (`models/chat_models.dart`)
6. ✅ Theme system created (`theme/app_theme.dart`)

### 📋 Remaining Tasks

#### Core Services (Step 4-6)
- [ ] **APIService** - HTTP client for backend communication
- [ ] **AudioService** - Recording (record package) + Playback (just_audio)
- [ ] **CameraService** - 1 FPS capture + keyframe selection

#### State Management (Step 7)
- [ ] **AppStateProvider** - Main Riverpod state (AppMode, persona, lastResponse)
- [ ] **ProfileProvider** - User profile state

#### UI Widgets (Step 8-12)
- [ ] **PersonaToggle** - Adam/Eve switcher (top of screen)
- [ ] **PushToTalkButton** - Large center button with animations
- [ ] **CameraView** - Full-screen camera background
- [ ] **ResponseOverlay** - Bottom 1/3 glassmorphism overlay
- [ ] **TTSWaveform** - Audio waveform animation

#### Main Screen (Step 13)
- [ ] **VoiceFirstScreen** - Assemble all widgets

#### Permissions & Polish (Step 14-15)
- [ ] **PermissionHandler** - Request camera + mic permissions
- [ ] **Main.dart** - App entry point with Riverpod
- [ ] **Error handling** - User-friendly error messages

---

## Simplified Implementation Strategy

Due to the complexity, let's implement in **3 focused batches**:

### Batch 1: Core Services ✅ (Next)
Create the three core services that handle backend communication, audio, and camera.

**Files to create:**
- `lib/services/api_service.dart`
- `lib/services/audio_service.dart`
- `lib/services/camera_service.dart`

### Batch 2: State Management & Providers
Setup Riverpod providers for app state management.

**Files to create:**
- `lib/providers/app_state_provider.dart`
- `lib/providers/profile_provider.dart`

### Batch 3: UI Widgets & Main Screen
Build all UI components and assemble the main screen.

**Files to create:**
- `lib/widgets/persona_toggle.dart`
- `lib/widgets/push_to_talk_button.dart`
- `lib/widgets/camera_view.dart`
- `lib/widgets/response_overlay.dart`
- `lib/widgets/tts_waveform.dart`
- `lib/screens/voice_first_screen.dart`
- `lib/main.dart` (update)

---

## Notes

- Keep each service focused and testable
- Use dependency injection where possible
- Handle errors gracefully with user feedback
- Follow Flutter best practices
- Use async/await for all I/O operations

---

## Next Immediate Steps

1. Create APIService with Dio
2. Create AudioService with record + just_audio
3. Create CameraService with camera package
4. Then move to State Management

Let's proceed with **Batch 1: Core Services** now.
