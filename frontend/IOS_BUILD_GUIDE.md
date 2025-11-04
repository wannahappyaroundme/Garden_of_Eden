# 🍎 iOS 빌드 가이드 (간단 버전)

## ✅ 수정 완료된 사항
- iOS deployment target → 13.0으로 설정
- Pods 재설치 완료

---

## 📱 Xcode에서 Archive 하는 방법

### 1단계: Xcode 열기 (이미 열려있으면 재시작)

```bash
# Xcode 재시작 (변경사항 반영)
killall Xcode
open ios/Runner.xcworkspace
```

또는 직접:
- `frontend/ios/Runner.xcworkspace` 더블클릭

---

### 2단계: Signing & Capabilities 설정

**화면 구성:**
```
좌측: 프로젝트 네비게이터
중앙: 설정 영역
상단: 탭 메뉴
```

**단계:**

1. **좌측 네비게이터에서 Runner 선택**
   - 맨 위에 파란색 아이콘 `Runner` 클릭

2. **중앙 TARGETS에서 Runner 선택**
   - `TARGETS` 섹션의 `Runner` 클릭 (PROJECT 말고!)

3. **상단 탭에서 `Signing & Capabilities` 클릭**
   ```
   General │ Signing & Capabilities │ Resource Tags │ Info │ ...
            ↑ 여기 클릭!
   ```

4. **Team 설정**
   - `Automatically manage signing` 체크 ✅
   - `Team` 드롭다운 클릭
   - Apple ID 선택 (없으면 "Add an Account..." 클릭)

5. **Apple ID 로그인 (처음 1회만)**
   - Apple ID 입력
   - 비밀번호 입력
   - 완료!

6. **Bundle Identifier 확인**
   - 자동으로 생성됨: `com.yourname.frontend`
   - 그대로 두면 됨

---

### 3단계: Archive 실행

1. **Destination 선택**
   - Xcode 상단 중앙: `Runner > [현재 장치]` 클릭
   - **`Any iOS Device (arm64)`** 선택
   - ⚠️ Simulator 선택하면 Archive 안됨!

2. **Archive 실행**
   ```
   상단 메뉴: Product > Archive
   ```
   - 빌드 시작됨 (2-5분 소요)
   - 진행 상황: Xcode 상단 중앙에 표시

3. **Archive 완료**
   - Organizer 창 자동으로 열림
   - Archive 목록에 최신 빌드 표시됨

---

### 4단계: IPA Export (USB 없이 배포)

**Organizer 창에서:**

1. **최신 Archive 선택**
   - 가장 위에 있는 항목

2. **Distribute App 클릭**

3. **배포 방법 선택: `Ad Hoc`**
   - ⚠️ Development 말고 Ad Hoc!
   - Ad Hoc = 파일로 배포 가능

4. **Next > Next**
   - 기본 설정 그대로 진행

5. **Export 클릭**
   - 저장 위치 선택 (Desktop 추천)
   - Export 완료!

6. **결과물 확인**
   ```
   📁 [선택한 폴더]
   └── Runner.ipa  (약 80MB)
   ```

---

## 📤 IPA 파일 iPhone에 설치

### 방법 1: AirDrop (가장 빠름)

1. Mac에서 `Runner.ipa` 우클릭
2. `공유` > `AirDrop` 선택
3. iPhone 선택
4. iPhone에서 수락

### 방법 2: 이메일

1. `Runner.ipa` 이메일에 첨부
2. iPhone에서 이메일 열기
3. 첨부파일 다운로드

### 방법 3: iCloud Drive

1. `Runner.ipa`를 iCloud Drive에 업로드
2. iPhone 파일 앱에서 다운로드

---

## 📲 iPhone에서 설치

1. **IPA 파일 열기**
   - 파일 앱 또는 이메일에서 탭

2. **설치 진행**
   - 자동으로 설치 시작

3. **개발자 신뢰 설정**
   - `설정` > `일반` > `VPN 및 기기 관리`
   - 개발자 프로필 찾기
   - `신뢰` 버튼 클릭

4. **앱 실행**
   - 홈 화면에서 Project Eden 아이콘 탭
   - 권한 허용 (카메라, 마이크)
   - 사용 시작!

---

## ⚠️ 문제 해결

### Signing 오류: "Failed to create provisioning profile"

**해결:**
1. Bundle Identifier 변경
   - `Signing & Capabilities`에서
   - `com.yourname.frontend` → `com.yourname.projecteden`
2. Clean Build: `Product` > `Clean Build Folder` (⇧⌘K)
3. 다시 Archive

### Archive 버튼이 회색으로 비활성화

**원인:** Simulator 선택되어 있음

**해결:**
- Destination을 `Any iOS Device (arm64)`로 변경

### "No accounts with App Store Connect access"

**원인:** Apple ID에 개발자 권한 없음

**해결:**
- 무료 계정으로도 가능
- Ad Hoc 배포는 App Store Connect 필요 없음
- Bundle Identifier만 고유하게 설정하면 됨

### IPA 설치 후 "신뢰할 수 없는 개발자"

**해결:**
1. iPhone `설정` 앱
2. `일반` > `VPN 및 기기 관리`
3. 개발자 프로필 선택
4. `신뢰` 클릭

---

## 💡 빠른 테스트 (USB 사용)

Archive 없이 바로 테스트하려면:

```bash
# iPhone USB 연결 후
cd frontend
flutter run
```

- 앱이 iPhone에 즉시 설치됨
- 무료 계정: 7일 후 만료
- 재설치하면 다시 7일 사용 가능

---

## 🎯 요약

### Xcode에서 해야 할 일:
1. ✅ Runner 선택 (좌측)
2. ✅ Signing & Capabilities 탭 (상단)
3. ✅ Team 설정 (Apple ID)
4. ✅ Destination: Any iOS Device
5. ✅ Product > Archive
6. ✅ Distribute App > Ad Hoc > Export

### 결과물:
- `Runner.ipa` 파일 (80MB)
- AirDrop / 이메일 / iCloud로 전송
- iPhone에서 바로 설치 가능!

---

**백엔드:** http://3.39.177.218:8000 (자동 연결)
**도움이 필요하면:** INSTALL_GUIDE.md 참고
