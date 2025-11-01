# 🚀 START HERE - Project Eden V2

**Welcome! Your J.A.R.V.I.S.-like AI companion is ready to test.**

---

## ✅ What's Already Done

- ✅ **Backend**: FastAPI with 7 services, Master Directive system, DynamoDB
- ✅ **Frontend**: Flutter mobile app with voice-first UI
- ✅ **Configuration**: iOS + Android permissions configured
- ✅ **Documentation**: Complete guides and checklists

**Status**: Ready for device testing! 🎉

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Start Backend (1 min)
```bash
cd backend
docker-compose up -d

# Verify it's running
curl http://localhost:8000/health
```

**Expected**: `{"status":"healthy",...}`

---

### Step 2: Get Your IP Address (10 seconds)
```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'
```

**Example output**: `192.168.1.100`

Copy this IP - you'll need it next!

---

### Step 3: Configure Mobile App (30 seconds)

Open `frontend/lib/utils/constants.dart` and update line 22:

```dart
// Change from:
static const String baseUrl = 'http://localhost:8000';

// To (use YOUR IP from Step 2):
static const String baseUrl = 'http://192.168.1.100:8000';
```

---

### Step 4: Install Dependencies (1 min)
```bash
cd frontend
flutter pub get
```

---

### Step 5: Connect Device & Run (2 min)

**iOS**:
1. Connect iPhone/iPad via USB
2. Trust computer on device
3. Run: `flutter run`
4. If prompted, open Xcode and select your Team

**Android**:
1. Enable Developer Mode (tap Build Number 7 times)
2. Enable USB Debugging in Developer Options
3. Connect via USB
4. Run: `flutter run`

---

### Step 6: Test! (1 min)

1. **Grant Permissions**: Tap "권한 허용" → Allow Camera & Mic
2. **Press & Hold**: Hold the microphone button
3. **Speak**: Say something in Korean (e.g., "안녕하세요")
4. **Release**: Let go of the button
5. **Wait**: AI will respond with voice and text

**Expected time**: ~5-10 seconds for response

---

## 🎯 What to Test

### Basic Flow ✅
- [ ] Permissions granted
- [ ] Camera preview shows
- [ ] Button records when held
- [ ] Response comes back
- [ ] TTS audio plays
- [ ] Text appears in overlay

### Advanced Features ✅
- [ ] Switch to Eve persona (top toggle)
- [ ] Test different conversation topics
- [ ] Check backend logs for profile learning
- [ ] Test pitfall detection (if configured)

---

## 🐛 Quick Fixes

### "Connection Refused"
Your IP address is wrong or backend isn't running.

**Fix**:
```bash
# Get IP again
ipconfig getifaddr en0

# Update frontend/lib/utils/constants.dart
# Restart app: flutter run
```

### "No Devices Found"
Device isn't connected properly.

**Fix**:
```bash
# iOS: Trust computer on device
# Android: Enable USB debugging

# Check connection
flutter devices
```

### "Camera Black Screen"
Permissions not granted.

**Fix**:
- iOS: Settings → Project Eden → Camera (ON)
- Android: Settings → Apps → Project Eden → Permissions
- Or uninstall app and reinstall

### Backend Not Responding
```bash
cd backend
docker-compose ps  # Check status
docker-compose logs backend-api  # Check errors
```

---

## 📚 Full Guides

- **This is too fast?** → See [PHASE_3_DEPLOYMENT_GUIDE.md](./PHASE_3_DEPLOYMENT_GUIDE.md)
- **Need more details?** → See [PHASE_3_QUICK_TEST.md](./PHASE_3_QUICK_TEST.md)
- **Want to understand the project?** → See [PROJECT_EDEN_V2_MASTER_SPEC.md](./PROJECT_EDEN_V2_MASTER_SPEC.md)

---

## 🎓 Pro Tips

1. **Use WiFi**: Both devices on same network
2. **Good Lighting**: Camera works better with light
3. **Speak Clearly**: Better STT results
4. **Be Patient**: First response takes 5-10 seconds
5. **Check Logs**: If issues arise, check backend logs

---

## 📊 Expected Behavior

### First Launch
```
1. App opens → Permission screen (black background)
2. Tap "권한 허용" → iOS/Android permission dialogs
3. Grant both → Navigate to main screen
4. Camera initializes → Full-screen preview
```

### First Conversation
```
1. Press mic button → Turns RED (recording)
2. Speak for 2-3 seconds
3. Release → Turns BLUE (processing)
4. Wait 5-10 seconds → Turns GREEN (responding)
5. TTS audio plays automatically
6. Text overlay slides up from bottom
7. Auto-hides after 3 seconds
```

---

## 🎭 Personas

### Adam (아담) - Default
- Logical, father-like tone
- Asks guiding questions
- Direct but caring
- Example: "먼저 생각해봅시다. 이 선택이 목표와 어떻게 연결되나요?"

### Eve (이브)
- Energetic, uplifting tone
- Celebrates and validates
- Warm and encouraging
- Example: "와! 정말 대단한데요! 당신은 이미 충분히 잘하고 있어요!"

**Switch**: Tap "Eve" at the top of screen

---

## 🔍 Verify Backend Learning

After 3-5 conversations, check if AI is learning about you:

```bash
curl http://localhost:8000/api/v2/profile/demo_user
```

Look for:
- `profile_version` increasing (1 → 2 → 3...)
- `top_traits` appearing with weights
- `recent_emotional_state` detected

---

## ⚠️ Known Limitations

- **No Retry**: If request fails, must restart conversation
- **No History**: Conversations not saved locally yet
- **Hardcoded User**: Using "demo_user" ID
- **No Offline**: Requires network connection
- **Portrait Only**: App locked to portrait mode

---

## 🚀 After First Success

Once your first conversation works:

1. **Test Both Personas**: Switch between Adam and Eve
2. **Try Different Topics**: See how AI responds
3. **Check Profile Learning**: Use curl to see profile updates
4. **Test Edge Cases**: Long recordings, silence, background noise
5. **Document Issues**: Note anything that doesn't work

---

## 📝 Feedback Checklist

After testing, note down:

- [ ] What worked perfectly
- [ ] What felt slow or laggy
- [ ] Any errors or crashes
- [ ] UI/UX improvements needed
- [ ] Features you want added

---

## 🎉 Success Criteria

You'll know it's working when:

1. ✅ Camera shows your face
2. ✅ Button responds to touch
3. ✅ Audio records successfully
4. ✅ Backend processes request
5. ✅ TTS audio plays clearly
6. ✅ Text appears and is readable
7. ✅ You can have a back-and-forth conversation

---

## 🆘 Need Help?

### Check Logs
```bash
# Flutter logs
flutter logs | grep -i error

# Backend logs
docker-compose logs -f backend-api

# Both together
tmux  # Or use two terminals
```

### Common Issues
- Connection refused → Wrong IP or firewall
- Camera black → Permissions not granted
- No audio → Check volume and silent mode
- Slow response → Backend processing (normal)

### Documentation
- [PHASE_3_DEPLOYMENT_GUIDE.md](./PHASE_3_DEPLOYMENT_GUIDE.md) - Comprehensive guide
- [PHASE_3_QUICK_TEST.md](./PHASE_3_QUICK_TEST.md) - Quick reference
- [PHASE_3_COMPLETE.md](./PHASE_3_COMPLETE.md) - What was built

---

## 🌟 What Makes This Special?

This isn't just another chatbot. Project Eden:

- **Learns YOU**: Builds weighted personality traits over time
- **Keeps You Focused**: Warns when you stray from your "One Thing"
- **Sees Context**: Camera captures provide visual awareness
- **Feels Personal**: Dual personas adapt to your emotional needs
- **100% Free**: Uses free-tier APIs (Gemini, Groq, Edge TTS)

---

## 💪 Let's Go!

**Everything is ready. Time to meet your AI companion!**

```bash
# Terminal 1
cd backend && docker-compose up -d

# Terminal 2
cd frontend && flutter run
```

**Expected time to first conversation**: 5 minutes

**Good luck! 화이팅!** 🚀

---

## 📌 Quick Reference

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start backend |
| `docker-compose logs -f` | View backend logs |
| `flutter devices` | List connected devices |
| `flutter run` | Run app on device |
| `flutter logs` | View app logs |
| `curl http://localhost:8000/health` | Check backend |

---

**Next**: After successful testing, move to Phase 4 (see [README.md](./README.md))
