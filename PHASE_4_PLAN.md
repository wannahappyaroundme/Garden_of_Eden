# 📋 Phase 4: Testing & Integration Plan

**Status**: Starting
**Date**: 2025-11-02
**Goal**: Test the complete system on physical devices

---

## 🎯 Phase 4 Objectives

1. **Backend Testing**: Verify all API endpoints work correctly
2. **Frontend Build**: Get the Flutter app running on physical device
3. **Integration Testing**: Test full conversation flow (voice → backend → TTS)
4. **Feature Testing**: Verify all features work as designed
5. **Bug Documentation**: Document any issues found

---

## ⚠️ System Requirements Discovered

### Current Environment
- **OS**: macOS (Darwin 24.6.0)
- **Python**: 3.11.13 (Available ✅)
- **Docker**: Not installed ❌
- **Flutter**: Need to check

### What We Need

#### Option 1: Docker Setup (Recommended)
```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop

# After installation:
cd backend
docker-compose up -d
```

#### Option 2: Direct Python Setup (Alternative)
```bash
# Install backend dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with API keys

# Run locally
python main.py
```

#### For Frontend
```bash
# Check Flutter
flutter doctor

# If not installed:
# Download from: https://docs.flutter.dev/get-started/install/macos
```

---

## 📝 Phase 4 Testing Plan

### Part 1: Backend Verification (Without Device)

#### 1.1 Start Backend
- [ ] Install Docker OR set up Python environment
- [ ] Start backend server
- [ ] Verify health endpoint: `http://localhost:8000/health`
- [ ] Check API docs: `http://localhost:8000/docs`

#### 1.2 Test API Endpoints
- [ ] GET `/health` - Health check
- [ ] POST `/api/v2/profile` - Create user profile
- [ ] GET `/api/v2/profile/{user_id}` - Get profile
- [ ] POST `/api/v2/chat` - Send chat (without audio/camera)
- [ ] POST `/api/v2/update-profile` - Update profile

#### 1.3 Test Core Services
- [ ] Gemini LLM responds
- [ ] Profile learning creates traits
- [ ] Pitfall detection works
- [ ] TTS generates audio

---

### Part 2: Frontend Setup

#### 2.1 Check Flutter Installation
```bash
flutter doctor -v
```

#### 2.2 Install Dependencies
```bash
cd frontend
flutter pub get
```

#### 2.3 Check for Devices
```bash
flutter devices
```

#### 2.4 Build Test
```bash
# iOS (if available)
flutter build ios --debug

# Android (if available)
flutter build apk --debug
```

---

### Part 3: Integration Testing (With Device)

#### 3.1 Configuration
- [ ] Get local IP address
- [ ] Update `frontend/lib/utils/constants.dart` with IP
- [ ] Verify backend is reachable from device network

#### 3.2 First Launch
- [ ] Deploy app to device
- [ ] Grant camera permission
- [ ] Grant microphone permission
- [ ] Camera preview appears

#### 3.3 Basic Flow Test
- [ ] Press and hold mic button → turns RED
- [ ] Speak for 2-3 seconds
- [ ] Release button → turns BLUE
- [ ] Wait for response → turns GREEN
- [ ] TTS audio plays
- [ ] Text overlay appears
- [ ] Overlay auto-hides after 3 seconds

#### 3.4 Persona Testing
- [ ] Default persona is Adam
- [ ] Tap "Eve" at top
- [ ] Underline animates to Eve
- [ ] Next conversation uses Eve's tone
- [ ] Switch back to Adam

#### 3.5 Profile Learning Testing
- [ ] Have 3-5 conversations
- [ ] Check backend logs for profile updates
- [ ] Verify `profile_version` increments
- [ ] Check traits are being learned
- [ ] Verify trait weights update

#### 3.6 Pitfall Detection Testing
- [ ] Create profile with "One Thing" and "Core Pitfall"
- [ ] Say something aligned → normal response
- [ ] Say something misaligned → benevolent dissent
- [ ] Check `pitfall_warning_triggered` flag

---

### Part 4: Edge Cases & Error Handling

#### 4.1 Network Issues
- [ ] Test with weak WiFi
- [ ] Test connection timeout
- [ ] Verify error messages appear

#### 4.2 Permission Issues
- [ ] Deny camera → error handling
- [ ] Deny microphone → error handling
- [ ] Revoke permissions → app behavior

#### 4.3 Audio Issues
- [ ] Very short recording (< 1 second)
- [ ] Very long recording (> 1 minute)
- [ ] Background noise
- [ ] Silence (no speech)

#### 4.4 Camera Issues
- [ ] Low light conditions
- [ ] Moving camera during recording
- [ ] Verify 1 FPS capture
- [ ] Verify keyframe selection

---

## 🐛 Expected Issues & Solutions

### Issue 1: Docker Not Installed
**Solution**:
- Install Docker Desktop from https://www.docker.com/products/docker-desktop
- OR use Python virtual environment setup

### Issue 2: No Physical Device
**Solution**:
- Borrow iOS/Android device
- Use friend's phone temporarily
- Note: Emulator won't work (needs real camera/mic)

### Issue 3: API Keys Not Set
**Solution**:
```bash
cd backend
cp .env.example .env
nano .env

# Add:
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_key_here
```

### Issue 4: Flutter Not Installed
**Solution**:
- Download from https://docs.flutter.dev/get-started/install/macos
- Follow installation guide
- Run `flutter doctor` to verify

### Issue 5: Backend Can't Connect to DynamoDB
**Solution**:
- If using Docker: DynamoDB Local included in compose
- If using Python: Install DynamoDB Local manually
- OR use actual AWS DynamoDB (free tier)

---

## 📊 Success Criteria

Phase 4 is **COMPLETE** when:

1. ✅ Backend runs and responds to API calls
2. ✅ Frontend builds successfully
3. ✅ App deploys to physical device
4. ✅ Permissions granted without issues
5. ✅ First conversation completes successfully
6. ✅ TTS audio plays clearly
7. ✅ Both personas work (Adam and Eve)
8. ✅ Profile learning observable in logs
9. ✅ No critical bugs found
10. ✅ Test results documented

---

## 🚀 Quick Start Options

### Option A: Full Docker Setup (Easiest)
```bash
# 1. Install Docker Desktop
# 2. Start backend
cd backend && docker-compose up -d

# 3. Get IP
ipconfig getifaddr en0

# 4. Update frontend config
# Edit: frontend/lib/utils/constants.dart

# 5. Run app
cd frontend && flutter run
```

### Option B: Python Backend Only
```bash
# 1. Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with API keys

# 2. Start backend
python main.py

# 3. Get IP
ipconfig getifaddr en0

# 4. Update frontend
# Edit: frontend/lib/utils/constants.dart

# 5. Run app
cd frontend && flutter run
```

### Option C: Test Backend Only (No Device)
```bash
# 1. Start backend (Docker or Python)
cd backend && python main.py

# 2. Test with curl
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v2/chat \
  -F "user_id=test_user" \
  -F "message=안녕하세요" \
  -F "voice_type=adam"

# 3. Check logs
tail -f backend/logs/app.log
```

---

## 📝 Testing Checklist Template

```markdown
## Phase 4 Test Session

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Device**: [iPhone 15 Pro / Pixel 6 / etc]
**Backend**: [Docker / Python Local / AWS]

### Backend Tests
- [ ] Health check passed
- [ ] Profile creation works
- [ ] Chat endpoint works
- [ ] TTS generation works
- [ ] Profile learning works

### Frontend Tests
- [ ] App installs successfully
- [ ] Permissions granted
- [ ] Camera preview works
- [ ] Recording works
- [ ] Backend communication works
- [ ] TTS playback works
- [ ] UI responds correctly

### Integration Tests
- [ ] Full conversation flow works
- [ ] Persona switching works
- [ ] Profile updates after conversations
- [ ] Error handling works

### Issues Found
1. [Description]
   - Severity: High/Medium/Low
   - Steps to reproduce:
   - Expected:
   - Actual:

### Notes
[Any observations]
```

---

## 🎯 Current Status

**Backend**: Not started (Docker not installed)
**Frontend**: Not tested yet
**Device**: Not connected yet

**Next Steps**:
1. Choose setup option (Docker vs Python)
2. Install necessary tools
3. Start backend
4. Test backend APIs
5. Connect device
6. Run frontend
7. Complete integration testing

---

## 📚 Resources

### Installation Guides
- Docker Desktop: https://www.docker.com/products/docker-desktop
- Flutter: https://docs.flutter.dev/get-started/install/macos
- Python venv: https://docs.python.org/3/library/venv.html

### API Documentation
- FastAPI Docs: http://localhost:8000/docs (when running)
- Backend README: [backend/README.md](backend/README.md)

### Testing Guides
- Deployment Guide: [PHASE_3_DEPLOYMENT_GUIDE.md](PHASE_3_DEPLOYMENT_GUIDE.md)
- Quick Test: [PHASE_3_QUICK_TEST.md](PHASE_3_QUICK_TEST.md)

---

**Ready to proceed with Phase 4!** 🚀

Let's start by choosing a setup option and getting the backend running.
