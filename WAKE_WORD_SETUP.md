# Wake Word Setup Guide

이 가이드는 "Hey Adam" 및 "Hey Eve" wake word 기능을 설정하는 방법을 설명합니다.

## 1. Picovoice Access Key 받기

1. [Picovoice Console](https://console.picovoice.ai/)에 가입/로그인
2. 새 프로젝트 생성
3. Access Key 복사
4. `frontend/lib/services/wake_word_service.dart` 파일에서 빈 문자열을 Access Key로 교체:

```dart
_porcupineManager = await PorcupineManager.fromKeywordPaths(
  'YOUR_ACCESS_KEY_HERE',  // <- 여기에 Access Key 붙여넣기
  [keywordPath],
  _wakeWordCallback,
  errorCallback: _errorCallback,
);
```

**참고**: Picovoice 무료 티어는 월 3개 wake words까지 무료입니다.

## 2. Wake Word 모델 파일 생성

### 2.1 Picovoice Console에서 커스텀 wake word 생성

1. Picovoice Console → "Wake Word" 탭
2. "Create Wake Word" 클릭
3. Wake word 입력:
   - **첫 번째**: "Hey Adam"
   - **두 번째**: "Hey Eve"
4. 각각에 대해 Android 및 iOS 플랫폼용 `.ppn` 파일 다운로드

### 2.2 파일 구조

다운로드한 `.ppn` 파일을 다음 위치에 배치:

```
frontend/
├── assets/
│   └── wake_words/
│       ├── hey_adam_android.ppn
│       ├── hey_adam_ios.ppn
│       ├── hey_eve_android.ppn
│       └── hey_eve_ios.ppn
```

### 2.3 파일명 규칙

Picovoice Console에서 다운로드한 파일명을 다음과 같이 변경:
- `Hey-Adam_en_android_v3_0_0.ppn` → `hey_adam_android.ppn`
- `Hey-Adam_en_ios_v3_0_0.ppn` → `hey_adam_ios.ppn`
- `Hey-Eve_en_android_v3_0_0.ppn` → `hey_eve_android.ppn`
- `Hey-Eve_en_ios_v3_0_0.ppn` → `hey_eve_ios.ppn`

## 3. 권한 설정

### Android (`android/app/src/main/AndroidManifest.xml`)

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- 마이크 권한 -->
    <uses-permission android:name="android.permission.RECORD_AUDIO" />

    <!-- 백그라운드 마이크 사용 (선택사항) -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

    <application>
        ...
    </application>
</manifest>
```

### iOS (`ios/Runner/Info.plist`)

```xml
<key>NSMicrophoneUsageDescription</key>
<string>Eden이 "Hey Adam" 또는 "Hey Eve" 호출어를 인식하기 위해 마이크 권한이 필요합니다.</string>
```

## 4. 테스트

1. 앱 실행
2. Wake word 모드 활성화
3. "Hey Adam" 또는 "Hey Eve" 말하기
4. 앱이 자동으로 듣기 시작하는지 확인

## 5. 문제 해결

### 에러: "Invalid Access Key"
- Picovoice Console에서 올바른 Access Key를 복사했는지 확인
- Access Key에 불필요한 공백이 없는지 확인

### 에러: "Keyword file not found"
- `.ppn` 파일이 올바른 위치에 있는지 확인
- 파일명이 정확히 일치하는지 확인
- `pubspec.yaml`에 assets가 선언되어 있는지 확인

### Wake word가 감지되지 않음
- 조용한 환경에서 테스트
- 명확하게 발음 ("Hey Adam" / "Hey Eve")
- 마이크 권한이 부여되었는지 확인
- Picovoice Console에서 민감도 조정 (sensitivity parameter)

## 6. 고급 설정

### 민감도 조정

`wake_word_service.dart`에서 민감도를 조정할 수 있습니다:

```dart
_porcupineManager = await PorcupineManager.fromKeywordPaths(
  accessKey,
  [keywordPath],
  _wakeWordCallback,
  errorCallback: _errorCallback,
  sensitivity: 0.7,  // 0.0 (덜 민감) ~ 1.0 (더 민감)
);
```

### 백그라운드 리스닝

백그라운드에서도 wake word를 감지하려면 추가 설정이 필요합니다:
- Android: Foreground Service 구현
- iOS: Background Modes 활성화

**참고**: 배터리 소모를 고려하여 필요시에만 활성화하는 것을 권장합니다.

## 7. 라이선스 및 비용

- **무료 티어**: 월 3개 wake words, 제한된 사용
- **개인 사용**: 월 $4.99
- **상업적 사용**: Picovoice 영업팀 문의

자세한 내용은 [Picovoice Pricing](https://picovoice.ai/pricing/)을 참조하세요.
