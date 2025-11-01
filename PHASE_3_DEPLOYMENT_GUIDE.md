# 🚀 Project Eden V2 - Phase 3 Deployment Guide

**Status**: Ready for Testing
**Date**: 2025-11-02
**Phase**: 3 of 7 - Testing & Integration

---

## 📋 Prerequisites

### System Requirements
- **macOS**: For iOS development (Xcode required)
- **Flutter SDK**: 3.35.7 or later
- **Python**: 3.12+ (for backend)
- **Docker**: Latest version (for backend services)
- **Physical Device**: iOS 13+ or Android 8.0+ (API 26+)
  - ⚠️ **Emulator will NOT work** - Camera and microphone required

### Development Tools
- Xcode 14+ (for iOS)
- Android Studio (for Android)
- VS Code or Android Studio with Flutter plugins

---

## 🔧 Part 1: Backend Setup

### Step 1: Start Backend Services

```bash
cd backend

# Start all services with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# - backend-api (FastAPI on port 8000)
# - dynamodb-local (on port 8001)
```

### Step 2: Verify Backend Health

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "dynamodb": "connected",
#     "gemini": "available",
#     "groq": "available"
#   }
# }
```

### Step 3: Create Test User Profile

```bash
# Create a test user
curl -X POST http://localhost:8000/api/v2/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "one_thing": "건강한 생활습관 만들기",
    "core_pitfall": "과도한 야근과 불규칙한 식사"
  }'

# Expected response:
# {
#   "user_id": "demo_user",
#   "profile_version": 1,
#   "one_thing": "건강한 생활습관 만들기",
#   "core_pitfall": "과도한 야근과 불규칙한 식사",
#   ...
# }
```

### Step 4: Get Your Local IP Address

The mobile app needs to connect to your backend via local network.

**On macOS:**
```bash
# Option 1: Using ifconfig
ifconfig | grep "inet " | grep -v 127.0.0.1

# Option 2: Using ipconfig
ipconfig getifaddr en0  # WiFi
# or
ipconfig getifaddr en1  # Ethernet

# Expected output example: 192.168.1.100
```

**On Linux:**
```bash
hostname -I | awk '{print $1}'
```

**On Windows:**
```bash
ipconfig | findstr IPv4
```

**Important**: Note down this IP address - you'll need it in the next section.

---

## 📱 Part 2: Mobile App Setup

### Step 1: Update API Configuration

Edit the API base URL to point to your backend:

```bash
cd frontend

# Open the constants file
open lib/utils/constants.dart
```

**Update the baseUrl**:
```dart
class ApiConfig {
  // Change this line:
  static const String baseUrl = 'http://localhost:8000';

  // To your local IP (from Part 1, Step 4):
  static const String baseUrl = 'http://192.168.1.100:8000';  // YOUR_IP_HERE

  // ... rest of the file
}
```

### Step 2: Install Flutter Dependencies

```bash
# Make sure you're in the frontend directory
cd frontend

# Get all dependencies
flutter pub get

# Expected output:
# Running "flutter pub get" in frontend...
# ... downloading packages ...
# Got dependencies!
```

### Step 3: Verify Flutter Doctor

```bash
flutter doctor -v

# Expected output should show:
# [✓] Flutter (Channel stable, 3.35.7)
# [✓] iOS toolchain (if you have Xcode)
# [✓] Android toolchain (if you have Android Studio)
# [✓] Xcode (for iOS development)
# [✓] Android Studio (for Android development)
# [✓] Connected device (when device is plugged in)
```

---

## 📲 Part 3: Deploy to Device

### For iOS Device

#### Step 1: Connect iOS Device
1. Connect iPhone/iPad via USB
2. Trust the computer on your device
3. Verify connection:
```bash
flutter devices

# Expected output:
# iPhone 15 Pro (mobile) • 00008110-001234567890ABCD • ios • iOS 17.0
```

#### Step 2: Open in Xcode (First Time Only)
```bash
# Open iOS project in Xcode
open ios/Runner.xcworkspace
```

In Xcode:
1. Select your device from the top toolbar
2. Go to **Signing & Capabilities** tab
3. Select your **Team** (Apple Developer account)
4. Xcode will automatically create a provisioning profile

#### Step 3: Run on Device
```bash
# Get device ID
flutter devices

# Run on specific device
flutter run -d <your-device-id>

# Or let Flutter choose the device
flutter run
```

**First Launch**: iOS will ask to trust the developer certificate:
1. Go to **Settings** → **General** → **VPN & Device Management**
2. Tap on your developer profile
3. Tap **Trust**
4. Go back to the app and launch it

---

### For Android Device

#### Step 1: Enable Developer Mode
On your Android device:
1. Go to **Settings** → **About Phone**
2. Tap **Build Number** 7 times
3. Enter PIN if prompted
4. "Developer mode enabled" will appear

#### Step 2: Enable USB Debugging
1. Go to **Settings** → **Developer Options**
2. Enable **USB Debugging**
3. Enable **Install via USB** (on some devices)

#### Step 3: Connect and Verify
```bash
# Connect device via USB

# Verify ADB connection
flutter devices

# Expected output:
# Pixel 6 (mobile) • 1A234B5C6D7E8F9G • android-arm64 • Android 13 (API 33)
```

#### Step 4: Run on Device
```bash
# Run on device
flutter run -d <your-device-id>

# Or let Flutter choose
flutter run
```

**First Launch**: Android will ask for USB debugging permission:
1. Tap **Allow** when prompted
2. Check "Always allow from this computer" (optional)

---

## 🧪 Part 4: Testing the App

### Phase 3.1: Permission Testing

**Expected Flow:**
1. App launches → Permission screen appears
2. Tap "권한 허용" (Allow Permissions)
3. iOS: System dialogs appear for Camera and Microphone
4. Android: System dialogs appear for Camera and Microphone
5. Grant both permissions
6. App navigates to main screen automatically

**Test Cases:**
- ✅ Permission screen shows camera and microphone items
- ✅ Both permissions show unchecked initially
- ✅ System permission dialogs appear when tapped
- ✅ After granting, checkmarks appear
- ✅ App navigates to VoiceFirstScreen

**Troubleshooting:**
- If permissions don't appear: Check Info.plist (iOS) or AndroidManifest.xml (Android)
- If app crashes: Check console logs with `flutter logs`

---

### Phase 3.2: Camera Testing

**Expected Flow:**
1. Main screen loads
2. Camera preview appears full-screen
3. Camera is active and showing live preview

**Test Cases:**
- ✅ Camera preview fills entire screen
- ✅ No black bars or distortion
- ✅ Preview is not rotated incorrectly
- ✅ Loading indicator disappears after initialization

**Troubleshooting:**
```bash
# If camera doesn't initialize:
flutter logs

# Look for:
# - CameraException messages
# - Permission denied errors
# - "No cameras available" error
```

---

### Phase 3.3: Voice Recording Testing

**Expected Flow:**
1. Press and hold the microphone button
2. Button turns RED and pulses
3. Recording starts
4. Release button
5. Recording stops
6. Button turns BLUE (processing)

**Test Cases:**
- ✅ Button responds to touch
- ✅ Button color changes (white → red → blue)
- ✅ Animation plays during recording (elastic scale)
- ✅ Recording file is created in temp directory

**Troubleshooting:**
```bash
# Check recording logs
flutter logs | grep -i "audio\|record"

# Common issues:
# - Microphone permission denied
# - Audio format not supported
# - Recording duration too short
```

---

### Phase 3.4: Camera Capture Testing (1 FPS)

**Expected Flow:**
1. During voice recording, camera captures at 1 FPS
2. Frames are stored in memory
3. After recording stops, keyframes are selected

**Test Cases:**
- ✅ Camera captures automatically during recording
- ✅ No visible lag or freezing
- ✅ Maximum 8 keyframes selected
- ✅ Images are compressed to 1024x1024

**Debug Information:**
```dart
// Capture interval: 1000ms (1 FPS)
// Max keyframes: 8
// Image compression: 85% quality
// Max dimensions: 1024x1024
```

**Troubleshooting:**
```bash
# Check capture logs
flutter logs | grep -i "camera\|capture\|frame"

# Common issues:
# - "takePicture" fails during recording
# - Image compression errors
# - Temp file write errors
```

---

### Phase 3.5: Backend Communication Testing

**Expected Flow:**
1. After recording stops, files are sent to backend
2. Backend processes request
3. Response received (text + TTS audio)
4. Button turns GREEN (responding)

**Test Cases:**
- ✅ Network request sent successfully
- ✅ Audio file uploaded (multipart/form-data)
- ✅ Camera frames uploaded (8 images)
- ✅ Response received with status 200
- ✅ JSON parsed correctly

**Verify Backend Received Data:**
```bash
# Watch backend logs
docker-compose logs -f backend-api

# Expected logs:
# POST /api/v2/chat
# - user_id: demo_user
# - voice_type: adam or eve
# - audio_file: [file received]
# - camera_frames: 8 files received
```

**Troubleshooting:**
```bash
# Check network logs
flutter logs | grep -i "http\|api\|dio"

# Common issues:
# - Connection refused (wrong IP address)
# - Timeout (firewall blocking)
# - 400 Bad Request (invalid data format)
# - 500 Server Error (backend issue)
```

**Test Backend Connectivity:**
```bash
# From your mobile device browser, visit:
http://YOUR_IP:8000/health

# Should show:
# {"status":"healthy","services":{...}}
```

---

### Phase 3.6: TTS Playback Testing

**Expected Flow:**
1. Response received from backend
2. TTS audio (base64) decoded automatically
3. Audio plays through device speakers
4. Waveform animation appears
5. Response overlay slides up from bottom

**Test Cases:**
- ✅ Audio plays automatically
- ✅ Sound quality is clear
- ✅ Waveform animation syncs with audio
- ✅ Audio can be heard through speakers
- ✅ Playback completes successfully

**Troubleshooting:**
```bash
# Check audio logs
flutter logs | grep -i "audio\|tts\|playback"

# Common issues:
# - Base64 decode fails
# - Audio format not supported
# - No audio output (check volume)
```

---

### Phase 3.7: Response Overlay Testing

**Expected Flow:**
1. Response text appears in glassmorphism overlay
2. Overlay covers bottom 1/3 of screen
3. Markdown text renders correctly
4. Waveform animates during TTS playback
5. Auto-hides after 3 seconds

**Test Cases:**
- ✅ Overlay appears with backdrop blur
- ✅ Text is readable (white on semi-transparent black)
- ✅ Markdown formatting works (bold, italic, lists)
- ✅ Waveform animation is smooth
- ✅ Swipe down to dismiss works
- ✅ Auto-hide after 3 seconds

**Troubleshooting:**
```bash
# Check overlay logs
flutter logs | grep -i "overlay\|response\|markdown"

# Common issues:
# - Backdrop blur not working (device limitation)
# - Text color contrast too low
# - Animation stuttering (performance issue)
```

---

### Phase 3.8: Persona Switching Testing

**Expected Flow:**
1. Top of screen shows "Adam | Eve" toggle
2. Tap on "Eve"
3. Underline animates to Eve
4. Next conversation uses Eve persona

**Test Cases:**
- ✅ Toggle renders at top of screen
- ✅ Adam is selected by default
- ✅ Tap switches persona
- ✅ Underline animation is smooth
- ✅ Backend receives correct persona

**Verify Backend:**
```bash
# Check backend logs after switching persona
docker-compose logs -f backend-api | grep "voice_type"

# Should show:
# voice_type: eve  (after switching)
```

---

### Phase 3.9: Pitfall Warning Testing

**Expected Flow:**
1. Create user profile with core pitfall
2. Say something that triggers pitfall
3. Backend detects misalignment
4. Response includes benevolent dissent
5. UI shows warning (future implementation)

**Setup Test Profile:**
```bash
curl -X POST http://localhost:8000/api/v2/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "one_thing": "건강한 생활습관 만들기",
    "core_pitfall": "야근하면서 라면 먹기"
  }'
```

**Test Scenarios:**
1. **Aligned**: "오늘 아침 운동했어요" → Normal response
2. **Misaligned**: "오늘도 야근하면서 라면 먹어야지" → Benevolent dissent

**Expected Response Fields:**
```json
{
  "pitfall_warning_triggered": true,
  "response_text": "[⚠️ 주의사항] ... benevolent dissent message ...",
  "emotional_support_mode": false
}
```

**Test Cases:**
- ✅ Backend detects pitfall correctly
- ✅ Response includes warning message
- ✅ App receives pitfall_warning_triggered: true
- ⏸️ UI warning indicator (not implemented yet)

---

### Phase 3.10: Profile Learning Testing

**Expected Flow:**
1. Have multiple conversations
2. Backend learns personality traits
3. Profile version increments
4. Responses become more personalized

**Test Cases:**
- ✅ profile_updated: true in response
- ✅ profile_version increments each conversation
- ✅ Traits appear in profile
- ✅ Weights update over time

**Verify Profile Learning:**
```bash
# Get user profile after 5+ conversations
curl http://localhost:8000/api/v2/profile/demo_user

# Check personality_summary:
# {
#   "top_traits": [
#     {"name": "건강_지향적", "weight": 0.7},
#     {"name": "자기_성찰적", "weight": 0.6},
#     ...
#   ]
# }
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Connection Refused"
**Symptoms**: App crashes when trying to send chat
**Cause**: Backend not reachable
**Solution**:
```bash
# 1. Verify backend is running
docker-compose ps

# 2. Check firewall
# macOS: System Settings → Network → Firewall → Allow port 8000
# Windows: Windows Defender Firewall → Allow port 8000

# 3. Test connectivity from device
# Open device browser, go to: http://YOUR_IP:8000/health
```

### Issue 2: Camera Black Screen
**Symptoms**: Camera preview is black
**Cause**: Permission denied or wrong camera selected
**Solution**:
```bash
# 1. Check permissions in Settings app
# iOS: Settings → Project Eden → Camera (should be ON)
# Android: Settings → Apps → Project Eden → Permissions

# 2. Uninstall and reinstall app
flutter clean
flutter run
```

### Issue 3: No Audio Playback
**Symptoms**: TTS received but no sound
**Cause**: Volume too low or audio session issue
**Solution**:
```bash
# 1. Check device volume
# 2. Check silent mode is OFF
# 3. Restart app
# 4. Check logs:
flutter logs | grep -i "audio\|player"
```

### Issue 4: App Crashes on Launch
**Symptoms**: App closes immediately after opening
**Cause**: Missing dependencies or configuration
**Solution**:
```bash
# 1. Clean and rebuild
flutter clean
flutter pub get
flutter run

# 2. Check logs
flutter logs

# 3. Verify permissions in manifest files
cat ios/Runner/Info.plist | grep -A1 "Camera\|Microphone"
cat android/app/src/main/AndroidManifest.xml | grep "permission"
```

### Issue 5: "Bad Request" from Backend
**Symptoms**: Button turns blue, then shows error
**Cause**: Invalid data format or missing fields
**Solution**:
```bash
# Check backend logs
docker-compose logs backend-api

# Common causes:
# - Audio file empty (recording too short)
# - Camera frames empty (capture failed)
# - Invalid voice_type (not "adam" or "eve")
```

---

## 📊 Testing Checklist

Copy this checklist and mark off items as you test:

### Basic Functionality
- [ ] App installs successfully on device
- [ ] Permission screen appears on first launch
- [ ] Camera permission granted successfully
- [ ] Microphone permission granted successfully
- [ ] Camera preview shows full screen
- [ ] Push-to-talk button responds to touch
- [ ] Button animates correctly (color + scale)
- [ ] Audio recording starts on press
- [ ] Audio recording stops on release
- [ ] Camera captures at 1 FPS during recording

### Backend Communication
- [ ] Backend is running and accessible
- [ ] API base URL configured correctly
- [ ] Chat request sent successfully
- [ ] Audio file uploaded
- [ ] 8 camera frames uploaded
- [ ] Response received within 5-10 seconds
- [ ] No network errors in logs

### Response Handling
- [ ] TTS audio decoded from base64
- [ ] TTS audio plays automatically
- [ ] Audio quality is clear
- [ ] Response overlay appears
- [ ] Glassmorphism effect visible
- [ ] Markdown text renders correctly
- [ ] Waveform animation is smooth
- [ ] Overlay auto-hides after 3 seconds
- [ ] Swipe-to-dismiss works

### Persona System
- [ ] Adam/Eve toggle visible at top
- [ ] Adam selected by default
- [ ] Tap switches to Eve
- [ ] Underline animation smooth
- [ ] Backend receives correct persona
- [ ] Adam response is logical/father-like
- [ ] Eve response is energetic/uplifting

### Profile & Learning
- [ ] User profile created in backend
- [ ] profile_version increments after conversations
- [ ] profile_updated flag appears in responses
- [ ] Personality traits detected over time
- [ ] Trait weights update correctly

### Pitfall Detection
- [ ] Core pitfall configured in profile
- [ ] Aligned conversation → normal response
- [ ] Misaligned conversation → benevolent dissent
- [ ] pitfall_warning_triggered flag correct
- [ ] Warning message in response text

### Error Handling
- [ ] Network errors show SnackBar
- [ ] Permission denied shows error
- [ ] Camera errors show message
- [ ] Audio errors show message
- [ ] App doesn't crash on errors

### Performance
- [ ] App launches within 3 seconds
- [ ] Camera preview is smooth (no lag)
- [ ] Recording has no delays
- [ ] Button animations are smooth
- [ ] Response appears within 10 seconds
- [ ] TTS plays without stuttering

---

## 🎯 Success Criteria

Phase 3 is considered **COMPLETE** when:

1. ✅ App runs on physical device (iOS or Android)
2. ✅ All permissions granted successfully
3. ✅ Camera preview shows correctly
4. ✅ Push-to-talk records audio
5. ✅ Camera captures 1 FPS during recording
6. ✅ Backend communication successful
7. ✅ Response received and displayed
8. ✅ TTS audio plays correctly
9. ✅ Persona switching works
10. ✅ Profile learning observable

**Optional Bonus:**
- ✅ Pitfall detection tested
- ✅ Both Adam and Eve personas tested
- ✅ Multiple conversations completed
- ✅ Profile traits visible

---

## 📝 Test Results Template

```markdown
## Test Session Report

**Date**: YYYY-MM-DD
**Tester**: [Your Name]
**Device**: [e.g., iPhone 15 Pro, iOS 17.0]
**Backend**: [e.g., Docker on macOS 14.0]

### Results
- Permissions: ✅ / ❌
- Camera: ✅ / ❌
- Recording: ✅ / ❌
- Backend: ✅ / ❌
- TTS: ✅ / ❌
- Persona: ✅ / ❌

### Issues Found
1. [Issue description]
   - Severity: High / Medium / Low
   - Steps to reproduce: ...
   - Expected: ...
   - Actual: ...

### Notes
[Any additional observations]
```

---

## 🔄 Next Steps After Phase 3

Once Phase 3 is complete, proceed to:

**Phase 4: UI/UX Polish**
- Add pitfall warning UI indicator
- Add profile viewing screen
- Add settings screen
- Improve loading states
- Add retry logic for failed requests
- Polish animations

**Phase 5: Profile Management**
- Profile editing interface
- Goal setting flow
- Pitfall configuration
- Personality insights visualization

**Phase 6: Advanced Features**
- Conversation history
- Context awareness
- Emotional support mode UI
- Multi-user support

**Phase 7: Production Ready**
- Error tracking (Sentry)
- Analytics (Firebase)
- Performance monitoring
- App Store deployment

---

## 📚 Resources

### Documentation
- [Flutter Documentation](https://docs.flutter.dev)
- [Riverpod Documentation](https://riverpod.dev)
- [Camera Plugin](https://pub.dev/packages/camera)
- [Record Package](https://pub.dev/packages/record)
- [Just Audio](https://pub.dev/packages/just_audio)

### Debugging Tools
```bash
# Flutter logs (all)
flutter logs

# Filter by severity
flutter logs --verbose
flutter logs | grep ERROR

# Device logs (iOS)
idevicesyslog

# Device logs (Android)
adb logcat

# Network traffic (iOS)
# Use Charles Proxy or Proxyman

# Network traffic (Android)
# Use Chrome DevTools or Flipper
```

### Backend Logs
```bash
# All services
docker-compose logs -f

# Just API
docker-compose logs -f backend-api

# Filter by error
docker-compose logs backend-api | grep ERROR
```

---

## ✅ Phase 3 Completion Checklist

Before marking Phase 3 complete:

- [ ] Permissions configured for both platforms
- [ ] API base URL updated to local IP
- [ ] App runs on physical device
- [ ] All basic features tested (see Testing Checklist)
- [ ] Backend communication verified
- [ ] No critical bugs found
- [ ] Test results documented
- [ ] Next steps identified

---

**🎉 Ready to Test? Let's Go!** 🚀

Start with Part 1 (Backend Setup) and work your way through each section systematically.

Good luck! 화이팅! 💪
