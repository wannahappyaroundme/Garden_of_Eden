# AWS EC2 배포 가이드 - Project Eden V2

**목표**: 로컬 서버 → AWS 클라우드로 이전하여 어떤 핸드폰에서든 WiFi만 있으면 사용 가능

**예상 비용**: 월 $0~10 (프리티어 사용 시)
**배포 시간**: 약 30분

---

## 📋 사전 준비

### 1. AWS 계정

- https://aws.amazon.com/ 에서 계정 생성
- 신용카드 등록 필요 (프리티어 사용 가능)

### 2. 필요한 정보

```bash
# API Keys (이미 있음)
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key  # Optional
```

---

## 🚀 배포 단계

### Step 1: EC2 인스턴스 생성 (5분)

1. **AWS Console 접속**

   - https://console.aws.amazon.com/ec2/
   - 우측 상단에서 지역 선택: **Asia Pacific (Seoul) ap-northeast-2**

2. **Launch Instance 클릭**

3. **인스턴스 설정**

   ```
   Name: project-eden-backend

   AMI (운영체제):
   - Ubuntu Server 22.04 LTS (프리티어)

   Instance type:
   - t3.micro (1 vCPU, 1GB RAM) - 프리티어
   - 또는 t3.small (2 vCPU, 2GB RAM) - 월 ~$15 (더 안정적)

   Key pair:
   - "Create new key pair" 클릭
   - Name: eden-key
   - Type: RSA
   - Format: .pem
   - 다운로드된 eden-key.pem 파일 안전하게 보관!

   Network settings:
   - ✅ Allow SSH traffic from Anywhere (0.0.0.0/0)
   - ✅ Allow HTTPS traffic from the internet
   - ✅ Allow HTTP traffic from the internet

   Storage:
   - 20 GB gp3 (프리티어: 30GB까지 무료)
   ```

4. **Launch Instance 클릭**

5. **Public IP 확인**
   - Instances 페이지에서 생성된 인스턴스 클릭
   - **Public IPv4 address** 복사 (주소 : 3.39.177.218 )
   - 이게 바로 여러분의 서버 주소입니다!

---

### Step 2: Security Group 설정 (2분)

EC2 인스턴스에 방화벽 규칙 추가:

1. EC2 인스턴스 선택 → **Security** 탭 → Security groups 클릭

2. **Inbound rules** → **Edit inbound rules**

3. 다음 규칙 추가:

   ```
   Type: Custom TCP
   Port: 8000
   Source: 0.0.0.0/0 (Anywhere IPv4)
   Description: FastAPI Backend
   ```

4. **Save rules**

---

### Step 3: 서버 접속 및 환경 설정 (10분)

1. **Key 파일 권한 설정** (로컬 Mac/Linux에서)

   ```bash
   cd ~/Downloads
   chmod 400 Eden_Key.pem
   mv Eden_Key.pem ~/.ssh/
   ```

2. **SSH 접속**

   ```bash
   # YOUR_PUBLIC_IP를 실제 IP로 변경
   ssh -i ~/.ssh/Eden_Key.pem ubuntu@3.39.177.218

   # 예시:
   # ssh -i ~/.ssh/eden-key.pem ubuntu@3.39.177.218
   ```

3. **서버에서 환경 설정**

   ```bash
   # 시스템 업데이트
   sudo apt update && sudo apt upgrade -y

   # Python 3.12 설치
   sudo apt install -y software-properties-common
   sudo add-apt-repository -y ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install -y python3.12 python3.12-venv python3.12-dev

   # Git 설치
   sudo apt install -y git

   # Nginx 설치 (리버스 프록시용)
   sudo apt install -y nginx
   ```

---

### Step 4: 코드 배포 (5분)

현재 두 가지 방법이 있습니다:

#### 방법 A: Git으로 배포 (추천)

```bash
# 1. GitHub에 코드 푸시 (로컬 Mac에서)
cd /Users/kyungsbook/Desktop/Garden_of_Eden
git add .
git commit -m "Prepare for AWS deployment"
git push origin main

# 2. 서버에서 코드 받기 (SSH 접속한 상태에서)
cd ~
git clone https://github.com/wannahappyaroundme/Garden_of_Eden.git
cd Garden_of_Eden/backend
```

#### 방법 B: SCP로 직접 전송

```bash
# 로컬 Mac에서 실행
cd /Users/kyungsbook/Desktop
scp -i ~/.ssh/eden-key.pem -r Garden_of_Eden ubuntu@3.39.177.218:~/
```

---

### Step 5: 백엔드 설정 및 실행 (5분)

서버에서 (SSH 접속 상태):

```bash
cd ~/Garden_of_Eden/backend

# 가상환경 생성
python3.12 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# .env 파일 생성
nano .env
```

`.env` 파일 내용:

```bash
# API Keys
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here

# AWS DynamoDB (Optional - 로컬 메모리 DB 사용 중)
USE_LOCAL_DYNAMODB=true

# Server
CORS_ORIGINS=*

# 저장: Ctrl+O, Enter, 종료: Ctrl+X
```

**서버 실행 테스트:**

```bash
cd ~/Garden_of_Eden/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 다른 터미널에서 테스트:
curl http://3.39.177.218:8000/health

# 작동하면 Ctrl+C로 종료
```

---

### Step 6: 백그라운드 실행 설정 (systemd) (3분)

서버가 재시작되어도 자동으로 실행되도록 설정:

```bash
sudo nano /etc/systemd/system/eden-backend.service
```

다음 내용 입력:

```ini
[Unit]
Description=Project Eden Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Garden_of_Eden/backend
Environment="PATH=/home/ubuntu/Garden_of_Eden/backend/venv/bin"
ExecStart=/home/ubuntu/Garden_of_Eden/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**서비스 시작:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable eden-backend
sudo systemctl start eden-backend

# 상태 확인
sudo systemctl status eden-backend

# 로그 확인
sudo journalctl -u eden-backend -f
```

---

### Step 7: Nginx 리버스 프록시 설정 (Optional, 권장) (2분)

HTTP를 통해 깔끔한 도메인 접근:

```bash
sudo nano /etc/nginx/sites-available/eden
```

내용:

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Nginx 활성화:**

```bash
sudo ln -s /etc/nginx/sites-available/eden /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Step 8: Flutter 앱 설정 변경 (1분)

로컬 Mac에서:

```bash
cd /Users/kyungsbook/Desktop/Garden_of_Eden/frontend/lib/config
nano api_config.dart
```

변경:

```dart
class ApiConfig {
  // 로컬 테스트용
  // static const String baseUrl = 'http://192.168.x.x:8000';

  // AWS 프로덕션용
  static const String baseUrl = 'http://YOUR_PUBLIC_IP:8000';  // 또는 http://YOUR_PUBLIC_IP (Nginx 사용 시)

  // API endpoints
  static const String chatEndpoint = '/api/v2/chat';
  static const String sttEndpoint = '/api/v2/stt';
  static const String profileEndpoint = '/api/v2/profile';
  static const String learningEventsEndpoint = '/api/v2/learning/events';
  static const String healthEndpoint = '/health';
}
```

**앱 재빌드:**

```bash
cd /Users/kyungsbook/Desktop/Garden_of_Eden/frontend
flutter clean
flutter pub get
flutter run
```

---

## ✅ 테스트

### 1. 헬스 체크

```bash
curl http://YOUR_PUBLIC_IP:8000/health
```

예상 응답:

```json
{
  "status": "healthy",
  "version": "2.1.0",
  "services": {
    "groq_stt": true,
    "gemini_llm": true,
    "edge_tts": true,
    "dynamodb": true,
    "master_processor": true
  }
}
```

### 2. 앱에서 테스트

- Flutter 앱 실행
- 마이크 버튼 누르고 "안녕하세요" 말하기
- AI 응답 들리면 성공! 🎉

---

## 💰 예상 비용 (월별)

### 프리티어 (첫 12개월)

```
EC2 t3.micro: $0
EBS 20GB: $0 (30GB까지 무료)
Data Transfer: $0 (15GB/월까지 무료)
-------------------
Total: $0/월
```

### 프리티어 이후

```
EC2 t3.micro: ~$7.50/월
EBS 20GB: ~$2/월
Data Transfer: ~$0.90/GB (15GB 초과분)
-------------------
Total: ~$10-15/월
```

### 더 안정적인 구성 (t3.small)

```
EC2 t3.small: ~$15/월
EBS 30GB: ~$3/월
Data Transfer: ~$0.90/GB
-------------------
Total: ~$20-25/월
```

---

## 🔧 유지보수

### 서버 로그 확인

```bash
# 백엔드 로그
sudo journalctl -u eden-backend -f

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 서버 재시작

```bash
sudo systemctl restart eden-backend
sudo systemctl restart nginx
```

### 코드 업데이트

```bash
cd ~/Garden_of_Eden/backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart eden-backend
```

### ChromaDB 데이터 확인

```bash
cd ~/Garden_of_Eden/backend
ls -la chroma_db/
```

---

## 🌐 도메인 연결 (Optional)

나중에 도메인을 사용하고 싶다면:

1. **도메인 구입**: Namecheap, GoDaddy 등 (~$10/년)
2. **Route 53 설정** (AWS DNS 서비스)
3. **SSL 인증서**: Let's Encrypt (무료)

자세한 내용은 필요시 추가 문서 작성 가능.

---

## ❗ 주의사항

### 1. 보안

- **SSH Key 절대 공유 금지** (eden-key.pem)
- **API Keys 노출 금지** (.env 파일은 절대 Git에 올리지 말 것)
- **정기적인 시스템 업데이트**:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

### 2. 비용 관리

- **AWS Billing Dashboard** 매일 확인
- **예산 알람 설정**: https://console.aws.amazon.com/billing/
- **프리티어 사용량 모니터링**

### 3. 백업

- **ChromaDB 데이터 백업** (주기적으로):
  ```bash
  cd ~/Garden_of_Eden/backend
  tar -czf chroma_backup_$(date +%Y%m%d).tar.gz chroma_db/
  ```

---

## 🆘 문제 해결

### 문제 1: 서버에 접속이 안돼요

```bash
# Security Group 확인
# EC2 Console → Security Groups → Inbound rules
# Port 8000이 0.0.0.0/0으로 열려있는지 확인

# 서버 상태 확인
sudo systemctl status eden-backend

# 방화벽 확인 (Ubuntu)
sudo ufw status
sudo ufw allow 8000
```

### 문제 2: 앱에서 연결이 안돼요

```bash
# 1. 헬스 체크
curl http://YOUR_PUBLIC_IP:8000/health

# 2. Flutter api_config.dart 확인
# 올바른 IP 주소인지 확인

# 3. 핸드폰과 같은 WiFi에 연결되어 있지 않아도 됨
# AWS 공개 IP는 인터넷 어디서든 접근 가능
```

### 문제 3: Gemini/Groq API 에러

```bash
# .env 파일 확인
cat ~/Garden_of_Eden/backend/.env

# 서비스 재시작
sudo systemctl restart eden-backend

# 로그 확인
sudo journalctl -u eden-backend -f
```

### 문제 4: 메모리 부족

```bash
# 메모리 사용량 확인
free -h

# ChromaDB 캐시 정리
cd ~/Garden_of_Eden/backend
rm -rf chroma_db/*

# t3.small로 업그레이드 고려
```

---

## 📊 모니터링

### CloudWatch (AWS 기본 모니터링)

- EC2 Console → Monitoring 탭
- CPU, 네트워크, 디스크 사용량 확인

### 간단한 헬스 체크 스크립트

```bash
# 로컬 Mac에서 실행
watch -n 30 curl -s http://YOUR_PUBLIC_IP:8000/health | jq
```

---

## 🚀 다음 단계

배포가 완료되었다면:

1. ✅ **앱 테스트**: 여러 핸드폰에서 접속 테스트
2. ✅ **성능 모니터링**: 1주일간 안정성 확인
3. ✅ **도메인 연결**: 원한다면 커스텀 도메인 설정
4. ✅ **HTTPS 설정**: Let's Encrypt SSL 인증서
5. ✅ **Auto Scaling**: 사용자 증가 시 자동 확장 설정

---

**축하합니다! 이제 Project Eden V2가 전 세계 어디서든 사용 가능합니다!** 🎉

궁금한 점이 있으면 언제든 물어보세요.
