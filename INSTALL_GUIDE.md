# 📱 프로젝트 에덴 V2 - 설치 가이드

## 📋 준비된 파일

### Android (Galaxy)
- **파일:** `frontend/build/app/outputs/flutter-apk/app-debug.apk`
- **크기:** 148MB
- **상태:** ✅ 빌드 완료

### iOS (iPhone)
- **파일:** 아래 가이드에 따라 생성 필요
- **요구사항:** Mac + Xcode

---

## 🤖 Android (Galaxy) 설치

### 방법 1: 파일 전송 후 설치 (추천)

**1단계: APK 파일 전송**
```bash
# 파일 위치
frontend/build/app/outputs/flutter-apk/app-debug.apk
```

다음 중 하나로 전송:
- 📧 이메일 첨부
- ☁️ Google Drive / Dropbox
- 💬 카카오톡 / 메신저
- 🔗 USB 케이블

**2단계: Galaxy에서 설치**
1. 전송받은 `app-debug.apk` 파일 실행
2. "출처를 알 수 없는 앱 설치" 허용 (처음 1회만)
3. "설치" 버튼 클릭
4. 설치 완료!

**3단계: 권한 허용**
1. 앱 실행
2. 카메라 권한 허용
3. 마이크 권한 허용
4. 사용 시작!

### 방법 2: USB 연결 (개발자용)

```bash
cd frontend
flutter install  # Galaxy USB 연결 후
```

---

## 🍎 iOS (iPhone) 설치

### 준비사항
- ✅ Mac 컴퓨터
- ✅ Xcode 설치됨
- ✅ Apple ID (무료 계정 가능)

### 방법 1: Ad Hoc IPA 생성 (파일로 배포 - 추천)

**자동 빌드 스크립트 사용:**
```bash
cd frontend
./build_ios_ipa.sh
```

스크립트가 안내하는 대로 Xcode에서:
1. `Product` > `Destination` > `Any iOS Device (arm64)` 선택
2. `Product` > `Archive` 실행
3. Organizer 창에서 `Distribute App` 클릭
4. **`Ad Hoc`** 선택
5. Next > Next > Export
6. `.ipa` 파일 저장

**IPA 파일 전송:**
- 🍎 AirDrop으로 iPhone에 전송
- 📧 이메일 첨부
- ☁️ iCloud Drive

**iPhone에서 설치:**
1. `.ipa` 파일 열기
2. `설정` > `일반` > `VPN 및 기기 관리`
3. 개발자 프로필 신뢰
4. 앱 실행!

### 방법 2: 직접 설치 (USB 필요)

**가장 빠른 방법:**
```bash
cd frontend
flutter run  # iPhone USB 연결 후
```

**주의:**
- 무료 Apple ID 사용 시 7일 후 앱 만료
- 재설치하면 다시 7일 사용 가능
- Apple Developer Program ($99/년) 가입 시 1년 유효

### 방법 3: TestFlight (정식 배포)

**Apple Developer Program 필요 ($99/년)**

1. App Store Connect에서 앱 등록
2. IPA 업로드
3. TestFlight 링크로 초대
4. iPhone에서 TestFlight 앱으로 설치

---

## ✅ 설치 후 확인사항

### 1. 권한 설정
- [ ] 카메라 권한 허용됨
- [ ] 마이크 권한 허용됨

### 2. 백엔드 연결 확인
- 백엔드 주소: `http://3.39.177.218:8000`
- WiFi 또는 모바일 데이터 연결 필요

### 3. 첫 대화 테스트
1. 마이크 버튼 **길게 누르기**
2. "안녕하세요" 말하기
3. 손가락 떼기
4. 15-20초 후 AI 응답 확인

---

## 🔧 문제 해결

### Android: 설치 안됨
**증상:** "앱을 설치할 수 없습니다"

**해결:**
1. `설정` > `보안` > `출처를 알 수 없는 앱` 허용
2. 저장 공간 확인 (최소 200MB)
3. 이전 버전 삭제 후 재설치

### iOS: Archive 실패
**증상:** Xcode에서 Archive 버튼이 비활성화

**해결:**
1. Destination을 `Any iOS Device (arm64)`로 설정
2. Simulator 선택되어 있으면 Archive 불가
3. `Product` > `Clean Build Folder` 후 재시도

### iOS: 설치 후 실행 안됨
**증상:** "신뢰할 수 없는 개발자"

**해결:**
1. `설정` > `일반` > `VPN 및 기기 관리`
2. 개발자 프로필 찾기
3. "신뢰" 버튼 클릭

### 백엔드 연결 실패
**증상:** "서버에 연결할 수 없습니다"

**해결:**
1. WiFi/데이터 연결 확인
2. 백엔드 상태 확인: http://3.39.177.218:8000/health
3. 방화벽이 포트 8000 차단하는지 확인

---

## 📊 파일 크기 참고

| 플랫폼 | 파일 형식 | 크기 | 비고 |
|--------|-----------|------|------|
| Android | `.apk` (Debug) | 148MB | 즉시 설치 가능 |
| Android | `.apk` (Release) | ~50MB | 서명 필요 |
| iOS | `.ipa` (Ad Hoc) | ~80MB | Xcode 필요 |

---

## 🎯 추천 설치 방법

### 지금 당장 테스트하려면:
1. **Galaxy:** APK 파일 전송 → 바로 설치 ✅
2. **iPhone:** `flutter run` → USB로 직접 설치 ✅

### 여러 사람에게 배포하려면:
1. **Galaxy:** APK 파일 공유 (이메일, 클라우드)
2. **iPhone:** Ad Hoc IPA 생성 → AirDrop 전송

### 정식 배포 (나중에):
1. **Galaxy:** Google Play Store (서명 필요)
2. **iPhone:** App Store (Apple Developer Program 필요)

---

**백엔드 상태:** http://3.39.177.218:8000/health
**API 문서:** http://3.39.177.218:8000/docs

모든 파일이 AWS EC2 백엔드에 자동 연결되도록 설정되어 있습니다! 🚀
