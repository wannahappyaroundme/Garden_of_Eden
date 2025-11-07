# Google Cloud Text-to-Speech 설정 가이드

Garden of Eden 프로젝트에서 TTS(Text-to-Speech) 기능을 사용하기 위한 Google Cloud 설정 가이드입니다.

## 필요한 이유
- Microsoft Edge TTS가 403 에러로 차단됨
- Google Cloud TTS는 고품질 Neural2 음성 제공
- 월 100만 글자까지 무료 (충분한 할당량)

---

## 1단계: Google Cloud 프로젝트 생성

### 1-1. Google Cloud Console 접속
1. https://console.cloud.google.com 접속
2. Google 계정으로 로그인

### 1-2. 새 프로젝트 만들기
1. 상단 메뉴에서 "프로젝트 선택" 클릭
2. "새 프로젝트" 버튼 클릭
3. 프로젝트 정보 입력:
   - **프로젝트 이름**: `Garden-of-Eden` (또는 원하는 이름)
   - **위치**: 조직 없음 (개인 프로젝트)
4. "만들기" 클릭
5. 프로젝트가 생성될 때까지 기다림 (몇 초 소요)

---

## 2단계: Text-to-Speech API 활성화

### 2-1. API 라이브러리로 이동
1. 왼쪽 메뉴 (≡) → "API 및 서비스" → "라이브러리" 클릭
2. 또는 직접 접속: https://console.cloud.google.com/apis/library

### 2-2. Text-to-Speech API 검색 및 활성화
1. 검색창에 `Text-to-Speech` 입력
2. "Cloud Text-to-Speech API" 클릭
3. **"사용 설정"** 버튼 클릭
4. API가 활성화될 때까지 기다림 (몇 초 소요)

> **참고**: 처음 사용 시 결제 정보 입력이 필요할 수 있습니다. 하지만 무료 할당량이 있어 실제 청구는 거의 없습니다.

---

## 3단계: 서비스 계정 생성

### 3-1. IAM 및 관리자 페이지로 이동
1. 왼쪽 메뉴 (≡) → "IAM 및 관리자" → "서비스 계정" 클릭
2. 또는 직접 접속: https://console.cloud.google.com/iam-admin/serviceaccounts

### 3-2. 서비스 계정 만들기
1. **"+ 서비스 계정 만들기"** 버튼 클릭
2. 서비스 계정 세부정보 입력:
   - **서비스 계정 이름**: `eden-tts-service`
   - **서비스 계정 ID**: `eden-tts-service` (자동 생성됨)
   - **서비스 계정 설명**: `Text-to-Speech service for Garden of Eden`
3. **"만들기 및 계속하기"** 클릭

### 3-3. 권한 부여
1. "이 서비스 계정에 프로젝트 액세스 권한 부여" 섹션에서:
   - **역할 선택** 드롭다운 클릭
   - 검색창에 `Cloud Text-to-Speech` 입력
   - **"Cloud Text-to-Speech 사용자"** 역할 선택
2. **"계속"** 클릭
3. **"완료"** 클릭

---

## 4단계: 서비스 계정 키 생성 및 다운로드

### 4-1. 키 생성
1. 서비스 계정 목록에서 방금 만든 `eden-tts-service` 클릭
2. 상단 탭에서 **"키"** 탭 클릭
3. **"키 추가"** → **"새 키 만들기"** 클릭
4. 키 유형 선택:
   - **JSON** 선택 (기본값)
5. **"만들기"** 클릭
6. JSON 키 파일이 자동으로 다운로드됨

### 4-2. 키 파일 확인
- 다운로드된 파일 이름 예시: `garden-of-eden-xxxxxx-xxxxxxxx.json`
- **중요**: 이 파일은 안전하게 보관하세요! (GitHub에 절대 업로드하지 마세요)

---

## 5단계: EC2에 키 파일 업로드

### 5-1. 키 파일명 변경 (선택사항)
간단하게 하기 위해 파일명을 변경하세요:
```bash
mv ~/Downloads/garden-of-eden-xxxxxx-xxxxxxxx.json ~/Downloads/google-cloud-key.json
```

### 5-2. EC2로 파일 전송
터미널에서 다음 명령어 실행:
```bash
# 로컬에서 EC2로 키 파일 업로드
scp -i ~/.ssh/Eden_Key.pem ~/Downloads/google-cloud-key.json ubuntu@3.39.177.218:/home/ubuntu/Garden_of_Eden/backend/
```

### 5-3. 파일 권한 설정
EC2에 접속해서 권한 설정:
```bash
# EC2 접속
ssh -i ~/.ssh/Eden_Key.pem ubuntu@3.39.177.218

# 키 파일 권한 변경 (읽기 전용)
cd Garden_of_Eden/backend
chmod 600 google-cloud-key.json
```

---

## 6단계: 환경 변수 설정

### 6-1. .env 파일에 경로 추가
EC2에서 `.env` 파일 수정:
```bash
cd /home/ubuntu/Garden_of_Eden/backend
nano .env
```

다음 줄 추가:
```bash
# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS=/home/ubuntu/Garden_of_Eden/backend/google-cloud-key.json
```

저장하고 종료: `Ctrl + X` → `Y` → `Enter`

---

## 7단계: 서버 재시작 및 테스트

### 7-1. 서버 재시작
```bash
# 기존 서버 프로세스 종료
lsof -i :8000  # PID 확인
kill -9 <PID>  # PID를 실제 번호로 교체

# 서버 재시작
cd /home/ubuntu/Garden_of_Eden/backend
source venv/bin/activate
nohup python3 main.py > nohup.log 2>&1 &
```

### 7-2. 로그 확인
```bash
# TTS 초기화 확인
tail -100 nohup.log | grep -i tts

# 성공 시 다음 메시지 표시:
# ✅ Google Cloud TTS service initialized (Neural2 Korean voices)
```

### 7-3. Health Check
```bash
curl http://localhost:8000/health
```

---

## 문제 해결 (Troubleshooting)

### 문제 1: "Your default credentials were not found" 에러
**원인**: 환경 변수가 설정되지 않음
**해결**:
1. `.env` 파일에 `GOOGLE_APPLICATION_CREDENTIALS` 경로가 올바른지 확인
2. 서버 재시작 필수

### 문제 2: "Permission denied" 에러
**원인**: 키 파일 권한 문제
**해결**:
```bash
chmod 600 /home/ubuntu/Garden_of_Eden/backend/google-cloud-key.json
```

### 문제 3: "Service account does not have permission" 에러
**원인**: 서비스 계정에 권한이 없음
**해결**:
1. Google Cloud Console → IAM 및 관리자 → IAM
2. `eden-tts-service` 계정에 "Cloud Text-to-Speech 사용자" 역할 추가

---

## 비용 관련 정보

### 무료 할당량 (매월)
- **처음 100만 글자**: 무료
- **WaveNet/Neural2 음성**: 처음 100만 글자 무료

### 예상 사용량
- 평균 응답 길이: 200자
- 하루 100번 사용: 20,000자
- 한 달 (30일): 600,000자
- **결론**: 무료 할당량으로 충분함 ✅

### 비용 초과 시 (100만 글자 초과)
- Neural2 음성: 100만 글자당 $16
- 하지만 개인 사용으로는 초과할 가능성 매우 낮음

---

## 완료 체크리스트

- [ ] Google Cloud 프로젝트 생성
- [ ] Text-to-Speech API 활성화
- [ ] 서비스 계정 생성
- [ ] 서비스 계정 키 다운로드
- [ ] EC2에 키 파일 업로드
- [ ] `.env` 파일에 경로 추가
- [ ] 서버 재시작
- [ ] 로그에서 "✅ Google Cloud TTS service initialized" 확인
- [ ] 앱에서 TTS 음성 테스트

---

## Claude에게 알려주기

설정이 완료되면 Claude에게 다음과 같이 말씀해주세요:

```
설정 완료했어! 서버 재시작하고 테스트해줘
```

또는 문제가 발생하면:

```
[발생한 에러 메시지]를 복사해서 보내주세요
```

---

## 추가 참고 자료

- [Google Cloud TTS 공식 문서](https://cloud.google.com/text-to-speech/docs)
- [한국어 Neural2 음성 샘플](https://cloud.google.com/text-to-speech/docs/voices)
- [가격 계산기](https://cloud.google.com/text-to-speech/pricing)

---

**작성일**: 2025-11-07
**버전**: 1.0
**작성자**: Claude Code
