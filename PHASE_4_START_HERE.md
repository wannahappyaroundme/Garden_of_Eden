# 🚀 Phase 4: Let's Test This Thing!

**Current Status**: Ready to start testing
**What You Have**: Python 3.11 ✅, Flutter 3.35.7 ✅
**What You Need**: Backend running, Physical device

---

## ⚡ Quick Start - 3 Options

### Option 1: Backend Only Testing (No Device Needed)

Test the backend APIs without needing a phone. Good for verifying backend works!

```bash
# Step 1: Set up backend
cd backend
./setup_local.sh

# Step 2: Edit API keys
nano .env
# Add your GEMINI_API_KEY and GROQ_API_KEY
# Save: Ctrl+X, Y, Enter

# Step 3: Start server
./start_local.sh

# Step 4: Test in another terminal
curl http://localhost:8000/health
```

---

### Option 2: Full Stack Testing (Need Physical Device)

Test the complete system - backend + mobile app.

```bash
# Terminal 1: Start backend
cd backend
./setup_local.sh
nano .env  # Add API keys
./start_local.sh

# Terminal 2: Get your IP
ipconfig getifaddr en0

# Edit frontend/lib/utils/constants.dart
# Change baseUrl to: http://YOUR_IP:8000

# Terminal 2: Run app
cd frontend
flutter pub get
flutter devices  # Connect phone via USB
flutter run
```

---

### Option 3: Install Docker First (Easiest Long-term)

If you want the smoothest experience, install Docker:

```bash
# 1. Download Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# 2. Install and open Docker Desktop

# 3. Start backend
cd backend
docker-compose up -d

# 4. Test
curl http://localhost:8000/health
```

---

## 📋 What We'll Test

### Backend Tests (No Device)
1. ✅ Health check
2. ✅ Create user profile
3. ✅ Send chat message
4. ✅ Profile learning
5. ✅ TTS generation

### Frontend Tests (Need Device)
1. ✅ App installs
2. ✅ Permissions granted
3. ✅ Camera preview works
4. ✅ Recording works
5. ✅ Full conversation flow

### Integration Tests
1. ✅ Voice → Backend → Response
2. ✅ Camera frames captured and sent
3. ✅ Profile updates after conversations
4. ✅ Persona switching (Adam ↔ Eve)
5. ✅ Pitfall detection

---

## 🎯 Let's Start with Backend

### Step 1: Setup (2 minutes)

```bash
cd backend
./setup_local.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Create .env template

### Step 2: Get API Keys (5 minutes)

You need TWO free API keys:

#### Gemini API (FREE)
1. Go to: https://ai.google.dev/
2. Click "Get API Key"
3. Sign in with Google
4. Create new API key
5. Copy it

#### Groq API (FREE)
1. Go to: https://console.groq.com/
2. Sign up (free)
3. Create API key
4. Copy it

### Step 3: Configure (1 minute)

```bash
nano .env
```

Add your keys:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
GROQ_API_KEY=your_actual_groq_key_here

# You can leave these as-is for now
USE_LOCAL_DYNAMODB=true
AWS_ACCESS_KEY_ID=dummy
AWS_SECRET_ACCESS_KEY=dummy
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Start Backend (30 seconds)

```bash
./start_local.sh
```

You should see:
```
✅ Starting server...
   API: http://localhost:8000
   Docs: http://localhost:8000/docs
```

Leave this terminal running!

---

## 🧪 Backend Testing (5 minutes)

Open a NEW terminal:

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "services": {
    "gemini": "available",
    "groq": "available"
  }
}
```

### Test 2: Create User Profile
```bash
curl -X POST http://localhost:8000/api/v2/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "one_thing": "SNU HCI Lab에 합격하기",
    "core_pitfall": "능력 함정 - 여러 기술 공부하느라 집중 못함"
  }'
```

**Expected**: JSON with profile details

### Test 3: Send Chat
```bash
curl -X POST http://localhost:8000/api/v2/chat \
  -F "user_id=test_user" \
  -F "message=안녕하세요, 오늘 기분이 좋아요" \
  -F "voice_type=adam"
```

**Expected**: JSON with:
- `response_text`: AI's text response
- `response_audio_base64`: TTS audio (long string)
- `profile_updated`: true
- `profile_version`: 2

### Test 4: Check Profile Learning
```bash
curl http://localhost:8000/api/v2/profile/test_user
```

**Expected**: Profile with `profile_version: 2` and possibly some traits

---

## 📱 Frontend Setup (If You Have Device)

### Check Device Availability

```bash
# Connect iPhone/iPad or Android phone via USB
flutter devices
```

**iOS**: Trust computer on device first
**Android**: Enable USB debugging in Developer Options

### Update API Configuration

```bash
# Get your local IP
ipconfig getifaddr en0  # macOS
# Example output: 192.168.1.100
```

Edit `frontend/lib/utils/constants.dart`:
```dart
// Line 22 - change from:
static const String baseUrl = 'http://localhost:8000';

// To (use YOUR IP):
static const String baseUrl = 'http://192.168.1.100:8000';
```

### Install Dependencies

```bash
cd frontend
flutter pub get
```

### Run on Device

```bash
flutter run
```

Flutter will:
1. Build the app
2. Install on device
3. Launch automatically

---

## 🎉 Your First Conversation

Once the app is running:

1. **Grant Permissions**
   - Tap "권한 허용"
   - Allow Camera
   - Allow Microphone

2. **Test Recording**
   - Press and hold the mic button
   - Button turns RED → Recording
   - Say "안녕하세요, 테스트입니다"
   - Release button

3. **Wait for Response**
   - Button turns BLUE → Processing
   - Wait 5-10 seconds
   - Button turns GREEN → Responding
   - Audio plays automatically
   - Text appears in overlay

4. **Success!**
   - You just had your first conversation with Eden!

---

## 🐛 Common Issues

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Fix**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `API key not found`
**Fix**:
- Edit `.env` file
- Add real API keys (not "your_key_here")

### Frontend Won't Build

**Error**: `flutter: command not found`
**Fix**:
```bash
# Add Flutter to PATH
export PATH="$PATH:/usr/local/bin/flutter/bin"
# Or install from: https://docs.flutter.dev/get-started/install/macos
```

**Error**: `No devices found`
**Fix**:
- iOS: Trust computer on device (Settings → General → VPN & Device Management)
- Android: Enable USB debugging (Settings → Developer Options)

### App Connection Failed

**Error**: "Connection refused" or "Network error"
**Fix**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify IP address is correct in `constants.dart`
3. Make sure phone and computer on same WiFi
4. Try pinging from device browser: `http://YOUR_IP:8000/health`

---

## 📊 Testing Checklist

### Backend Tests
- [ ] `./setup_local.sh` completed
- [ ] API keys added to `.env`
- [ ] `./start_local.sh` started server
- [ ] Health check returns "healthy"
- [ ] Profile creation works
- [ ] Chat endpoint works
- [ ] TTS audio generated

### Frontend Tests (If Device Available)
- [ ] `flutter devices` shows device
- [ ] `frontend/lib/utils/constants.dart` updated with IP
- [ ] `flutter pub get` completed
- [ ] `flutter run` builds and deploys
- [ ] App launches on device
- [ ] Permissions granted
- [ ] Camera preview appears
- [ ] Recording works (button turns red)
- [ ] Backend receives request (check logs)
- [ ] Response returns (button turns green)
- [ ] TTS audio plays
- [ ] Text overlay appears

### Integration Tests
- [ ] Full conversation completed
- [ ] Persona toggle switches (Adam ↔ Eve)
- [ ] Profile version increments after chat
- [ ] Multiple conversations work
- [ ] No crashes or errors

---

## 🎯 Next Steps After First Success

Once you complete your first conversation:

1. **Test Both Personas**
   - Tap "Eve" at top
   - Have a conversation
   - Notice the tone difference

2. **Test Profile Learning**
   - Have 3-5 conversations
   - Check profile: `curl http://localhost:8000/api/v2/profile/test_user`
   - Look for traits being learned

3. **Test Pitfall Detection**
   - Create profile with clear "One Thing"
   - Say something aligned → normal response
   - Say something misaligned → benevolent dissent

4. **Document Issues**
   - Note any bugs or crashes
   - Save error messages
   - Take screenshots if helpful

5. **Move to Phase 5**
   - UI/UX improvements
   - Add missing features
   - Polish animations

---

## 💪 You've Got This!

**Current Progress**:
- ✅ Phase 1: Backend built
- ✅ Phase 2: Frontend built
- ✅ Phase 3: Configured
- 🔄 Phase 4: Testing NOW!

**Time Estimate**:
- Backend setup: 10 minutes
- First backend test: 2 minutes
- Frontend setup: 5 minutes
- First conversation: 1 minute

**Total**: ~20 minutes to first working conversation!

---

## 📚 Quick Reference

### Backend Commands
```bash
cd backend
./setup_local.sh              # First time setup
nano .env                     # Edit API keys
./start_local.sh              # Start server
curl http://localhost:8000/health  # Test health
```

### Frontend Commands
```bash
cd frontend
flutter pub get              # Install deps
flutter devices              # List devices
flutter run                  # Run app
flutter logs                 # View logs
```

### Useful Checks
```bash
# Get local IP
ipconfig getifaddr en0

# Check backend logs
tail -f backend/logs/app.log

# Check if port 8000 in use
lsof -i :8000

# Kill process on port 8000
kill -9 $(lsof -t -i:8000)
```

---

**Ready? Let's start!** 🚀

**Step 1**: `cd backend && ./setup_local.sh`

Good luck! 화이팅! 💪
