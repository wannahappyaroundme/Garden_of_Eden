# 🧪 Project Eden V2 - Quick Test Guide

**For impatient developers who want to test NOW** ⚡

---

## ⏱️ 5-Minute Quick Start

### 1. Start Backend (1 min)
```bash
cd backend
docker-compose up -d
```

### 2. Get Your IP (10 sec)
```bash
# macOS
ipconfig getifaddr en0

# Note the output (e.g., 192.168.1.100)
```

### 3. Update Mobile App (30 sec)
```bash
cd frontend

# Edit lib/utils/constants.dart
# Change this line:
static const String baseUrl = 'http://localhost:8000';
# To:
static const String baseUrl = 'http://YOUR_IP_HERE:8000';
```

### 4. Install Dependencies (1 min)
```bash
flutter pub get
```

### 5. Run on Device (2 min)
```bash
# Connect your phone via USB
flutter devices  # Note your device ID
flutter run -d <device-id>
```

### 6. Test! (1 min)
1. Grant permissions when asked
2. Press and hold mic button
3. Say something in Korean
4. Release button
5. Wait for AI response

**Done!** 🎉

---

## 🎯 Critical Test Points

### Must Work:
1. ✅ Permissions granted
2. ✅ Camera preview visible
3. ✅ Button records when held
4. ✅ Response comes back
5. ✅ TTS plays audio

### Can Debug Later:
- Persona switching
- Profile learning
- Pitfall detection
- Glassmorphism effects

---

## 🐛 Quick Fixes

### "Connection Refused"
```bash
# Your IP is wrong. Get it again:
ipconfig getifaddr en0  # macOS
hostname -I | awk '{print $1}'  # Linux

# Update lib/utils/constants.dart
```

### "No Devices Found"
```bash
# iOS: Trust computer on device
# Android: Enable USB debugging in Settings
flutter devices  # Try again
```

### "Permission Denied"
```bash
# Uninstall app from device
# Run again:
flutter run
# Grant permissions this time
```

### "Backend Not Running"
```bash
cd backend
docker-compose ps  # Check status
docker-compose up -d  # Restart if needed
```

---

## 📋 1-Minute Test Checklist

**Time: 60 seconds after app launches**

- [ ] 0:00 - App opens → Permission screen
- [ ] 0:10 - Tap "권한 허용" → System dialogs
- [ ] 0:20 - Grant both permissions → Main screen
- [ ] 0:25 - Camera preview visible ✅
- [ ] 0:30 - Press and hold button → Turns RED
- [ ] 0:35 - Say "안녕하세요" → Still recording
- [ ] 0:40 - Release button → Turns BLUE
- [ ] 0:50 - Wait... → Turns GREEN
- [ ] 0:55 - Audio plays ✅
- [ ] 1:00 - Overlay shows text ✅

**If all ✅ → SUCCESS!** 🎉

---

## 🚨 Emergency Debugging

### App Crashes Immediately
```bash
flutter logs | grep FATAL
# Read the error, Google it
```

### No Response from Backend
```bash
# Test from device browser:
http://YOUR_IP:8000/health
# If it doesn't load → firewall issue
```

### Audio Doesn't Play
```bash
# Check device volume (duh)
# Check silent mode is OFF
# Restart app
```

---

## 🎓 Pro Tips

1. **Use WiFi**: Both device and computer on same network
2. **Disable VPN**: VPNs can block local connections
3. **Check Firewall**: Allow port 8000
4. **Real Device Only**: Emulators won't work (need camera)
5. **Good Lighting**: Camera captures clearer in bright rooms

---

## 🔥 Speed Run Record

**World Record**: Backend to first conversation: **3 minutes 47 seconds**

Can you beat it? 🏆

---

**Full guide**: See [PHASE_3_DEPLOYMENT_GUIDE.md](./PHASE_3_DEPLOYMENT_GUIDE.md)
