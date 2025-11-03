# 🧪 Project Eden V2 - Simulator/Emulator Testing Guide

**Apple Silicon Mac에서 iOS/Android 시뮬레이터로 테스트하기**

Version: 1.0 | Last Updated: 2025-11-03

---

## ⚠️ 중요: 시뮬레이터 제약사항

### iOS 시뮬레이터의 치명적 한계

**작동하지 않는 기능:**
- ❌ **오디오 녹음**: iOS 15/Xcode 15 이후 시뮬레이터에서 녹음 실패 (알려진 버그)
- ❌ **카메라 프리뷰/캡처**: 하드웨어 제약으로 완전히 지원 안 됨
- ❌ **멀티모달 테스트**: 음성+카메라 동시 테스트 불가능

**작동하는 기능:**
- ✅ **권한 프롬프트**: 정상 작동
- ✅ **오디오 재생**: TTS 재생 가능
- ✅ **UI/로직 테스트**: 화면 표시 및 상태 관리

**결론: iOS는 실물 iPhone/iPad 필수!**

### Android 에뮬레이터 (권장)

**작동하는 기능:**
- ✅ **오디오 녹음**: 설정 후 정상 작동 (16kHz 권장)
- ✅ **카메라**: Webcam 또는 Emulated 모드로 작동
- ✅ **멀티모달 테스트**: 음성+카메라 동시 테스트 가능
- ✅ **권한 프롬프트**: 정상 작동

**알려진 제약:**
- ⚠️ 가끔 오디오에 잡음 발생 가능
- ⚠️ 카메라 화질은 실기기보다 낮음
- ⚠️ 성능은 실기기보다 느림

**결론: Android 에뮬레이터로 대부분의 기능 테스트 가능!**

---

## 📋 Prerequisites (필수 준비사항)

### 소프트웨어

```bash
# 1. Xcode (iOS 개발)
xcode-select --install
# Xcode 15+ 필요 (App Store에서 설치)

# 2. Flutter SDK
flutter --version
# Flutter 3.35.7+ 필요

# 3. Android Studio
# https://developer.android.com/studio 에서 다운로드
# Android SDK, Platform Tools 포함

# 4. 설치 확인
flutter doctor
```

**flutter doctor 출력 예시:**
```
[✓] Flutter (Channel stable, 3.35.7)
[✓] Android toolchain - develop for Android devices (Android SDK 34.0.0)
[✓] Xcode - develop for iOS and macOS (Xcode 15.0)
[✓] Chrome - develop for the web
[✓] Android Studio (version 2023.1)
[✓] VS Code (version 1.85)
[✓] Connected device (3 available)
```

### 하드웨어

| 목적 | 필수/권장 | 기기 |
|------|----------|------|
| iOS 음성+카메라 테스트 | **필수** | iPhone 13+ 또는 iPhone SE 3세대 |
| Android 테스트 | 권장 | 에뮬레이터로 대체 가능 |
| 성능 테스트 | 권장 | 실기기 모두 |

**예산 옵션:**
- iPhone SE 3세대 (2022): ~$429 (Apple 공식)
- 중고 iPhone 13: ~$300-400 (eBay/중고나라)

---

## 🚀 Quick Start (5분 빠른 시작)

### Option 1: Android 에뮬레이터 (일일 개발용)

```bash
# 1. Android Studio에서 에뮬레이터 생성 (처음 한 번만)
# Android Studio → Tools → Device Manager → Create Device
# - Phone: Pixel 7
# - System Image: arm64-v8a, API Level 30 (Android 11)
# - Advanced: Camera Front/Back = Webcam0, Enable Virtual Microphone

# 2. 에뮬레이터 실행
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_30

# 또는 Android Studio에서 실행
# Device Manager → ▶️ 버튼 클릭

# 3. 앱 실행
cd /Users/kyungsbook/Desktop/myai/frontend
flutter run
# 기기 선택 프롬프트에서 Android 에뮬레이터 선택

# 4. 권한 자동 부여 (선택사항)
adb shell pm grant com.example.frontend android.permission.CAMERA
adb shell pm grant com.example.frontend android.permission.RECORD_AUDIO
```

### Option 2: iOS 실물 기기 (필수)

```bash
# 1. iPhone USB로 Mac에 연결

# 2. iPhone에서:
#    - "이 컴퓨터를 신뢰하시겠습니까?" → 신뢰
#    - 설정 → 개인정보 보호 및 보안 → 개발자 모드 켜기 (iOS 16+)

# 3. 기기 확인
flutter devices
# 출력: iPhone (model) • <device-id> • ios • iOS 17.0

# 4. 앱 실행
cd /Users/kyungsbook/Desktop/myai/frontend
flutter run -d <device-id>
# 또는 그냥 flutter run 후 기기 선택
```

### Option 3: iOS 시뮬레이터 (제한적 테스트만 가능)

```bash
# 1. 시뮬레이터 실행
open -a Simulator

# 또는 특정 시뮬레이터 부팅
xcrun simctl boot "iPhone 16e"
open -a Simulator

# 2. 앱 실행
cd /Users/kyungsbook/Desktop/myai/frontend
flutter run
# 시뮬레이터 자동 선택됨

# ⚠️ 주의: 음성 녹음과 카메라는 작동하지 않습니다!
```

---

## Part 1: iOS 테스트

### 1.1 iOS 시뮬레이터 설정 (제한적 테스트용)

#### 사용 가능한 시뮬레이터 확인

```bash
# 설치된 모든 시뮬레이터 목록
xcrun simctl list devices

# 부팅된 시뮬레이터만 표시
xcrun simctl list devices | grep Booted
```

**출력 예시:**
```
-- iOS 17.0 --
    iPhone 15 (UUID-1234) (Shutdown)
    iPhone 15 Pro (UUID-5678) (Shutdown)
    iPhone 16e (UUID-9012) (Booted)
    iPad Pro 12.9-inch (UUID-3456) (Shutdown)
```

#### 시뮬레이터 실행

```bash
# 방법 1: Simulator 앱 열기 (가장 간단)
open -a Simulator

# 방법 2: 특정 시뮬레이터 부팅
xcrun simctl boot "iPhone 15 Pro"
open -a Simulator

# 방법 3: Flutter에서 자동 실행
cd frontend
flutter run  # 시뮬레이터가 자동으로 선택됨
```

#### 권한 자동 부여 (테스트용)

```bash
# 현재 부팅된 시뮬레이터에 권한 부여
xcrun simctl privacy booted grant camera com.example.frontend
xcrun simctl privacy booted grant microphone com.example.frontend
xcrun simctl privacy booted grant photos com.example.frontend

# 특정 시뮬레이터에 권한 부여
xcrun simctl privacy <device-UUID> grant camera com.example.frontend

# 권한 확인
xcrun simctl privacy booted list
```

#### 시뮬레이터에서 테스트 가능한 것

✅ **가능:**
- UI 레이아웃 및 반응형 디자인
- 상태 관리 (Riverpod providers)
- 네트워크 요청 (API 호출)
- 권한 프롬프트 표시
- 오디오 재생 (TTS 듣기)
- 이미지 선택 (갤러리에서)
- 페이지 전환 및 네비게이션

❌ **불가능:**
- 오디오 녹음 (`record` 패키지 실패)
- 카메라 프리뷰 (`availableCameras()` 빈 배열 반환)
- 카메라 캡처
- 멀티모달 플로우 (음성+카메라)
- 실제 하드웨어 성능 측정

#### 시뮬레이터 단축키

```
⌘ + 1/2/3/4/5 : 화면 크기 조정 (50%, 75%, 100%...)
⌘ + K         : 소프트웨어 키보드 토글
⌘ + ←/→       : 화면 회전
⌘ + S         : 스크린샷
⌘ + Shift + H : 홈 버튼
⌘ + Shift + A : 앱 전환
```

---

### 1.2 실물 iOS 기기 설정 (필수!)

#### Step 1: iPhone/iPad 준비

```bash
# 1. iPhone을 USB-C 또는 Lightning 케이블로 Mac에 연결

# 2. iPhone에서 팝업 표시:
#    "이 컴퓨터를 신뢰하시겠습니까?"
#    → [신뢰] 탭
#    → iPhone 암호 입력

# 3. iPhone 설정:
#    설정 → 개인정보 보호 및 보안 → 개발자 모드
#    → 개발자 모드 켜기
#    → iPhone 재시동
#    → "개발자 모드 켜기" 다시 확인

# 4. 기기 연결 확인
flutter devices
```

**출력 예시:**
```
Found 3 connected devices:
  iPhone 15 Pro (mobile) • 00008030-001234567890 • ios • iOS 17.0.1
  iPhone 16e (simulator) • UUID-9012 • ios • iOS 17.0 (simulator)
  sdk gphone64 arm64 (emulator) • emulator-5554 • android • Android 13 (API 33)
```

#### Step 2: 앱 배포 및 실행

```bash
cd /Users/kyungsbook/Desktop/myai/frontend

# 방법 1: 기기 ID로 직접 실행
flutter run -d 00008030-001234567890

# 방법 2: flutter run 후 선택
flutter run
# 프롬프트:
# [1]: iPhone 15 Pro (00008030-001234567890)
# [2]: iPhone 16e (simulator)
# [3]: sdk gphone64 arm64 (emulator)
# Please choose one (or "q" to quit): 1

# 빌드 + 설치 + 실행 (최초 1-2분 소요)
```

#### Step 3: 권한 부여

앱 최초 실행 시 자동으로 권한 프롬프트 표시:

1. **카메라 권한**: "Eden이 카메라에 접근하려고 합니다" → [허용]
2. **마이크 권한**: "Eden이 마이크에 접근하려고 합니다" → [허용]

**권한 거부 시 재요청:**
```
설정 → Eden → 권한
→ 카메라 [켜기]
→ 마이크 [켜기]
```

#### Step 4: 테스트 시나리오

**전체 멀티모달 플로우:**
```
1. 앱 실행
2. 권한 허용 (카메라 + 마이크)
3. 카메라 프리뷰 확인
4. 마이크 버튼 길게 누르기
5. "안녕하세요, 오늘 기분이 어때요?" 말하기
6. 버튼 놓기
7. 로딩 오버레이 확인
8. 8개 키프레임 캡처 확인 (1 FPS)
9. 백엔드 응답 대기
10. TTS 오디오 재생 확인
11. 응답 텍스트 오버레이 확인
```

**개별 기능 테스트:**
- 음성 녹음만: 카메라 꺼진 상태에서 테스트
- 카메라만: 설정에서 카메라 활성화 후 프리뷰 확인
- 페르소나 전환: Adam ↔ Eve 토글
- 프로필 화면: 왼쪽 상단 👤 아이콘
- 설정 화면: 오른쪽 상단 ⚙️ 아이콘

---

### 1.3 iOS 테스트 명령어 모음

```bash
# === 기기 관리 ===

# 모든 기기 목록 (시뮬레이터 + 실기기)
flutter devices

# iOS 시뮬레이터만 목록
xcrun simctl list devices available

# 시뮬레이터 부팅
xcrun simctl boot "iPhone 15 Pro"

# 시뮬레이터 종료
xcrun simctl shutdown "iPhone 15 Pro"

# 모든 시뮬레이터 종료
xcrun simctl shutdown all

# 시뮬레이터 초기화 (앱 삭제, 데이터 초기화)
xcrun simctl erase "iPhone 15 Pro"

# === 앱 실행 ===

# 시뮬레이터에서 실행
flutter run -d <simulator-UUID>

# 실기기에서 실행
flutter run -d <device-UUID>

# 디버그 모드 (기본값)
flutter run

# 릴리스 모드 (최적화된 빌드)
flutter run --release

# 프로파일 모드 (성능 분석)
flutter run --profile

# === 권한 관리 (시뮬레이터만) ===

# 카메라 권한 부여
xcrun simctl privacy booted grant camera com.example.frontend

# 마이크 권한 부여
xcrun simctl privacy booted grant microphone com.example.frontend

# 권한 거부
xcrun simctl privacy booted revoke camera com.example.frontend

# 모든 권한 초기화
xcrun simctl privacy booted reset all

# 권한 목록 확인
xcrun simctl privacy booted list

# === 빌드 ===

# iOS 빌드만 (실행 안 함)
flutter build ios

# 빌드 정리 후 재빌드
flutter clean
flutter pub get
flutter build ios

# === 로그 확인 ===

# Flutter 로그
flutter logs

# iOS 시스템 로그
xcrun simctl spawn booted log stream --predicate 'eventMessage contains "Eden"'

# === Hot Reload ===

# 앱 실행 중
# 코드 수정 후 터미널에서:
r   # Hot reload (빠름, 상태 유지)
R   # Hot restart (느림, 상태 초기화)
q   # 종료
```

---

## Part 2: Android 테스트

### 2.1 Android 에뮬레이터 생성 (Apple Silicon 최적화)

#### Step 1: Android Studio 열기

```bash
# Android Studio 실행
open -a "Android Studio"

# 또는 Spotlight 검색: ⌘ + Space → "Android Studio"
```

#### Step 2: Device Manager 접근

```
Android Studio 메뉴:
Tools → Device Manager (또는 Tools → AVD Manager)

또는:
상단 툴바에서 휴대폰 아이콘 🔧 클릭
```

#### Step 3: 가상 기기 생성

**1. Create Virtual Device 클릭**

**2. 하드웨어 선택:**
```
Category: Phone
Device: Pixel 7 (권장) 또는 Pixel 6

특징:
- 6.3" 1080x2400
- 420 dpi
- arm64-v8a 아키텍처 지원

[Next] 클릭
```

**3. 시스템 이미지 선택 (중요!):**
```
Release Name: Tiramisu (API Level 33, Android 13)
또는: S (API Level 31, Android 12)

ABI: arm64-v8a ⚠️ 필수! (Apple Silicon 최적화)
Target: Google Play 또는 Google APIs

다운로드 필요 시:
[Download] 클릭 → 다운로드 완료 대기 (약 1-2GB)

[Next] 클릭
```

**4. AVD 설정:**
```
AVD Name: Pixel_7_API_33
Startup orientation: Portrait

[Show Advanced Settings] 클릭

=== Graphics ===
Graphics: Automatic (또는 Hardware - GLES 2.0)

=== Memory and Storage ===
RAM: 2048 MB (최소) ~ 4096 MB (권장)
VM heap: 256 MB
Internal Storage: 2048 MB
SD card: 512 MB

=== Camera ===
Front camera: Webcam0 ⚠️ 중요! (또는 Emulated)
Back camera: Webcam0 ⚠️ 중요! (또는 Emulated)

=== Network ===
Speed: Full
Latency: None

=== Emulated Performance ===
Boot option: Cold boot
Multi-Core CPU: 4 cores (Apple Silicon M1/M2/M3 성능 활용)

[Finish] 클릭
```

#### 시스템 이미지 선택 가이드

| 시스템 이미지 | ABI | Apple Silicon 지원 | 성능 | 카메라 지원 |
|-------------|-----|-------------------|------|-----------|
| arm64-v8a + Google Play | arm64 | ✅ 네이티브 (빠름) | ⭐⭐⭐⭐⭐ | ✅ Webcam/Emulated |
| arm64-v8a + Google APIs | arm64 | ✅ 네이티브 (빠름) | ⭐⭐⭐⭐⭐ | ✅ Webcam/Emulated |
| x86_64 + Google Play | x86_64 | ⚠️ 에뮬레이션 (느림) | ⭐⭐ | ✅ Webcam/VirtualScene |
| x86 | x86 | ❌ 지원 안 됨 | ❌ | ❌ |

**권장: arm64-v8a + Google Play (API 33)**

---

### 2.2 오디오 설정 (마이크 녹음)

#### Step 1: AVD 설정에서 마이크 활성화

```
Device Manager → Pixel_7_API_33 옆 ✏️ (Edit) 아이콘
→ [Show Advanced Settings]
→ Microphone 섹션:
   [Enable audio input] 체크
   또는
   드롭다운에서 "Virtual microphone uses host audio input" 선택

→ [Finish]
```

#### Step 2: macOS 마이크 권한 부여

```
macOS 설정:
시스템 설정 → 개인정보 보호 및 보안 → 마이크

"Android Studio" 또는 "qemu-system-aarch64" 찾기
→ 스위치 켜기 (활성화)

권한 부여 안 되어 있으면:
- 에뮬레이터에서 녹음 시도
- macOS 팝업: "qemu-system-aarch64가 마이크에 접근하려고 합니다"
- [허용] 클릭
```

#### Step 3: 에뮬레이터 재시작

```bash
# 설정 후 에뮬레이터 재시작 필수!
# Device Manager에서:
▶️ 버튼 클릭 → 에뮬레이터 부팅

# 또는 명령어:
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33
```

#### Step 4: 오디오 테스트

```
에뮬레이터 실행 후:
1. Flutter 앱 실행
2. 마이크 버튼 길게 누르기
3. Mac 마이크에 대고 말하기
4. 버튼 놓기
5. 오디오 파일 생성 확인

문제 발생 시:
- 에뮬레이터 설정에서 마이크 다시 활성화
- macOS 권한 재확인
- 에뮬레이터 cold boot (완전 재시작)
```

#### 오디오 품질 설정 (선택사항)

**Flutter 앱에서 16kHz 사용 (에뮬레이터 최적화):**

현재 `audio_service.dart`에서:
```dart
// 에뮬레이터 감지 후 샘플레이트 조정
final config = RecordConfig(
  encoder: AudioEncoder.aacLc,
  sampleRate: Platform.isAndroid ? 16000 : 44100, // Android 에뮬레이터는 16kHz
  bitRate: 128000,
);
```

**알려진 문제:**
- 44100Hz 샘플레이트는 macOS Android 에뮬레이터에서 불안정
- 16000Hz 사용 시 안정성 향상
- 실기기에서는 44100Hz 사용 가능

---

### 2.3 카메라 설정

#### Camera Mode 옵션

| 모드 | 설명 | 사용 사례 |
|------|------|----------|
| **None** | 카메라 없음 | 카메라 불필요한 앱 |
| **Emulated** | 소프트웨어 시뮬레이션 (테스트 패턴) | 기본 기능 테스트 |
| **Webcam0** | Mac 웹캠 사용 | 실제 카메라 피드 테스트 |
| **VirtualScene** | 가상 3D 환경 (AR용) | x86_64 이미지에서만 사용 가능 |

#### 권장 설정

```
Device Manager → Edit AVD → Show Advanced Settings

=== Camera ===
Front camera: Webcam0    ← Mac 내장 웹캠 (FaceTime 카메라)
Back camera: Webcam0     ← Mac 내장 웹캠

또는 (웹캠 없는 경우):
Front camera: Emulated
Back camera: Emulated
```

#### Webcam 사용 시 주의사항

1. **macOS 카메라 권한:**
   ```
   시스템 설정 → 개인정보 보호 및 보안 → 카메라
   → "qemu-system-aarch64" 활성화
   ```

2. **웹캠 해상도:**
   - Mac 웹캠이 1080p 이상이면 Flutter `camera` 패키지에서 자동 다운샘플링
   - 성능 문제 시 해상도 낮추기:
     ```dart
     ResolutionPreset.medium // 720p
     ResolutionPreset.low    // 480p
     ```

3. **멀티 카메라:**
   - Front/Back 모두 Webcam0로 설정 시 동일한 웹캠 사용
   - 실제 전면/후면 카메라 구분 불가
   - 앱 로직에서 처리 필요

#### Emulated 모드 (웹캠 없는 경우)

**표시되는 것:**
- 컬러 그리드 패턴
- 움직이는 정사각형
- 타임스탬프

**장점:**
- 웹캠 불필요
- 카메라 API 동작 테스트 가능
- 권한 처리 테스트 가능

**단점:**
- 실제 영상 처리 불가
- 얼굴 인식 등 테스트 불가

---

### 2.4 에뮬레이터 실행 및 앱 배포

#### 방법 1: Android Studio에서 실행 (GUI)

```
Device Manager → Pixel_7_API_33 옆 ▶️ 버튼 클릭

에뮬레이터 부팅 대기 (처음: 1-2분, 이후: 30초)
→ Android 홈 화면 표시
```

#### 방법 2: 명령어로 실행

```bash
# 사용 가능한 AVD 목록
~/Library/Android/sdk/emulator/emulator -list-avds

# 출력 예시:
# Pixel_7_API_33
# Pixel_6_API_31

# 특정 AVD 실행
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33

# 백그라운드로 실행
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33 &

# Cold boot (완전 재시작)
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33 -no-snapshot-load

# GPU 가속 활성화
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33 -gpu host
```

#### Flutter 앱 실행

```bash
cd /Users/kyungsbook/Desktop/myai/frontend

# 기기 확인
flutter devices
# 출력:
# sdk gphone64 arm64 (mobile) • emulator-5554 • android-arm64 • Android 13 (API 33)

# 앱 실행
flutter run -d emulator-5554

# 또는 자동 선택
flutter run
# "sdk gphone64 arm64" 선택
```

#### 앱 설치 확인

**에뮬레이터에서:**
```
1. 앱 아이콘이 홈 화면이나 앱 드로어에 표시됨
2. 앱 이름: "Eden" 또는 "frontend" (pubspec.yaml 설정에 따라)
```

**명령어로 확인:**
```bash
# 설치된 앱 목록
adb shell pm list packages | grep frontend

# 출력:
# package:com.example.frontend

# 앱 정보
adb shell dumpsys package com.example.frontend | grep version
```

---

### 2.5 Android 권한 관리

#### 자동 권한 부여 (테스트 편의)

```bash
# ADB 연결 확인
adb devices
# 출력:
# emulator-5554   device

# 카메라 권한 부여
adb shell pm grant com.example.frontend android.permission.CAMERA

# 마이크 권한 부여
adb shell pm grant com.example.frontend android.permission.RECORD_AUDIO

# 저장소 권한 (선택사항)
adb shell pm grant com.example.frontend android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant com.example.frontend android.permission.WRITE_EXTERNAL_STORAGE

# 모든 권한 확인
adb shell dumpsys package com.example.frontend | grep permission
```

#### 수동 권한 부여 (사용자 플로우 테스트)

```
앱 실행 후:
1. "Eden에서 카메라에 액세스하도록 허용하시겠습니까?" → [허용]
2. "Eden에서 마이크에 액세스하도록 허용하시겠습니까?" → [허용]

권한 거부 시 재요청:
설정 → 앱 → Eden → 권한
→ 카메라 [허용]
→ 마이크 [허용]
```

#### 권한 초기화 (재테스트용)

```bash
# 앱 데이터 및 권한 초기화
adb shell pm clear com.example.frontend

# 앱 재실행 시 권한 프롬프트 다시 표시됨
```

---

### 2.6 Android 테스트 명령어 모음

```bash
# === 에뮬레이터 관리 ===

# AVD 목록
~/Library/Android/sdk/emulator/emulator -list-avds

# 에뮬레이터 실행
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33

# 에뮬레이터 종료
adb -s emulator-5554 emu kill

# 모든 에뮬레이터 종료
killall qemu-system-aarch64

# === ADB 기본 명령 ===

# 연결된 기기 목록
adb devices

# 특정 기기에 명령 실행 (여러 기기 연결 시)
adb -s emulator-5554 shell <command>

# 에뮬레이터 재부팅
adb reboot

# === 앱 관리 ===

# APK 설치 (수동)
adb install app-release.apk

# 앱 제거
adb uninstall com.example.frontend

# 앱 데이터 초기화
adb shell pm clear com.example.frontend

# 앱 실행
adb shell am start -n com.example.frontend/.MainActivity

# 앱 강제 종료
adb shell am force-stop com.example.frontend

# === 권한 관리 ===

# 권한 부여
adb shell pm grant com.example.frontend android.permission.CAMERA
adb shell pm grant com.example.frontend android.permission.RECORD_AUDIO

# 권한 취소
adb shell pm revoke com.example.frontend android.permission.CAMERA

# 권한 목록
adb shell dumpsys package com.example.frontend | grep permission

# === 파일 전송 ===

# 에뮬레이터 → Mac
adb pull /sdcard/audio.m4a ~/Desktop/

# Mac → 에뮬레이터
adb push ~/Desktop/test.jpg /sdcard/

# === 로그 확인 ===

# 전체 로그
adb logcat

# Flutter 앱 로그만 필터링
adb logcat | grep flutter

# 에러만 표시
adb logcat *:E

# 로그 저장
adb logcat > android_log.txt

# === 스크린샷/녹화 ===

# 스크린샷
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# 화면 녹화 (최대 3분)
adb shell screenrecord /sdcard/recording.mp4
# Ctrl+C로 중단
adb pull /sdcard/recording.mp4

# === 성능 모니터링 ===

# CPU/메모리 사용량
adb shell top -n 1 | grep com.example.frontend

# 앱 메모리 사용량 상세
adb shell dumpsys meminfo com.example.frontend

# 배터리 사용량
adb shell dumpsys batterystats com.example.frontend
```

---

## Part 3: 오디오 기능 테스트

### 3.1 오디오 녹음 테스트

#### iOS (실기기 필수!)

**테스트 시나리오:**
```
1. 앱 실행 → 마이크 권한 허용
2. 푸시-투-톡 버튼 길게 누르기
3. iPhone 마이크에 대고 말하기: "안녕하세요, 오늘 날씨가 좋네요"
4. 버튼 놓기
5. 로딩 오버레이 표시 확인
6. 백엔드 응답 대기
7. TTS 재생 확인

예상 동작:
- 녹음 중: 버튼 애니메이션 (파동 효과)
- 녹음 완료: 파일 생성 (app_documents/audio.m4a)
- STT 변환: "안녕하세요, 오늘 날씨가 좋네요"
- 백엔드 처리 시간: 1-3초
```

**디버그 로그 확인:**
```dart
// frontend/lib/services/audio_service.dart
// Logger 출력:
🎙️ Recording started
🎙️ Recording stopped: /path/to/audio.m4a
🎙️ Audio duration: 3.2s
```

**알려진 문제:**
- ❌ iOS 시뮬레이터에서 녹음 실패 (iOS 15+ 버그)
- ✅ 실기기에서는 정상 작동

---

#### Android (에뮬레이터 가능)

**테스트 시나리오:**
```
1. 에뮬레이터 실행
2. macOS 마이크 권한 확인 (시스템 설정)
3. 앱 실행 → 마이크 권한 허용
4. 푸시-투-톡 버튼 길게 누르기
5. Mac 마이크에 대고 말하기
6. 버튼 놓기
7. 오디오 파일 생성 확인

예상 동작:
- 녹음 중: Mac 마이크 입력 감지 (시스템 트레이 아이콘)
- 녹음 완료: 파일 생성
- STT 변환: Groq Whisper로 텍스트 변환
```

**샘플레이트 확인:**
```dart
// 현재 설정 (audio_service.dart)
final config = RecordConfig(
  encoder: AudioEncoder.aacLc,
  sampleRate: 16000, // ⚠️ 에뮬레이터는 16kHz 권장
  bitRate: 128000,
);

// 실기기에서는 44100Hz 사용 가능
```

**문제 해결:**
```bash
# 문제: 녹음 시작 안 됨
# 해결:
1. 에뮬레이터 설정 → Virtual microphone 재확인
2. macOS 시스템 설정 → 마이크 권한 재확인
3. 에뮬레이터 재시작 (cold boot)

# 문제: 오디오에 잡음/끊김
# 해결:
1. 샘플레이트 16kHz로 변경
2. 에뮬레이터 RAM 4GB로 증가
3. Mac 시스템 리소스 확인 (Activity Monitor)

# 녹음 파일 확인
adb shell ls /data/data/com.example.frontend/cache/
adb pull /data/data/com.example.frontend/cache/audio.m4a ~/Desktop/
```

---

### 3.2 오디오 재생 테스트

#### iOS & Android (시뮬레이터/에뮬레이터 모두 가능)

**테스트 시나리오:**
```
1. 앱에서 AI 응답 수신
2. TTS 오디오 자동 재생
3. 응답 오버레이에 텍스트 표시
4. 재생 완료 후 오버레이 사라짐

TTS 소스:
- Backend: Edge TTS (Korean voices)
- Adam: ko-KR-InJoonNeural (남성)
- Eve: ko-KR-SunHiNeural (여성)
```

**볼륨 테스트:**
```
설정 화면 → TTS Volume 슬라이더
- 0.0 (음소거)
- 0.5 (중간)
- 1.0 (최대)

각 볼륨에서 재생 테스트
```

**재생 상태 확인:**
```dart
// frontend/lib/services/audio_service.dart
// Logger 출력:
🔊 Playing audio from base64
🔊 Audio playback completed
🔊 Audio playback error: ...
```

**문제 해결:**
```bash
# 문제: 오디오 재생 안 됨
# iOS:
- 물리적 볼륨 버튼 확인
- 무음 스위치 확인
- AirPods 연결 상태 확인

# Android:
- 에뮬레이터 볼륨 확인 (Settings → Sound)
- Mac 시스템 볼륨 확인
- 오디오 출력 장치 확인

# 문제: TTS 음질 나쁨
# 해결:
- Edge TTS는 고품질 (실기기에서 테스트 필요)
- 에뮬레이터/시뮬레이터는 스피커 품질 제한적
```

---

### 3.3 알려진 오디오 문제 및 해결책

| 문제 | 플랫폼 | 원인 | 해결책 |
|------|--------|------|--------|
| 녹음 실패 | iOS 시뮬레이터 | iOS 15+ 시뮬레이터 버그 | ✅ 실기기 사용 필수 |
| 녹음에 잡음 | Android 에뮬레이터 | 샘플레이트 불일치 | ✅ 16kHz로 변경 |
| 마이크 접근 안 됨 | Android 에뮬레이터 | macOS 권한 없음 | ✅ 시스템 설정에서 권한 부여 |
| 재생 안 됨 | 공통 | 볼륨 0 또는 음소거 | ✅ 볼륨 확인 |
| TTS 음질 나쁨 | 시뮬레이터/에뮬레이터 | 스피커 시뮬레이션 | ✅ 실기기에서 테스트 |
| 동시 녹음+재생 불가 | iOS 시뮬레이터 | AVAudioSession 제약 | ✅ 실기기 사용 |

---

## Part 4: 카메라 기능 테스트

### 4.1 카메라 프리뷰 테스트

#### iOS (실기기 필수!)

**테스트 시나리오:**
```
1. 앱 실행 → 카메라 권한 허용
2. 전체 화면에 카메라 프리뷰 표시
3. 전면/후면 카메라 전환 (있는 경우)
4. 프리뷰 해상도 확인
5. 조명 변화에 따른 자동 노출 확인

예상 동작:
- CameraController 초기화 성공
- 실시간 프리뷰 표시 (30 FPS)
- 화면 회전 시 프리뷰 자동 조정
```

**디버그 로그:**
```dart
// frontend/lib/services/camera_service.dart
📷 Camera initialized: back camera
📷 Available cameras: 2 (front, back)
📷 Preview resolution: 1920x1080
```

**알려진 문제:**
- ❌ iOS 시뮬레이터: `availableCameras()` 빈 배열 반환
- ❌ iOS 시뮬레이터: CameraController 초기화 실패
- ✅ 실기기: 정상 작동

---

#### Android (에뮬레이터 가능)

**테스트 시나리오 - Webcam 모드:**
```
1. AVD 설정: Camera Back = Webcam0
2. macOS 카메라 권한 허용
3. 에뮬레이터 실행
4. 앱 실행 → 카메라 권한 허용
5. Mac 웹캠 프리뷰 표시

예상 동작:
- Mac FaceTime 카메라 피드 표시
- 실시간 영상 처리 가능
- 손 또는 물체 인식 테스트 가능
```

**테스트 시나리오 - Emulated 모드:**
```
1. AVD 설정: Camera Back = Emulated
2. 에뮬레이터 실행
3. 앱 실행 → 카메라 권한 허용
4. 테스트 패턴 표시

표시되는 것:
- 컬러 그리드 (3D 큐브)
- 움직이는 정사각형
- 타임스탬프

용도:
- 카메라 API 동작 테스트
- 권한 처리 테스트
- UI 레이아웃 테스트
```

**카메라 목록 확인:**
```bash
# 에뮬레이터에서 사용 가능한 카메라
adb shell pm list features | grep camera

# 출력:
# feature:android.hardware.camera
# feature:android.hardware.camera.front
# feature:android.hardware.camera.autofocus
```

---

### 4.2 카메라 캡처 테스트 (1 FPS 키프레임)

#### 프로젝트 Eden의 카메라 캡처 로직

```dart
// frontend/lib/services/camera_service.dart

// 1초마다 프레임 캡처 (1 FPS)
Timer.periodic(Duration(seconds: 1), (timer) async {
  if (_isCapturing && _cameraController.value.isInitialized) {
    final image = await _cameraController.takePicture();
    _keyframes.add(image);

    if (_keyframes.length >= 8) {
      timer.cancel();
      _isCapturing = false;
    }
  }
});

// 결과: 8개 키프레임 (8초 분량)
```

**테스트 시나리오:**
```
1. 앱 실행 → 카메라 권한 허용
2. 푸시-투-톡 버튼 길게 누르기 (5-8초)
3. 버튼 누르는 동안 카메라 자동 캡처
4. 매 1초마다 키프레임 저장
5. 버튼 놓기 → 캡처 종료
6. 8개 키프레임 백엔드 전송

디버그 로그:
📷 Capturing keyframe 1/8
📷 Capturing keyframe 2/8
...
📷 Capturing keyframe 8/8
📷 Capture complete: 8 frames
```

**캡처 품질 확인:**
```bash
# Android: 캡처된 이미지 확인
adb shell ls /data/data/com.example.frontend/cache/camera/
adb pull /data/data/com.example.frontend/cache/camera/frame_001.jpg ~/Desktop/

# iOS: Xcode Devices & Simulators
# Devices → iPhone → Installed Apps → Eden → Download Container
# AppData/Library/Caches/camera/
```

**예상 결과:**
- 파일명: `frame_001.jpg`, `frame_002.jpg`, ..., `frame_008.jpg`
- 해상도: 1920x1080 (또는 설정된 해상도)
- 용량: ~100-300 KB/프레임 (JPEG 압축)
- 총 용량: ~800 KB - 2.4 MB (8 프레임)

---

### 4.3 알려진 카메라 문제 및 해결책

| 문제 | 플랫폼 | 원인 | 해결책 |
|------|--------|------|--------|
| 카메라 없음 | iOS 시뮬레이터 | 하드웨어 제약 | ✅ 실기기 사용 필수 |
| 프리뷰 느림 | Android 에뮬레이터 | 가상화 오버헤드 | ✅ Graphics: Hardware 설정 |
| Webcam 접근 안 됨 | Android 에뮬레이터 | macOS 권한 없음 | ✅ 시스템 설정에서 권한 부여 |
| 캡처 실패 | 공통 | 권한 없음 | ✅ 카메라 권한 재확인 |
| 캡처 느림 | Android 에뮬레이터 | 낮은 RAM | ✅ AVD RAM 4GB로 증가 |
| 이미지 품질 낮음 | Android 에뮬레이터 | Emulated 모드 | ✅ Webcam 모드 사용 |
| VirtualScene 없음 | Apple Silicon | arm64 미지원 | ℹ️ x86_64 이미지 사용 (느림) |

---

## Part 5: 권한 처리 테스트

### 5.1 권한 프롬프트 시나리오

#### 시나리오 1: 최초 실행 (권한 없음)

```
앱 최초 실행:

1. 앱 시작
2. PermissionScreen 표시
3. [카메라와 마이크 권한 허용하기] 버튼
4. 버튼 탭
5. iOS: 시스템 권한 다이얼로그 2개 (카메라, 마이크)
   Android: 시스템 권한 다이얼로그 2개
6. 각각 [허용] 탭
7. 권한 확인 후 VoiceFirstScreen으로 이동

예상 동작:
- permission_handler 패키지 사용
- 권한 상태: denied → granted
- 자동 화면 전환
```

#### 시나리오 2: 권한 거부

```
권한 거부 시:

1. 시스템 다이얼로그에서 [허용 안 함] 탭
2. PermissionScreen에 에러 메시지 표시:
   "카메라와 마이크 권한이 필요합니다"
3. [다시 시도] 버튼 표시
4. 다시 시도 → 권한 재요청

Android (2번 이상 거부 시):
- "다시 묻지 않음" 체크 가능
- 체크 시 권한 재요청 불가
- [설정으로 이동] 버튼 표시
```

#### 시나리오 3: 영구 거부 (Android)

```
Android 권한 영구 거부:

1. 권한 거부 + "다시 묻지 않음" 체크
2. 권한 재요청 시 다이얼로그 표시 안 됨
3. PermissionScreen에서:
   "설정에서 권한을 허용해주세요"
   [설정 열기] 버튼
4. 버튼 탭 → 앱 설정 화면으로 이동
5. 수동으로 권한 허용
6. 앱 재시작
```

#### 시나리오 4: 런타임 권한 취소

```
앱 사용 중 권한 취소:

1. 앱 실행 중 (VoiceFirstScreen)
2. iOS: 설정 → Eden → 카메라/마이크 끄기
   Android: 설정 → 앱 → Eden → 권한 → 거부
3. 앱으로 돌아오기
4. 카메라 프리뷰 중단
5. 푸시-투-톡 버튼 탭 시 에러 스낵바:
   "마이크 권한이 필요합니다"
6. [설정 열기] 액션 버튼
```

---

### 5.2 자동 권한 부여 (테스트/개발용)

#### iOS 시뮬레이터

```bash
# 앱 실행 전 권한 미리 부여
xcrun simctl boot "iPhone 16e"

# 카메라 권한 (작동은 안 하지만 프롬프트 생략 가능)
xcrun simctl privacy booted grant camera com.example.frontend

# 마이크 권한
xcrun simctl privacy booted grant microphone com.example.frontend

# 사진 라이브러리
xcrun simctl privacy booted grant photos com.example.frontend

# 모든 권한 부여
xcrun simctl privacy booted grant all com.example.frontend

# 앱 실행 → PermissionScreen 생략, 바로 VoiceFirstScreen
```

**권한 초기화 (재테스트):**
```bash
# 특정 권한 취소
xcrun simctl privacy booted revoke camera com.example.frontend

# 모든 권한 초기화
xcrun simctl privacy booted reset all

# 앱 데이터 초기화 (권한 포함)
xcrun simctl uninstall booted com.example.frontend
```

---

#### Android 에뮬레이터

```bash
# 에뮬레이터 실행 후
adb devices

# 카메라 권한 부여
adb shell pm grant com.example.frontend android.permission.CAMERA

# 마이크 권한 부여
adb shell pm grant com.example.frontend android.permission.RECORD_AUDIO

# 저장소 권한 (선택)
adb shell pm grant com.example.frontend android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant com.example.frontend android.permission.WRITE_EXTERNAL_STORAGE

# 위치 권한 (미래 기능용)
adb shell pm grant com.example.frontend android.permission.ACCESS_FINE_LOCATION

# 앱 실행 → PermissionScreen 생략
```

**권한 취소 (재테스트):**
```bash
# 특정 권한 취소
adb shell pm revoke com.example.frontend android.permission.CAMERA

# 앱 데이터 및 권한 초기화
adb shell pm clear com.example.frontend
```

**권한 상태 확인:**
```bash
# 모든 권한 목록
adb shell dumpsys package com.example.frontend | grep permission

# 특정 권한 상태
adb shell dumpsys package com.example.frontend | grep CAMERA
# 출력: granted=true 또는 granted=false
```

---

### 5.3 권한 처리 테스트 체크리스트

```
✅ 최초 실행 시 권한 프롬프트 표시
✅ 권한 허용 시 메인 화면으로 이동
✅ 권한 거부 시 에러 메시지 표시
✅ 권한 재요청 가능
✅ Android: "다시 묻지 않음" 처리
✅ 설정 화면으로 이동 버튼 작동
✅ 런타임 권한 취소 시 에러 처리
✅ 권한 복구 후 기능 재개
✅ 카메라만 허용 시 마이크 경고
✅ 마이크만 허용 시 카메라 경고
✅ 앱 재시작 시 권한 상태 유지
```

---

## Part 6: 멀티모달 플로우 테스트 (음성 + 카메라)

### 6.1 End-to-End 테스트 시나리오

#### 전체 플로우 (실기기 필수 - iOS)

```
=== Phase 1: 앱 시작 ===
1. 앱 실행
2. 권한 허용 (카메라 + 마이크)
3. 백엔드 연결 확인
4. VoiceFirstScreen 로드

예상 화면:
- 전체 화면 카메라 프리뷰
- 중앙 하단: 푸시-투-톡 버튼
- 상단: Adam/Eve 토글
- 왼쪽 상단: 프로필 아이콘
- 오른쪽 상단: 설정 아이콘

=== Phase 2: 대화 시작 ===
5. 푸시-투-톡 버튼 길게 누르기 (마이크 아이콘)
6. 버튼 애니메이션 시작 (파동 효과)
7. 카메라 자동 캡처 시작 (1 FPS)

예상 동작:
- 버튼 색상 변경: 파란색 → 빨간색
- 버튼 크기 증가
- 파동 애니메이션
- Logger: "Recording started"
- Logger: "Capturing keyframe 1/8"

=== Phase 3: 음성 입력 ===
8. iPhone 마이크에 대고 말하기:
   "안녕하세요, Adam. 오늘 SNU HCI Lab 지원서를 작성하고 있어요."

녹음 중 (5초):
- 매 1초마다 카메라 키프레임 캡처
- Logger: "Capturing keyframe 2/8", "3/8", ...
- 오디오 버퍼에 음성 저장

=== Phase 4: 전송 ===
9. 버튼 놓기
10. 버튼 애니메이션 종료
11. 로딩 오버레이 표시:
    "AI가 응답을 준비하고 있어요..."
12. 데이터 준비:
    - 오디오 파일: audio.m4a (~500 KB)
    - 키프레임: 5개 JPEG 이미지 (~1.5 MB)
13. 백엔드 전송:
    POST /api/v2/chat
    - user_id: test_user
    - audio: multipart/form-data
    - images: 5 frames
    - voice_type: adam

예상 로그:
Logger: "Recording stopped: 5.2s"
Logger: "Captured 5 keyframes"
Logger: "Sending to backend..."
Logger: "API call: POST /api/v2/chat"

=== Phase 5: 백엔드 처리 ===
14. 백엔드 수신 및 처리 (2-4초):
    a. STT: Groq Whisper로 음성 → 텍스트
    b. 키프레임 S3 업로드 (선택)
    c. 프로필 로드 (DynamoDB)
    d. Master Directive 실행:
       - 사용자 프로필 확인
       - One Thing: "SNU HCI Lab 진학"
       - Pitfall 체크: 지원서 작성 = 정렬됨 (0.9)
    e. Gemini LLM 응답 생성
    f. Edge TTS 생성 (Adam 음성)
    g. 프로필 업데이트 (learning service)

=== Phase 6: 응답 수신 ===
15. 백엔드 응답 수신:
    {
      "response_text": "좋아요! SNU HCI Lab 지원서 작성은...",
      "response_audio_base64": "<base64_mp3>",
      "pitfall_warning_triggered": false,
      "emotional_support_mode": false,
      "processing_time_ms": 2847
    }

16. 로딩 오버레이 숨김
17. 응답 오버레이 표시:
    - 글래스모피즘 배경
    - 응답 텍스트 표시
    - Adam 음성 TTS 자동 재생

=== Phase 7: 응답 재생 ===
18. TTS 오디오 재생 (10-20초)
19. 재생 중 텍스트 스크롤 가능
20. 재생 완료 후 오버레이 자동 사라짐 (3초 후)

=== Phase 8: 다음 대화 준비 ===
21. 다시 푸시-투-톡 버튼 활성화
22. 카메라 프리뷰 계속 표시
23. 다음 대화 준비 완료

전체 플로우 시간:
- 녹음: 5초
- 전송: 1초
- 백엔드 처리: 2-4초
- TTS 재생: 10-20초
- 총: ~20-30초
```

---

### 6.2 Pitfall Warning 트리거 테스트

```
=== Benevolent Dissent 시나리오 ===

사용자 프로필:
- One Thing: "SNU HCI Lab 진학"
- Core Pitfall: "능력 함정 - 에너지 분산"

테스트 입력:
"Adam, SLAM 알고리즘을 배우려고 하는데 어떻게 생각해?"

예상 동작:

1. 백엔드 Pitfall Detection:
   - Topic 추출: "SLAM algorithm"
   - Alignment 계산: 0.2 (약함)
   - Trigger 판단: True

2. 응답:
   {
     "response_text": "잠깐만요. SLAM은 흥미롭지만, 지금 SNU HCI Lab 준비와...",
     "pitfall_warning_triggered": true,
     "pitfall_message": "이 주제는 당신의 능력 함정 패턴으로 보입니다."
   }

3. 프론트엔드:
   - 응답 오버레이 표시
   - PitfallWarningBanner 상단에 표시 (노란색):
     "⚠️ 이 주제는 당신의 능력 함정 패턴으로 보입니다."
   - TTS 재생: 경고 톤
   - 배너 10초 후 자동 사라짐

4. 사용자 액션:
   - 배너 탭 → 프로필 화면으로 이동
   - Core Pitfall 설명 확인
```

---

### 6.3 Emotional Support Mode 테스트

```
=== Supporter Mode 시나리오 ===

테스트 입력 (우울한 톤):
"Adam... 오늘 모의면접에서 완전히 망했어요. 아무것도 제대로 대답 못 했어요."

예상 동작:

1. 백엔드 Emotional Detection:
   - 키워드 감지: "망했어요", "못 했어요"
   - 감정 상태: 좌절, 불안
   - Mode 전환: Supporter

2. 응답:
   {
     "response_text": "힘들었겠어요. 하지만 모의면접은 연습이에요...",
     "emotional_support_mode": true,
     "pitfall_warning_triggered": false
   }

3. 프론트엔드:
   - 응답 오버레이 배경색 변화 (따뜻한 색조)
   - TTS 톤: 부드럽고 공감적
   - 아이콘: 💚 표시

4. 응답 특징:
   - 판단하지 않음
   - 공감 우선
   - 격려 메시지
   - One Thing 상기시킴
```

---

### 6.4 멀티모달 테스트 디바이스 매트릭스

| 기기 | 음성 녹음 | 카메라 캡처 | 동시 처리 | 백엔드 전송 | TTS 재생 | 전체 플로우 |
|------|----------|-----------|----------|------------|---------|-----------|
| **iOS Simulator** | ❌ | ❌ | ❌ | ⚠️ | ✅ | ❌ |
| **iOS Device** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Android Emulator** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Android Device** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**결론:**
- iOS는 실기기 필수
- Android는 에뮬레이터로 전체 플로우 테스트 가능
- 성능 테스트는 실기기 권장

---

## Part 7: 문제 해결 (Troubleshooting)

### 7.1 iOS 관련 문제

#### 문제 1: "No cameras available"

**증상:**
```dart
Logger: Available cameras: 0
Error: No cameras available on this device
```

**원인:**
- iOS 시뮬레이터 사용 중

**해결책:**
```bash
# ✅ 실물 iPhone/iPad 사용
flutter devices
# iPhone 선택
flutter run -d <iphone-device-id>
```

---

#### 문제 2: "Audio recording failed"

**증상:**
```dart
Logger: Recording started
Error: Recording failed: PlatformException
```

**원인:**
- iOS 시뮬레이터 사용 (iOS 15+ 알려진 버그)

**해결책:**
```bash
# ✅ 실물 iPhone 사용 필수
# 또는 Mock 서비스 구현 (테스트용)

# 시뮬레이터에서 임시 우회 (개발 중):
# audio_service.dart에 조건 추가
if (Platform.isIOS && _isSimulator()) {
  // Mock audio file 반환
  return _loadMockAudio();
}
```

---

#### 문제 3: "Permission denied"

**증상:**
```
User denied camera permission
User denied microphone permission
```

**원인:**
- Info.plist에 usage description 누락
- 사용자가 권한 거부

**해결책:**
```bash
# 1. Info.plist 확인
cat ios/Runner/Info.plist | grep Usage

# 출력 확인:
# <key>NSCameraUsageDescription</key>
# <key>NSMicrophoneUsageDescription</key>

# 2. 없으면 추가 (이미 있음)
# frontend/ios/Runner/Info.plist 수정

# 3. 권한 재요청
# 앱 삭제 후 재설치
flutter clean
flutter run

# 4. 시뮬레이터 권한 강제 부여
xcrun simctl privacy booted grant camera com.example.frontend
xcrun simctl privacy booted grant microphone com.example.frontend
```

---

#### 문제 4: "Device not trusted"

**증상:**
```
Could not find any available devices
```

**원인:**
- iPhone이 Mac을 신뢰하지 않음

**해결책:**
```
1. iPhone에서:
   - USB 연결 시 "이 컴퓨터를 신뢰하시겠습니까?" → [신뢰]
   - iPhone 암호 입력

2. Mac에서:
   - Xcode → Window → Devices and Simulators
   - iPhone 연결 상태 확인

3. 개발자 모드 활성화 (iOS 16+):
   - 설정 → 개인정보 보호 및 보안 → 개발자 모드 → 켜기
   - iPhone 재시동
```

---

#### 문제 5: "Code signing error"

**증상:**
```
error: Signing for "Runner" requires a development team.
```

**원인:**
- Xcode에서 개발 팀 미설정

**해결책:**
```bash
# 1. Xcode에서 자동 서명 설정
open ios/Runner.xcworkspace

# Xcode:
# Runner 프로젝트 선택 → Signing & Capabilities
# Team: [자신의 Apple ID 선택]
# Automatically manage signing: ✅ 체크

# 2. 또는 명령어로
cd ios
pod install
cd ..
flutter clean
flutter pub get
flutter run
```

---

### 7.2 Android 관련 문제

#### 문제 1: "Audio recording fails" (에뮬레이터)

**증상:**
```dart
Logger: Recording started
Error: Failed to start recording
```

**원인:**
- Virtual microphone 비활성화
- macOS 마이크 권한 없음

**해결책:**
```bash
# 1. AVD 설정 확인
# Device Manager → Edit AVD → Advanced Settings
# Microphone: Enable audio input ✅

# 2. macOS 권한 확인
# 시스템 설정 → 개인정보 보호 및 보안 → 마이크
# "qemu-system-aarch64" 또는 "Android Studio" 활성화

# 3. 에뮬레이터 재시작 (cold boot)
adb -s emulator-5554 emu kill
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33 -no-snapshot-load

# 4. 샘플레이트 변경 (audio_service.dart)
sampleRate: 16000 // 44100 대신 16kHz 사용
```

---

#### 문제 2: "Audio has static/noise"

**증상:**
- 녹음 파일에 잡음 심함
- 재생 시 끊김 또는 디스토션

**원인:**
- 높은 샘플레이트 (44100Hz)
- 에뮬레이터 리소스 부족

**해결책:**
```dart
// frontend/lib/services/audio_service.dart
final config = RecordConfig(
  encoder: AudioEncoder.aacLc,
  sampleRate: 16000, // ← 16kHz로 변경
  bitRate: 64000,     // ← 비트레이트 낮춤
);

// AVD RAM 증가
// Device Manager → Edit → RAM: 4096 MB
```

---

#### 문제 3: "Camera not available"

**증상:**
```dart
Logger: Available cameras: 0
```

**원인:**
- AVD 카메라 설정 안 됨

**해결책:**
```bash
# 1. AVD 설정 확인
# Device Manager → Edit AVD → Advanced Settings
# Camera Front: Webcam0 (또는 Emulated)
# Camera Back: Webcam0 (또는 Emulated)

# 2. macOS 카메라 권한 확인 (Webcam 사용 시)
# 시스템 설정 → 개인정보 보호 및 보안 → 카메라
# "qemu-system-aarch64" 활성화

# 3. 에뮬레이터 재시작
```

---

#### 문제 4: "Emulator is slow"

**증상:**
- 에뮬레이터 부팅 느림 (5분+)
- 앱 실행 느림
- UI 버벅임

**원인:**
- x86_64 이미지 사용 (Apple Silicon에서 비효율적)
- 낮은 RAM/CPU 할당

**해결책:**
```bash
# 1. ARM64 이미지 사용 (필수!)
# Device Manager → Create Device
# System Image: arm64-v8a (NOT x86_64)

# 2. Hardware acceleration 활성화
# AVD Settings:
# Graphics: Hardware - GLES 2.0
# Multi-Core CPU: 4 cores

# 3. RAM 증가
# AVD Settings:
# RAM: 4096 MB
# VM heap: 512 MB

# 4. Snapshot 사용
# AVD Settings:
# Boot option: Quick boot
# (최초 부팅 후 상태 저장)
```

---

#### 문제 5: "Build fails: SDK not found"

**증상:**
```
Android SDK not found. Define location with sdk.dir...
```

**원인:**
- Android SDK 경로 설정 안 됨

**해결책:**
```bash
# 1. Android SDK 경로 확인
~/Library/Android/sdk

# 2. local.properties 생성 (없으면)
echo "sdk.dir=$HOME/Library/Android/sdk" > android/local.properties

# 3. Flutter 재설정
flutter clean
flutter pub get
flutter doctor --android-licenses

# 4. 빌드 재시도
flutter run
```

---

### 7.3 Flutter 관련 문제

#### 문제 1: "flutter run fails"

**증상:**
```bash
$ flutter run
No devices found
```

**해결책:**
```bash
# 1. 기기 연결 확인
flutter devices

# 출력 없으면:
# - iOS: 시뮬레이터 부팅 또는 iPhone 연결
# - Android: 에뮬레이터 실행

# 2. Doctor 실행
flutter doctor -v

# 문제 있는 항목 수정

# 3. Flutter 캐시 재구성
flutter clean
rm -rf build/
flutter pub get
flutter run
```

---

#### 문제 2: "Hot reload not working"

**증상:**
- 코드 수정 후 `r` 눌러도 변경사항 반영 안 됨

**해결책:**
```bash
# 1. Hot restart 시도
# 터미널에서: R (대문자)

# 2. 앱 재시작
# 터미널에서: q (종료)
flutter run

# 3. 빌드 정리
flutter clean
flutter run

# 4. 특정 파일은 hot reload 불가:
# - main.dart
# - pubspec.yaml
# - native code (iOS/Android)
# → 앱 재시작 필요
```

---

#### 문제 3: "Build fails after pub get"

**증상:**
```
Error: Could not resolve package dependencies
```

**해결책:**
```bash
# 1. 캐시 정리
flutter clean
rm -rf pubspec.lock
rm -rf ~/.pub-cache/hosted/pub.dartlang.org/

# 2. 의존성 재설치
flutter pub get

# 3. 버전 충돌 확인
flutter pub outdated

# 4. 특정 패키지 버전 고정
# pubspec.yaml:
# record: 6.1.2 (^6.1.2 대신)
```

---

#### 문제 4: "Permission denied errors"

**증상:**
```dart
PlatformException(PermissionHandler.PermissionRequestDenied)
```

**해결책:**
```bash
# 1. 권한 상태 확인
# iOS:
xcrun simctl privacy booted list

# Android:
adb shell dumpsys package com.example.frontend | grep permission

# 2. 앱 데이터 초기화
# iOS:
xcrun simctl uninstall booted com.example.frontend

# Android:
adb shell pm clear com.example.frontend

# 3. 앱 재설치
flutter run
```

---

#### 문제 5: "Camera/Audio packages not working"

**증상:**
```dart
MissingPluginException(No implementation found for method...)
```

**원인:**
- Native plugin 빌드 안 됨

**해결책:**
```bash
# 1. Pod 재설치 (iOS)
cd ios
rm -rf Pods/ Podfile.lock
pod install --repo-update
cd ..

# 2. Gradle 캐시 정리 (Android)
cd android
./gradlew clean
cd ..

# 3. Flutter 재빌드
flutter clean
flutter pub get
flutter run

# 4. 여전히 안 되면 패키지 버전 확인
flutter pub outdated
# 최신 버전으로 업그레이드
```

---

## Part 8: 권장 테스트 워크플로우

### 8.1 일일 개발 워크플로우

```
=== 매일 반복 작업 ===

1. Android 에뮬레이터 실행 (1분)
   ~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33 &

2. 백엔드 서버 실행 (30초)
   cd backend
   ./start_local.sh

3. Flutter 앱 실행 (1분)
   cd frontend
   flutter run

4. 기능 개발 및 테스트
   - 코드 수정
   - Hot reload (r)
   - UI 확인
   - Android 에뮬레이터에서 음성/카메라 테스트

5. 로그 확인
   flutter logs | grep -E "Logger|Error"

6. 주기적으로 iOS 시뮬레이터도 확인 (UI만)
   open -a Simulator
   flutter run
   # UI 레이아웃, 네비게이션만 테스트

총 소요 시간: ~3분
```

**권장 사항:**
- **주요 개발**: Android 에뮬레이터 (음성+카메라 가능)
- **UI 확인**: iOS 시뮬레이터 (빠름)
- **실기기 테스트**: 주 1-2회

---

### 8.2 주간 검증 워크플로우

```
=== 매주 금요일 (2시간) ===

1. 전체 기능 테스트 - Android 에뮬레이터 (30분)
   ✅ 음성 녹음 (5회)
   ✅ 카메라 캡처 (3회)
   ✅ 멀티모달 플로우 (3회)
   ✅ 페르소나 전환 (Adam ↔ Eve)
   ✅ 프로필 화면
   ✅ 설정 화면
   ✅ Pitfall warning 트리거
   ✅ Emotional support mode

2. 전체 기능 테스트 - iOS 실기기 (30분)
   ✅ 동일한 테스트 시나리오
   ✅ iOS 특화 기능 확인

3. 크로스 플랫폼 비교 (20분)
   - UI 차이점 확인
   - 성능 차이 측정
   - 버그 리스트 작성

4. 회귀 테스트 (40분)
   - 이전에 수정한 버그 재확인
   - 새 기능이 기존 기능에 영향 없는지 확인
   - 엣지 케이스 테스트:
     * 네트워크 끊김
     * 권한 취소
     * 빠른 버튼 연타
     * 백엔드 에러 응답
```

---

### 8.3 릴리스 전 워크플로우 (QA)

```
=== 출시 2주 전 (1주일 집중 테스트) ===

Day 1-2: 기능 테스트 (모든 기기)
  ✅ iOS Simulator: UI/네비게이션만
  ✅ Android Emulator: 전체 기능
  ✅ iPhone (실기기): 전체 기능
  ✅ Android (실기기): 전체 기능

Day 3: 성능 테스트
  ✅ 앱 시작 시간 측정
  ✅ 메모리 사용량 모니터링
  ✅ 배터리 소모 테스트
  ✅ 네트워크 사용량 측정
  ✅ 카메라 1 FPS 캡처 성능

Day 4: 호환성 테스트
  ✅ iOS 15, 16, 17
  ✅ Android 11, 12, 13
  ✅ iPhone SE, 13, 14, 15
  ✅ 다양한 Android 기기 (Pixel, Samsung)

Day 5: 엣지 케이스 및 에러 처리
  ✅ 네트워크 불안정
  ✅ 백엔드 다운
  ✅ 권한 런타임 취소
  ✅ 디스크 공간 부족
  ✅ 메모리 부족
  ✅ 빠른 입력 (버튼 연타)
  ✅ 긴 오디오 (30초+)
  ✅ 많은 키프레임 (20개+)

Day 6-7: 사용자 시나리오 테스트
  ✅ 최초 사용자 플로우
  ✅ 반복 사용자 플로우
  ✅ 다양한 대화 주제
  ✅ Pitfall 트리거 시나리오 10개
  ✅ 감정적 지원 시나리오 5개
  ✅ 프로필 성장 시뮬레이션 (50회 대화)
```

**릴리스 체크리스트:**
```
✅ flutter analyze: 0 errors, 0 warnings
✅ flutter test: All tests pass
✅ 모든 권한 프롬프트 정상 작동
✅ TTS 음성 품질 확인
✅ 카메라 화질 확인
✅ 앱 아이콘 및 스플래시 화면
✅ App Store/Play Store 스크린샷
✅ 개인정보 처리방침
✅ 이용약관
✅ 백엔드 프로덕션 배포 완료
✅ API rate limiting 설정
✅ 에러 모니터링 (Sentry/Firebase)
```

---

### 8.4 기기별 테스트 우선순위

#### 높은 우선순위 (매일)

1. **Android 에뮬레이터** (Pixel 7, arm64-v8a, API 33)
   - 이유: 전체 기능 테스트 가능
   - 용도: 일일 개발 및 빠른 검증

2. **iOS 시뮬레이터** (iPhone 15 Pro, iOS 17)
   - 이유: UI/UX 빠른 확인
   - 용도: 레이아웃, 네비게이션, 시각적 요소

#### 중간 우선순위 (주 1-2회)

3. **iPhone (실기기)** (iPhone 13+)
   - 이유: iOS 전체 기능 테스트
   - 용도: 음성, 카메라, 성능 검증

#### 낮은 우선순위 (월 1-2회 또는 릴리스 전)

4. **Android (실기기)** (Pixel 6+)
   - 이유: Android 에뮬레이터가 대부분 커버
   - 용도: 최종 성능 및 하드웨어 호환성

5. **다양한 iOS 기기** (iPad, iPhone SE, 구형 모델)
   - 이유: 호환성 확인
   - 용도: 릴리스 전 QA

6. **다양한 Android 기기** (Samsung, Xiaomi 등)
   - 이유: 제조사별 차이 확인
   - 용도: 릴리스 전 QA

---

### 8.5 CI/CD 파이프라인에서 시뮬레이터 활용

```yaml
# .github/workflows/flutter_test.yml (예시)

name: Flutter Test

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest  # Apple Silicon 또는 Intel
    steps:
      - uses: actions/checkout@v3

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.35.7'

      - name: Install dependencies
        run: |
          cd frontend
          flutter pub get

      - name: Run analyzer
        run: |
          cd frontend
          flutter analyze

      - name: Run unit tests
        run: |
          cd frontend
          flutter test

      - name: Run integration tests (iOS Simulator)
        run: |
          cd frontend
          # iOS 시뮬레이터에서 UI 테스트만
          xcrun simctl boot "iPhone 15 Pro"
          flutter test integration_test/ui_test.dart
          # ❌ 음성/카메라 테스트 제외

      - name: Run integration tests (Android Emulator)
        run: |
          # Android 에뮬레이터 설정 (x86_64 for CI)
          echo "y" | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager \
            "system-images;android-30;google_apis;x86_64"

          $ANDROID_HOME/emulator/emulator -avd test_avd -no-window -no-audio &
          adb wait-for-device

          cd frontend
          flutter test integration_test/full_test.dart
          # ✅ 전체 기능 테스트 (mock 서비스)

  # 실기기 테스트는 수동 또는 별도 파이프라인
```

**CI/CD 전략:**
- **자동 테스트**: 시뮬레이터/에뮬레이터 (UI, 로직, mock 서비스)
- **수동 테스트**: 실기기 (음성, 카메라, 성능)
- **릴리스 게이트**: 수동 실기기 테스트 통과 필수

---

## 🎯 요약 및 권장사항

### 최종 권장 사항

#### ✅ DO (해야 할 것)

1. **Android 에뮬레이터를 주요 개발 환경으로 사용**
   - ARM64 이미지 (Apple Silicon 최적화)
   - Webcam + Virtual microphone 설정
   - 매일 사용하여 빠른 반복 개발

2. **iOS 실물 기기 반드시 준비**
   - iPhone 13 이상 또는 iPhone SE 3세대
   - 주 1-2회 전체 기능 테스트
   - 릴리스 전 필수 검증

3. **iOS 시뮬레이터는 UI 확인용으로만 사용**
   - 레이아웃, 네비게이션, 색상 등
   - 음성/카메라 기능은 테스트 불가

4. **체계적인 테스트 워크플로우 구축**
   - 일일: Android 에뮬레이터
   - 주간: iOS 실기기
   - 릴리스 전: 모든 기기

---

#### ❌ DON'T (하지 말아야 할 것)

1. **iOS 시뮬레이터에서 음성/카메라 테스트 시도**
   - 시간 낭비 (작동 안 함)
   - 실기기 사용 필수

2. **Android x86_64 이미지 사용 (Apple Silicon에서)**
   - 느리고 비효율적
   - ARM64 이미지 사용

3. **에뮬레이터 성능을 실기기 성능으로 착각**
   - 에뮬레이터는 느림
   - 성능 측정은 실기기에서

4. **권한 자동 부여만 사용**
   - 사용자 플로우도 테스트 필요
   - 권한 거부 시나리오 확인

---

### 예산별 권장 사항

#### 최소 예산 (~$400)

```
필수:
✅ iPhone SE 3세대 (~$429)
   - iOS 전체 기능 테스트
   - 음성 + 카메라

✅ Android 에뮬레이터 (무료)
   - 일일 개발
   - 빠른 검증

총: ~$430

이것만으로도 충분히 개발 및 테스트 가능!
```

#### 권장 예산 (~$800)

```
권장:
✅ iPhone 13 (~$500 중고)
   - 더 나은 카메라
   - 더 빠른 성능

✅ Android 에뮬레이터 (무료)

✅ Pixel 6a (~$300 중고, 선택)
   - Android 실기기 테스트
   - 제조사별 차이 확인

총: ~$500-800
```

#### 이상적인 예산 (~$1,500)

```
이상적:
✅ iPhone 15 Pro (~$999)
   - 최신 기능
   - 최고 성능

✅ Android 에뮬레이터 (무료)

✅ Pixel 7 (~$599)
   - 최신 Android 테스트

✅ iPad Pro (~$799, 선택)
   - 태블릿 레이아웃 테스트

총: ~$1,600-2,400
```

---

### 빠른 참조 명령어 모음

```bash
# === iOS ===

# 시뮬레이터 실행
open -a Simulator

# 기기 목록
flutter devices

# 앱 실행 (시뮬레이터)
flutter run

# 앱 실행 (실기기)
flutter run -d <iphone-device-id>

# 권한 부여 (시뮬레이터)
xcrun simctl privacy booted grant camera com.example.frontend
xcrun simctl privacy booted grant microphone com.example.frontend

# === Android ===

# 에뮬레이터 실행
~/Library/Android/sdk/emulator/emulator -avd Pixel_7_API_33

# 기기 목록
adb devices

# 앱 실행
flutter run

# 권한 부여
adb shell pm grant com.example.frontend android.permission.CAMERA
adb shell pm grant com.example.frontend android.permission.RECORD_AUDIO

# 로그 확인
adb logcat | grep flutter

# === Flutter ===

# 의존성 설치
flutter pub get

# 분석
flutter analyze

# 테스트
flutter test

# 빌드 정리
flutter clean

# Hot reload
r

# Hot restart
R

# 종료
q
```

---

## 📚 추가 리소스

### 공식 문서

- **Flutter**: https://docs.flutter.dev/testing
- **iOS Simulator**: https://developer.apple.com/documentation/xcode/running-your-app-in-simulator
- **Android Emulator**: https://developer.android.com/studio/run/emulator

### 프로젝트 문서

- **README.md**: 프로젝트 개요
- **DEPLOYMENT.md**: 배포 가이드 (6,000+ 단어)
- **docs/archive/**: Phase별 구현 문서

### 유용한 명령어 치트시트

```bash
# 이 가이드를 PDF로 변환 (선택)
pandoc SIMULATOR_TESTING.md -o SIMULATOR_TESTING.pdf

# 또는 Markdown 뷰어에서 읽기
# VS Code, Typora, MacDown 등
```

---

## 🤝 도움이 필요하신가요?

이 가이드를 따라 문제가 해결되지 않으면:

1. **Flutter Doctor 실행**:
   ```bash
   flutter doctor -v
   ```
   모든 항목이 ✅ 인지 확인

2. **로그 확인**:
   ```bash
   flutter logs > flutter_log.txt
   adb logcat > android_log.txt
   ```

3. **버전 확인**:
   ```bash
   flutter --version
   xcodebuild -version
   ~/Library/Android/sdk/emulator/emulator -version
   ```

---

---

## 📱 Part 9: 실제 기기 테스트 (iPhone & Galaxy)

### 왜 실제 기기 테스트가 필요한가?

**시뮬레이터/에뮬레이터의 한계:**
- iOS 시뮬레이터: 음성 녹음/카메라 작동 안 함
- Android 에뮬레이터: 성능/하드웨어 정확도 낮음
- 실제 사용자 경험과 차이 있음

**실제 기기에서만 테스트 가능:**
- ✅ 실제 마이크 녹음 품질
- ✅ 실제 카메라 화질 및 성능
- ✅ 배터리 소모
- ✅ 네트워크 환경 (LTE/5G/Wi-Fi)
- ✅ 실제 하드웨어 성능
- ✅ 제조사별 차이점 (Samsung, Apple)

---

### 9.1 iPhone 실제 기기 테스트 (USB 연결)

#### 준비물

```
하드웨어:
✅ iPhone 13 이상 또는 iPhone SE 3세대
✅ USB-C to Lightning 케이블 (또는 USB-C to USB-C for iPhone 15+)
✅ Mac (Apple Silicon 또는 Intel)

소프트웨어:
✅ Xcode 15+ 설치됨
✅ iOS 15+ (iPhone)
✅ Flutter 3.35.7+
```

---

#### Step 1: iPhone 준비 및 연결

**1.1 개발자 모드 활성화 (iOS 16+ 필수)**

```
iPhone에서:
1. 설정 앱 열기
2. 개인정보 보호 및 보안 → 개발자 모드
3. 개발자 모드 스위치 켜기
4. iPhone 재시동 (자동 프롬프트)
5. 재시동 후 "개발자 모드 켜기" 다시 확인
6. iPhone 암호 입력하여 확인
```

**iOS 15 이하:**
- 개발자 모드 설정 불필요
- USB 연결 후 바로 신뢰 가능

---

**1.2 USB 케이블로 Mac 연결**

```
1. iPhone을 USB 케이블로 Mac에 연결

2. iPhone에 팝업 표시:
   "이 컴퓨터를 신뢰하시겠습니까?"

3. [신뢰] 탭

4. iPhone 암호(또는 Face ID/Touch ID) 입력

5. Mac에서 확인:
```

```bash
# 터미널에서 확인
flutter devices

# 출력 예시:
# iPhone 15 Pro (mobile) • 00008030-001A2B3C4D5E001F • ios • iOS 17.0.1
```

---

**1.3 Xcode에서 기기 확인 (선택사항)**

```bash
# Xcode 열기
open -a Xcode

# 또는 메뉴:
# Xcode → Window → Devices and Simulators (⌘ + Shift + 2)
```

**Devices 탭에서 확인:**
```
왼쪽 사이드바:
✅ iPhone 15 Pro
   - iOS 17.0.1
   - Identifier: 00008030-001A2B3C4D5E001F
   - Status: Connected (초록색 점)

문제 발생 시:
⚠️ Status: Unavailable
   → iPhone 잠금 해제
   → "신뢰" 재확인
   → 케이블 재연결
```

---

#### Step 2: Flutter 앱 배포 및 실행

**2.1 기기 ID 확인**

```bash
cd /Users/kyungsbook/Desktop/myai/frontend

# 연결된 기기 목록
flutter devices

# 출력:
# 3 connected devices:
#
# iPhone 15 Pro (mobile) • 00008030-001A2B3C4D5E001F • ios • iOS 17.0.1
# iPhone 16e (mobile)    • AF123456-7890-ABCD-EF12-34567890ABCD • ios • com.apple.CoreSimulator.SimRuntime.iOS-17-0 (simulator)
# sdk gphone64 arm64 (mobile) • emulator-5554 • android-arm64 • Android 13 (API 33) (emulator)
```

**실제 iPhone 구분:**
- `(mobile)` + `ios` + `iOS 17.0.1` (시뮬레이터 아님)
- Device ID: 실제 하드웨어 UUID (00008030-...)

---

**2.2 앱 실행**

```bash
# 방법 1: Device ID로 직접 실행 (추천)
flutter run -d 00008030-001A2B3C4D5E001F

# 방법 2: flutter run 후 선택
flutter run

# 프롬프트:
# Multiple devices found:
# [1]: iPhone 15 Pro (00008030-001A2B3C4D5E001F)
# [2]: iPhone 16e (simulator)
# [3]: sdk gphone64 arm64 (emulator)
# Please choose one (or "q" to quit): 1

# 빌드 시작 (최초 2-3분 소요)
```

**빌드 과정:**
```
Launching lib/main.dart on iPhone 15 Pro in debug mode...
Running pod install...                                      2,341ms
Running Xcode build...
 └─Compiling, linking and signing...                      45.3s
Xcode build done.                                          48.2s
Syncing files to device iPhone 15 Pro...                   234ms

Flutter run key commands.
r Hot reload. 🔥🔥🔥
R Hot restart.
h List all available interactive commands.
d Detach (terminate "flutter run" but leave application running).
c Clear the screen
q Quit (terminate the application on the device).

A Dart VM Service on iPhone 15 Pro is available at:
http://127.0.0.1:50123/abc123def456/
```

---

**2.3 앱 설치 확인**

**iPhone 홈 화면에서:**
```
1. 앱 아이콘 확인:
   - 이름: "Eden" (또는 "frontend")
   - 기본 Flutter 아이콘 또는 커스텀 아이콘

2. 앱 탭하여 실행 가능
   - Hot reload 중이면 터미널 연결 유지
   - Hot reload 종료 후에도 앱 독립 실행 가능
```

**설정에서 확인:**
```
iPhone 설정 → 일반 → VPN 및 기기 관리 (또는 프로파일 및 기기 관리)
→ 개발자 앱 섹션
→ [Apple ID 이메일] 확인
→ Eden 앱 나열됨
```

---

#### Step 3: 권한 부여 및 테스트

**3.1 최초 실행 시 권한 프롬프트**

```
앱 실행 순서:

1. 앱 시작 → PermissionScreen 표시

2. [카메라와 마이크 권한 허용하기] 버튼 탭

3. 시스템 권한 다이얼로그 (순차적):

   첫 번째 다이얼로그:
   "Eden"이(가) 카메라에 접근하려고 합니다
   [ 허용 안 함 ]  [ 확인 ]
   → [확인] 탭

   두 번째 다이얼로그:
   "Eden"이(가) 마이크에 접근하려고 합니다
   [ 허용 안 함 ]  [ 확인 ]
   → [확인] 탭

4. 권한 부여 완료 → VoiceFirstScreen으로 자동 이동
```

---

**3.2 전체 멀티모달 플로우 테스트**

```
=== 완전한 End-to-End 테스트 ===

1. VoiceFirstScreen 확인:
   ✅ 전체 화면 카메라 프리뷰 (실제 iPhone 후면 카메라)
   ✅ 중앙 하단: 푸시-투-톡 버튼 (파란색 마이크)
   ✅ 상단: Adam/Eve 토글
   ✅ 왼쪽 상단: 프로필 아이콘 (👤)
   ✅ 오른쪽 상단: 설정 아이콘 (⚙️)

2. 백엔드 서버 실행 확인:
   터미널 새 탭:
   cd /Users/kyungsbook/Desktop/myai/backend
   ./start_local.sh

   확인:
   ✅ Backend server started successfully!
   ✅ Server: http://192.168.1.100:8000

3. iPhone에서 마이크 버튼 길게 누르기:
   ✅ 버튼 색상: 파란색 → 빨간색
   ✅ 버튼 크기 증가
   ✅ 파동 애니메이션 시작
   ✅ 카메라 1 FPS 자동 캡처 시작

4. iPhone 마이크에 대고 말하기 (5-8초):
   "안녕하세요, Adam. 오늘 SNU HCI Lab 연구 계획서를 작성하고 있어요."

   진행 상황:
   ✅ 매 1초마다 키프레임 캡처 (최대 8개)
   ✅ 오디오 녹음 중
   ✅ Logger: "Capturing keyframe 1/8", "2/8", ...

5. 버튼 놓기:
   ✅ 녹음 종료
   ✅ 로딩 오버레이 표시: "AI가 응답을 준비하고 있어요..."
   ✅ 백엔드 전송 (오디오 + 키프레임)

6. 백엔드 처리 (2-4초):
   ✅ STT: Groq Whisper (음성 → 텍스트)
   ✅ 프로필 로드
   ✅ Master Directive 실행
   ✅ Gemini LLM 응답 생성
   ✅ Edge TTS 생성 (Adam 음성)

7. 응답 수신:
   ✅ 로딩 오버레이 숨김
   ✅ 응답 오버레이 표시 (글래스모피즘)
   ✅ 응답 텍스트: "좋아요! SNU HCI Lab 연구 계획서 작성은..."
   ✅ TTS 자동 재생 (Adam 남성 목소리)

8. TTS 재생 중 (10-20초):
   ✅ iPhone 스피커로 음성 출력
   ✅ 텍스트 스크롤 가능
   ✅ 재생 완료 후 오버레이 자동 사라짐 (3초 후)

9. 다음 대화 준비:
   ✅ 푸시-투-톡 버튼 다시 활성화
   ✅ 카메라 프리뷰 계속 표시

전체 플로우 시간: 약 20-30초
```

---

**3.3 세부 기능 테스트**

**카메라 테���트:**
```
1. 후면 카메라 프리뷰:
   ✅ 실시간 영상 표시
   ✅ 조명 변화에 따른 자동 노출 조정
   ✅ 해상도: 1920x1080 또는 설정값

2. 카메라 전환 (코드에서 지원 시):
   ✅ 전면/후면 카메라 전환

3. 1 FPS 키프레임 캡처:
   ✅ 매 1초마다 JPEG 이미지 저장
   ✅ 8초 녹음 = 8개 키프레임
   ✅ 파일 크기: ~100-300 KB/프레임
```

**오디오 테스트:**
```
1. 녹음 품질:
   ✅ iPhone 마이크 (하단 또는 상단)
   ✅ 샘플레이트: 44100 Hz (고품질)
   ✅ 인코더: AAC-LC
   ✅ 배경 소음 필터링 (iOS 자동)

2. 재생 품질:
   ✅ iPhone 스피커
   ✅ Edge TTS 한국어 음성 (InJoonNeural/SunHiNeural)
   ✅ 볼륨 조절 (설정 화면)
   ✅ AirPods/Bluetooth 스피커 지원
```

**권한 테스트:**
```
1. 권한 거부 후 재요청:
   설정 → Eden → 권한 → 카메라/마이크 끄기
   → 앱 재실행
   → 에러 메시지 표시
   → [설정 열기] 버튼 탭
   → 권한 수동 허용

2. 런타임 권한 취소:
   앱 실행 중 → 설정에서 권한 끄기
   → 앱 돌아오기
   → 카메라 프리뷰 중단
   → 버튼 탭 시 에러 스낵바
```

---

#### Step 4: 디버깅 및 로그 확인

**4.1 Flutter 로그 (터미널)**

```bash
# flutter run 실행 중인 터미널에서 실시간 로그 확인

# 필터링된 로그만 보기
flutter logs | grep -E "Logger|Error|Exception"

# 전체 로그
flutter logs

# 로그 파일로 저장
flutter logs > iphone_test.log
```

**로그 예시:**
```
🔍 DEBUG: Camera initialized: back camera
📷 Capturing keyframe 1/8
📷 Capturing keyframe 2/8
🎙️ Recording started
🎙️ Recording stopped: /path/to/audio.m4a
🌐 API call: POST /api/v2/chat, status: 200, duration: 2847ms
🔊 Playing audio from base64
✅ Audio playback completed
```

---

**4.2 Xcode Console (상세 로그)**

```bash
# Xcode 열기
open ios/Runner.xcworkspace

# Xcode에서:
# 1. 상단 툴바: iPhone 15 Pro 선택
# 2. Product → Run (⌘ + R)
# 3. 하단 Console 영역 확인

# Console에서:
# - Flutter 로그
# - iOS 시스템 로그
# - 네이티브 플러그인 로그
# - 에러 스택 트레이스
```

---

**4.3 iPhone 디바이스 로그**

```bash
# iPhone 시스템 로그 보기 (Xcode)
# Xcode → Window → Devices and Simulators
# iPhone 15 Pro 선택 → Open Console

# 필터: "Eden" 또는 "flutter"

# 또는 명령어:
idevicesyslog | grep Eden
```

---

#### Step 5: 성능 프로파일링

**5.1 Flutter DevTools**

```bash
# flutter run 후 출력된 URL 복사:
# The Flutter DevTools debugger and profiler is available at:
# http://127.0.0.1:9100?uri=http://127.0.0.1:50123/abc123def456/

# 브라우저에서 열기
open http://127.0.0.1:9100?uri=http://127.0.0.1:50123/abc123def456/
```

**DevTools 기능:**
```
1. Performance 탭:
   ✅ FPS 측정 (목표: 60 FPS)
   ✅ Frame rendering time
   ✅ GPU/CPU 사용량

2. Memory 탭:
   ✅ 메모리 사용량 (목표: < 200 MB)
   ✅ 메모리 누수 감지
   ✅ 힙 스냅샷

3. Network 탭:
   ✅ API 호출 로그
   ✅ 요청/응답 크기
   ✅ 응답 시간

4. Logging 탭:
   ✅ Logger 출력
   ✅ 에러 로그
   ✅ 필터링 및 검색
```

---

**5.2 Xcode Instruments**

```bash
# Xcode에서:
# Product → Profile (⌘ + I)
# Instruments 앱 실행됨

# 템플릿 선택:
# - Time Profiler: CPU 사용량
# - Allocations: 메모리 할당
# - Leaks: 메모리 누수
# - Energy Log: 배터리 소모

# Record 버튼 (빨간 점) 클릭
# → iPhone에서 앱 사용
# → Stop (사각형) 클릭
# → 분석 결과 확인
```

---

#### Step 6: 문제 해결 (iPhone)

**문제 1: "Developer Mode Required"**

```
증상:
iPhone에 "개발자 모드가 필요합니다" 메시지

해결:
1. 설정 → 개인정보 보호 및 보안 → 개발자 모드
2. 개발자 모드 켜기
3. iPhone 재시동
4. "개발자 모드 켜기" 재확인 + 암호 입력
```

---

**문제 2: "Trust This Computer?"가 안 뜸**

```
증상:
USB 연결했는데 신뢰 프롬프트 없음

해결:
1. iPhone 잠금 해제
2. 케이블 재연결
3. 다른 USB 포트 시도
4. 케이블 교체 (충전 전용 vs 데이터 케이블)
5. Mac 재시작
```

---

**문제 3: "No provisioning profiles found"**

```
증상:
Xcode build failed: Signing for "Runner" requires a development team

해결:
1. Xcode에서 ios/Runner.xcworkspace 열기
2. Runner 프로젝트 선택 (왼쪽)
3. Signing & Capabilities 탭
4. Team: [Apple ID 선택] (자동으로 Personal Team 생성됨)
5. Bundle Identifier 변경 (고유해야 함):
   com.example.frontend → com.yourname.eden
6. Automatically manage signing ✅ 체크
7. flutter clean && flutter run
```

---

**문제 4: "The device is locked"**

```
증상:
Could not install application: The device is locked.

해결:
1. iPhone 잠금 해제
2. flutter run 재시도
```

---

**문제 5: 앱이 설치되었는데 실행 안 됨**

```
증상:
빌드 성공했는데 앱 탭하면 즉시 종료

해결:
1. iPhone 설정 → 일반 → VPN 및 기기 관리
2. [Apple ID] 선택
3. "Eden" 앱 → [신뢰] 탭
4. 확인 다이얼로그 → [신뢰] 탭
5. 앱 재실행
```

---

### 9.2 Galaxy (Android) 실제 기기 테스트 (USB 연결)

#### 준비물

```
하드웨어:
✅ Samsung Galaxy S21 이상 또는 Pixel 6 이상
✅ USB-C to USB-C 케이블 (또는 USB-C to USB-A)
✅ Mac (Apple Silicon 또는 Intel)

소프트웨어:
✅ Android Studio 설치됨
✅ Android 11+ (Galaxy)
✅ Flutter 3.35.7+
✅ ADB (Android Debug Bridge)
```

---

#### Step 1: Galaxy 준비 및 연결

**1.1 개발자 옵션 활성화**

```
Galaxy에서:

1. 설정 앱 열기

2. 휴대전화 정보 (맨 아래)

3. 소프트웨어 정보

4. "빌드 번호" 7번 연속 탭
   (탭할 때마다 "개발자 모드까지 n단계 남음" 메시지)

5. "개발자 모드가 사용 설정되었습니다" 토스트 메시지

6. 뒤로 가기 → 설정 메인
   → 개발자 옵션 메뉴 새로 생김 (일반 섹션 하단)
```

---

**1.2 USB 디버깅 활성화**

```
Galaxy에서:

1. 설정 → 개발자 옵션

2. 개발자 옵션 스위치 켜기 (맨 위)

3. USB 디버깅 스위치 켜기
   (디버깅 섹션)

4. 경고 다이얼로그:
   "USB 디버깅을 허용하시겠습니까?"
   → [확인]

선택사항 (성능 향상):
5. USB 구성 → MTP (미디어 전송 프로토콜)
6. 애니메이션 배율 → 0.5x (또는 끄기)
```

---

**1.3 USB 케이블로 Mac 연결**

```
1. Galaxy를 USB 케이블로 Mac에 연결

2. Galaxy 알림:
   "USB 디버깅 허용"

   "이 컴퓨터에서 USB 디버깅을 허용하시겠습니까?"

   RSA 키 지문:
   AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD

   [이 컴퓨터에서 항상 허용] ✅ 체크 (권장)

   [취소] [확인]
   → [확인] 탭

3. Mac 터미널에서 확인:
```

```bash
# ADB로 기기 확인
adb devices

# 출력:
# List of devices attached
# RF8R1234ABC    device

# "device" = 연결 성공
# "unauthorized" = Galaxy에서 아직 승인 안 함
# "offline" = 연결 불안정
```

---

**1.4 Flutter에서 기기 확인**

```bash
cd /Users/kyungsbook/Desktop/myai/frontend

flutter devices

# 출력:
# 3 connected devices:
#
# SM G991N (mobile)       • RF8R1234ABC • android-arm64 • Android 13 (API 33)
# sdk gphone64 arm64 (mobile) • emulator-5554 • android-arm64 • Android 13 (API 33) (emulator)
# iPhone 16e (mobile)     • UUID-9012 • ios • iOS 17.0 (simulator)
```

**실제 Galaxy 구분:**
- `(mobile)` + `android-arm64` + `Android 13 (API 33)` (에뮬레이터 아님)
- Device ID: 실제 하드웨어 시리얼 (RF8R...)
- 모델명: SM G991N (Galaxy S21) 등

---

#### Step 2: Flutter 앱 배포 및 실행

**2.1 앱 실행**

```bash
# 방법 1: Device ID로 직접 실행
flutter run -d RF8R1234ABC

# 방법 2: flutter run 후 선택
flutter run

# 프롬프트:
# Multiple devices found:
# [1]: SM G991N (RF8R1234ABC)
# [2]: sdk gphone64 arm64 (emulator-5554)
# [3]: iPhone 16e (simulator)
# Please choose one (or "q" to quit): 1

# 빌드 시작 (최초 2-5분 소요)
```

**빌드 과정:**
```
Launching lib/main.dart on SM G991N in debug mode...
Running Gradle task 'assembleDebug'...
✓ Built build/app/outputs/flutter-apk/app-debug.apk (45.2 MB)
Installing build/app/outputs/flutter-apk/app-debug.apk...        1,234ms

Flutter run key commands.
r Hot reload.
R Hot restart.
h List all available interactive commands.
d Detach (terminate "flutter run" but leave application running).
c Clear the screen
q Quit (terminate the application on the device).

A Dart VM Service on SM G991N is available at:
http://127.0.0.1:40123/xyz789uvw012/
```

---

**2.2 앱 설치 확인**

**Galaxy 홈 화면/앱 드로어에서:**
```
1. 앱 아이콘 확인:
   - 이름: "Eden" (또는 "frontend")
   - 기본 Flutter 아이콘 또는 커스텀 아이콘

2. 앱 탭하여 실행 가능
   - Hot reload 중이면 터미널 연결 유지
   - 독립적으로 실행 가능
```

**ADB로 확인:**
```bash
# 설치된 앱 확인
adb shell pm list packages | grep frontend

# 출력:
# package:com.example.frontend

# 앱 정보
adb shell dumpsys package com.example.frontend | head -20
```

---

#### Step 3: 권한 부여 및 테스트

**3.1 최초 실행 시 권한 프롬프트**

```
앱 실행 순서:

1. 앱 시작 → PermissionScreen 표시

2. [카메라와 마이크 권한 허용하기] 버튼 탭

3. 시스템 권한 다이얼로그 (순차적):

   첫 번째 다이얼로그:
   "Eden이 사진 및 동영상을 촬영하도록 허용하시겠어요?"
   [ 앱 사용 중에만 허용 ]
   [ 이번만 허용 ]
   [ 허용 안 함 ]
   → [앱 사용 중에만 허용] 탭 (권장)

   두 번째 다이얼로그:
   "Eden이 오디오를 녹음하도록 허용하시겠어요?"
   [ 앱 사용 중에만 허용 ]
   [ 이번만 허용 ]
   [ 허용 안 함 ]
   → [앱 사용 중에만 허용] 탭

4. 권한 부여 완료 → VoiceFirstScreen으로 자동 이동
```

---

**3.2 전체 멀티모달 플로우 테스트**

```
=== Galaxy에서 완전한 End-to-End 테스트 ===

1. VoiceFirstScreen 확인:
   ✅ 전체 화면 카메라 프리뷰 (Galaxy 후면 카메라)
   ✅ 중앙 하단: 푸시-투-톡 버튼 (파란색 마이크)
   ✅ 상단: Adam/Eve 토글
   ✅ 왼쪽 상단: 프로필 아이콘
   ✅ 오른쪽 상단: 설정 아이콘

2. 백엔드 서버 확인 (동일)

3. Galaxy에서 마이크 버튼 길게 누르기:
   ✅ 버튼 애니메이션 시작
   ✅ 카메라 1 FPS 자동 캡처

4. Galaxy 마이크에 대고 말하기 (5-8초):
   "안녕, Eve! 오늘 기분이 좋아요!"

   진행:
   ✅ 오디오 녹음 (하단 마이크)
   ✅ 키프레임 캡처 (1 FPS)

5. 버튼 놓기:
   ✅ 로딩 오버레이
   ✅ 백엔드 전송

6. 백엔드 처리 (2-4초)

7. 응답 수신:
   ✅ 응답 오버레이 (글래스모피즘)
   ✅ TTS 재생 (Eve 여성 목소리)
   ✅ Galaxy 스피커 출력

8. 다음 대화 준비

전체 플로우 시간: 약 20-30초
```

---

**3.3 Galaxy 특화 기능 테스트**

**카메라 품질 (삼성 고해상도):**
```
Galaxy S21/S22/S23:
✅ 후면 카메라: 64MP (또는 108MP)
✅ Flutter에서 다운샘플링: 1920x1080
✅ 우수한 저조도 성능
✅ 빠른 AF (자동 초점)
```

**오디오 품질:**
```
Galaxy 마이크:
✅ 다중 마이크 (노이즈 캔슬링)
✅ 샘플레이트: 44100 Hz 지원
✅ 고품질 AAC 인코딩
```

**Samsung One UI 특성:**
```
알림:
- 권한 요청 시 One UI 스타일 다이얼로그
- 알림 패널에서 앱 상태 확인 가능

배터리 최적화:
- 설정 → 배터리 → 백그라운드 사용 제한 → Eden 예외 추가 (선택)
```

---

#### Step 4: 디버깅 및 로그 확인

**4.1 ADB Logcat (실시간 로그)**

```bash
# 전체 로그
adb logcat

# Flutter 앱 로그만 필터링
adb logcat | grep flutter

# 에러만 표시
adb logcat *:E

# 특정 태그 필터
adb logcat -s Eden

# 로그 저장
adb logcat > galaxy_test.log
```

**로그 예시:**
```
11-04 05:30:12.345 12345 12346 I flutter : 🔍 DEBUG: Camera initialized
11-04 05:30:13.456 12345 12346 I flutter : 📷 Capturing keyframe 1/8
11-04 05:30:14.567 12345 12346 I flutter : 🎙️ Recording started
11-04 05:30:19.678 12345 12346 I flutter : 🎙️ Recording stopped: 5.2s
11-04 05:30:21.789 12345 12346 I flutter : 🌐 API call: POST /api/v2/chat
11-04 05:30:24.890 12345 12346 I flutter : 🔊 Playing audio from base64
```

---

**4.2 Flutter DevTools (동일)**

```bash
# flutter run 후 출력된 URL 브라우저에서 열기
open http://127.0.0.1:9100?uri=http://127.0.0.1:40123/xyz789uvw012/
```

---

**4.3 Android Studio Logcat (GUI)**

```
Android Studio 열기:
1. View → Tool Windows → Logcat
2. Device 선택: SM G991N (RF8R1234ABC)
3. Package 선택: com.example.frontend
4. Log level: Verbose

필터 추가:
- Tag: flutter
- Message: 정규식 검색 가능
```

---

#### Step 5: 성능 프로파일링

**5.1 Flutter DevTools (동일)**

**5.2 Android Studio Profiler**

```
Android Studio:
1. View → Tool Windows → Profiler
2. Device 선택: SM G991N
3. Process 선택: com.example.frontend

프로파일링:
- CPU: CPU 사용량 및 스레드
- Memory: 메모리 할당 및 힙
- Network: API 호출 및 데이터 전송
- Energy: 배터리 소모
```

---

**5.3 Galaxy 개발자 옵션 (성능 모니터링)**

```
Galaxy에서:
설정 → 개발자 옵션

성능 모니터링:
✅ GPU 렌더링 프로파일 작성 → 화면에 막대 그래프로 표시
✅ GPU 뷰 업데이트 표시 → 화면 업데이트 시 깜빡임
✅ 레이아웃 경계 표시 → UI 구조 확인
✅ 프로파일 GPU 렌더링 → adb shell dumpsys gfxinfo

FPS 확인:
- 목표: 60 FPS (16.67ms/프레임)
- 초록색 선 아래 유지
```

---

#### Step 6: 문제 해결 (Galaxy)

**문제 1: "USB 디버깅 허용" 안 뜸**

```
해결:
1. Galaxy 잠금 해제
2. USB 케이블 재연결
3. USB 디버깅 껐다 다시 켜기
4. 다른 USB 포트 시도
5. 케이블 교체
6. adb kill-server && adb start-server
```

---

**문제 2: adb devices에서 "unauthorized"**

```
해결:
1. Galaxy 알림 패널 확인
2. "USB 디버깅 허용" 탭
3. [확인] 탭
4. adb devices 재확인
```

---

**문제 3: "Offline" 상태**

```
해결:
1. USB 케이블 품질 확인 (데이터 전송 가능한 케이블)
2. USB 포트 변경
3. adb kill-server && adb start-server
4. Galaxy 재부팅
5. Mac 재부팅
```

---

**문제 4: 빌드 느림 (Gradle)**

```
해결:
1. Android Studio → Preferences → Build, Execution, Deployment
   → Compiler → Command-line Options:
   --parallel --max-workers=4

2. android/gradle.properties 추가:
   org.gradle.jvmargs=-Xmx4096m
   org.gradle.parallel=true
   org.gradle.caching=true

3. flutter clean && flutter pub get
```

---

**문제 5: 권한 에러**

```
증상:
Camera/Microphone permission denied

해결:
1. Galaxy 설정 → 앱 → Eden
2. 권한 → 카메라/마이크 허용
3. 앱 재시작

또는 ADB:
adb shell pm grant com.example.frontend android.permission.CAMERA
adb shell pm grant com.example.frontend android.permission.RECORD_AUDIO
```

---

### 9.3 기기 비교 테스트

#### iPhone vs Galaxy 기능 비교

| 기능 | iPhone 15 Pro | Galaxy S23 | 비고 |
|------|--------------|-----------|------|
| **카메라 화질** | ⭐⭐⭐⭐⭐ (48MP) | ⭐⭐⭐⭐⭐ (200MP) | 둘 다 우수 |
| **오디오 녹음** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | iPhone 약간 우수 |
| **TTS 재생** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 스피커 품질 차이 |
| **빌드 속도** | ⭐⭐⭐⭐ (45초) | ⭐⭐⭐ (2-3분) | Gradle 느림 |
| **Hot Reload** | ⭐⭐⭐⭐⭐ (즉시) | ⭐⭐⭐⭐⭐ (즉시) | 동일 |
| **성능** | ⭐⭐⭐⭐⭐ (A17 Pro) | ⭐⭐⭐⭐⭐ (Snapdragon 8 Gen 2) | 거의 동일 |
| **배터리 효율** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Galaxy 약간 우수 |
| **UI 일관성** | ⭐⭐⭐⭐⭐ (iOS 통일) | ⭐⭐⭐⭐ (One UI 변형) | iOS 더 일관적 |

---

#### 동시 테스트 워크플로우

```
=== 크로스 플랫폼 테스트 ===

1. 두 기기 모두 Mac에 USB 연결

2. 기기 확인:
   flutter devices

   # 출력:
   # iPhone 15 Pro (mobile) • 00008030-... • ios
   # SM G991N (mobile)      • RF8R1234ABC • android-arm64

3. 터미널 탭 2개 사용:

   탭 1 (iPhone):
   flutter run -d 00008030-001A2B3C4D5E001F

   탭 2 (Galaxy):
   flutter run -d RF8R1234ABC

4. 동시에 동일한 대화 테스트:
   - iPhone: "안녕, Adam!"
   - Galaxy: "안녕, Adam!"

5. 응답 비교:
   - 텍스트 동일한지
   - TTS 음성 동일한지
   - 응답 시간 차이
   - UI 표시 차이

6. 버그 발견 시:
   - 어느 플랫폼에서 발생했는지 기록
   - 로그 저장 (flutter logs > platform_bug.log)
   - 재현 단계 문서화
```

---

### 9.4 실제 기기 테스트 체크리스트

```
=== iPhone 테스트 ===
✅ USB 연결 및 신뢰
✅ 개발자 모드 활성화
✅ flutter run 성공
✅ 앱 설치 확인
✅ 카메라 권한 허용
✅ 마이크 권한 허용
✅ 카메라 프리뷰 작동
✅ 음성 녹음 (5초+)
✅ 1 FPS 키프레임 캡처 (8개)
✅ 백엔드 전송 성공
✅ TTS 재생 (Adam/Eve)
✅ 페르소나 전환 (Adam ↔ Eve)
✅ 프로필 화면 확인
✅ 설정 화면 확인
✅ Pitfall warning 트리거
✅ Emotional support 모드
✅ 오프라인 모드 (캐시)
✅ 앱 재시작 후 설정 유지
✅ Hot reload 테스트
✅ DevTools 프로파일링
✅ 배터리 소모 측정
✅ 메모리 사용량 (<200 MB)

=== Galaxy 테스트 ===
✅ USB 연결 및 디버깅 허용
✅ 개발자 옵션 활성화
✅ flutter run 성공
✅ 앱 설치 확인
✅ 카메라 권한 허용
✅ 마이크 권한 허용
✅ 카메라 프리뷰 작동
✅ 음성 녹음 (5초+)
✅ 1 FPS 키프레임 캡처 (8개)
✅ 백엔드 전송 성공
✅ TTS 재생 (Adam/Eve)
✅ 페르소나 전환
✅ 프로필 화면 확인
✅ 설정 화면 확인
✅ Pitfall warning 트리거
✅ Emotional support 모드
✅ 오프라인 모드
✅ 앱 재시작 후 설정 유지
✅ Hot reload 테스트
✅ DevTools 프로파일링
✅ 배터리 소모 측정
✅ 메모리 사용량 (<200 MB)

=== 크로스 플랫폼 ===
✅ UI 일관성 확인
✅ 동일한 대화에 동일한 응답
✅ 성능 차이 측정
✅ 버그 플랫폼별 확인
✅ 폰트/색상 차이 없음
✅ 애니메이션 동일
✅ 권한 처리 동일
```

---

### 9.5 빠른 참조 명령어

```bash
# === iPhone ===

# 기기 확인
flutter devices | grep ios

# 앱 실행
flutter run -d <iphone-device-id>

# 로그
flutter logs | grep Logger

# Xcode에서 기기 확인
open -a Xcode
# Window → Devices and Simulators

# === Galaxy ===

# 기기 확인
adb devices
flutter devices | grep android

# 앱 실행
flutter run -d <android-device-id>

# 로그
adb logcat | grep flutter

# 권한 부여
adb shell pm grant com.example.frontend android.permission.CAMERA
adb shell pm grant com.example.frontend android.permission.RECORD_AUDIO

# 앱 삭제
adb uninstall com.example.frontend

# 스크린샷
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# === 공통 ===

# 빌드 정리
flutter clean
flutter pub get

# Hot reload (앱 실행 중)
r

# Hot restart
R

# 종료
q
```

---

**이제 실제 iPhone과 Galaxy로 테스트하세요!** 📱🚀

```bash
# 1. 두 기기 모두 USB 연결
# 2. 터미널 탭 2개 열기
# 3. 백엔드 서버 실행
cd backend && ./start_local.sh

# 4. iPhone 테스트
cd frontend
flutter run -d <iphone-id>

# 5. Galaxy 테스트 (새 탭)
cd frontend
flutter run -d <android-id>

# 6. 동시에 대화 테스트!
```

**즐거운 테스팅 되세요!** 🎉
