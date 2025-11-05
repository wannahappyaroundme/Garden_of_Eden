# 📱 Garden of Eden - Installation Guide

Complete guide for installing and running the Garden of Eden AI mentor system.

---

## 📋 System Requirements

### Backend Server
- **Python**: 3.12+
- **Operating System**: Linux (Ubuntu 22.04 recommended) or macOS
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 10GB free space
- **Internet**: Required for API access (Gemini, Groq, gTTS)

### Frontend Mobile App
- **Android**:
  - Android 6.0 (API 23) or higher
  - 150MB free storage
  - Camera and microphone permissions

- **iOS**:
  - iOS 12.0 or higher
  - 150MB free storage
  - Camera and microphone permissions
  - Mac with Xcode (for building)

### Required API Keys (FREE)
- **Google Gemini API**: [Get Key](https://aistudio.google.com/app/apikey)
- **Groq API** (Whisper STT): [Get Key](https://console.groq.com/keys)
- **Tavily API** (Optional - Web Search): [Get Key](https://tavily.com/)

---

## 🚀 Quick Start (Local Development)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/Garden_of_Eden.git
cd Garden_of_Eden
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

**Required `.env` configuration:**
```env
# AI Service APIs
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional

# Database Configuration
USE_LOCAL_DYNAMODB=true  # Use in-memory DB for testing
AWS_REGION=ap-northeast-2  # Seoul region

# DynamoDB Table Names (for production)
DYNAMODB_PROFILES_TABLE=eden_user_profiles_v2
DYNAMODB_CONVERSATIONS_TABLE=eden_conversations_raw
DYNAMODB_LEARNING_EVENTS_TABLE=eden_learning_events
```

#### Run Backend Server
```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify backend is running:**
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

#### Install Flutter Dependencies
```bash
cd ../frontend
flutter pub get
```

#### Configure API Endpoint
Edit `lib/services/api_service.dart`:
```dart
// For local testing
static const String baseUrl = 'http://localhost:8000';

// For production (AWS)
static const String baseUrl = 'http://3.39.177.218:8000';
```

#### Run on Android/iOS
```bash
# Run on connected device
flutter run

# Build APK (Android)
flutter build apk --release

# Build iOS (requires Mac + Xcode)
flutter build ios --release
```

---

## 🐳 Docker Deployment (Recommended)

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The `docker-compose.yml` includes:
- Backend API server (port 8000)
- ChromaDB vector database (port 8001)
- Automatic restart on failure

---

## ☁️ AWS EC2 Deployment (Production)

### 1. Launch EC2 Instance

**Recommended Configuration:**
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM)
- **AMI**: Ubuntu 22.04 LTS
- **Storage**: 20GB GP3 SSD
- **Region**: ap-northeast-2 (Seoul)
- **Security Group**:
  - Port 22 (SSH) - Your IP only
  - Port 8000 (HTTP) - 0.0.0.0/0
  - Port 443 (HTTPS) - 0.0.0.0/0

### 2. Connect and Setup

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install system dependencies
sudo apt install -y git build-essential libpq-dev
```

### 3. Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/Garden_of_Eden.git
cd Garden_of_Eden/backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
nano .env  # Add your API keys and AWS credentials
```

### 4. Setup Systemd Service

```bash
sudo nano /etc/systemd/system/eden-backend.service
```

**Service configuration:**
```ini
[Unit]
Description=Garden of Eden Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Garden_of_Eden/backend
Environment="PATH=/home/ubuntu/Garden_of_Eden/backend/venv/bin"
ExecStart=/home/ubuntu/Garden_of_Eden/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable eden-backend
sudo systemctl start eden-backend
sudo systemctl status eden-backend
```

**View logs:**
```bash
sudo journalctl -u eden-backend -f
```

---

## 📊 AWS DynamoDB Setup (Production)

### 1. Create DynamoDB Tables

**Using AWS CLI:**
```bash
# User Profiles Table
aws dynamodb create-table \
    --table-name eden_user_profiles_v2 \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-2

# Conversations Table
aws dynamodb create-table \
    --table-name eden_conversations_raw \
    --attribute-definitions \
        AttributeName=conversation_id,AttributeType=S \
        AttributeName=user_id,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
    --key-schema \
        AttributeName=conversation_id,KeyType=HASH \
    --global-secondary-indexes \
        IndexName=user_id-created_at-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL} \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-2

# Learning Events Table
aws dynamodb create-table \
    --table-name eden_learning_events \
    --attribute-definitions \
        AttributeName=event_id,AttributeType=S \
        AttributeName=user_id,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
    --key-schema \
        AttributeName=event_id,KeyType=HASH \
    --global-secondary-indexes \
        IndexName=user_id-created_at-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL} \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-2

# Goal Progress Table
aws dynamodb create-table \
    --table-name eden_goal_progress \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-2
```

### 2. Configure IAM Permissions

Your EC2 instance needs DynamoDB access. Attach this policy to the EC2 IAM role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-northeast-2:*:table/eden_*"
      ]
    }
  ]
}
```

---

## 📱 Mobile App Installation

### Android (APK)

**Build APK:**
```bash
cd frontend
flutter build apk --release
```

**Install on device:**
```bash
# Via USB
flutter install

# Or transfer APK file manually
# File location: frontend/build/app/outputs/flutter-apk/app-release.apk
```

**Distribution options:**
- 📧 Email the APK file
- ☁️ Upload to Google Drive/Dropbox
- 💬 Send via messaging apps
- 🏪 Publish to Google Play Store

### iOS (IPA)

**Requirements:**
- Mac computer
- Xcode installed
- Apple Developer account (free or paid)

**Build and install:**
```bash
cd frontend

# Run on connected iPhone
flutter run

# Or build IPA for distribution
flutter build ios --release
```

**For Ad Hoc distribution:**
1. Open `frontend/ios/Runner.xcworkspace` in Xcode
2. Product → Destination → Any iOS Device (arm64)
3. Product → Archive
4. Distribute App → Ad Hoc
5. Export IPA file

**Install on iPhone:**
- Use Xcode Organizer
- AirDrop the IPA file
- Use TestFlight (requires Apple Developer Program)

---

## 🧪 Testing the Installation

### 1. Backend Health Check
```bash
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime_seconds": 123.45
}
```

### 2. Test API Endpoints
```bash
# Interactive API docs
open http://localhost:8000/docs

# Test conversation endpoint
curl -X POST http://localhost:8000/api/v2/conversation/test-user \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "persona": "adam"}'
```

### 3. Mobile App Testing

**Initial setup:**
1. Launch app on device
2. Grant camera and microphone permissions
3. Complete onboarding (6-step Socratic dialogue)
4. Select persona (Adam or Eve)

**Test conversation:**
1. Press and hold the microphone button
2. Say "안녕하세요" (Hello)
3. Release button
4. Wait 5-6 seconds for AI response
5. Verify audio playback

---

## 🔧 Troubleshooting

### Backend Issues

**Error: "API key not found"**
```bash
# Check .env file exists and has correct keys
cat backend/.env | grep API_KEY
```

**Error: "Port 8000 already in use"**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8080
```

**Error: "DynamoDB connection failed"**
- Check AWS credentials: `aws configure list`
- Verify IAM permissions
- Test with `USE_LOCAL_DYNAMODB=true` first

### Frontend Issues

**Error: "Cannot connect to server"**
- Verify backend is running: `curl http://localhost:8000/health`
- Check `api_service.dart` has correct baseUrl
- Disable any VPN or firewall

**Error: "Camera/microphone permission denied"**
- Android: Settings → Apps → Eden → Permissions
- iOS: Settings → Privacy → Camera/Microphone → Eden

**Error: "Audio recording failed"**
- Check microphone is not used by another app
- Try restarting the app
- Verify device has working microphone

---

## 📊 Performance Tuning

### Backend Optimization

**For high load (100+ concurrent users):**
```bash
# Increase workers
uvicorn main:app --workers 8

# Use Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**ChromaDB optimization:**
```python
# In backend/services/retrieval_augmented_generation_service.py
# Increase batch size for embedding
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

### Frontend Optimization

**Reduce APK size:**
```bash
# Split APKs by architecture
flutter build apk --split-per-abi
```

**Enable code shrinking:**
```dart
// In android/app/build.gradle
buildTypes {
    release {
        minifyEnabled true
        shrinkResources true
    }
}
```

---

## 🔒 Security Checklist

- [ ] Change default ports (8000 → custom)
- [ ] Use HTTPS with SSL certificate (Let's Encrypt)
- [ ] Restrict SSH access to specific IPs
- [ ] Enable DynamoDB point-in-time recovery
- [ ] Rotate API keys monthly
- [ ] Set up CloudWatch alarms
- [ ] Enable AWS WAF for DDoS protection
- [ ] Use environment variables (never commit .env)
- [ ] Enable rate limiting on API endpoints
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

---

## 📈 Monitoring

### Backend Logs
```bash
# Systemd service logs
sudo journalctl -u eden-backend -f --since "1 hour ago"

# Application logs
tail -f backend/logs/app.log
```

### AWS CloudWatch
```bash
# Install CloudWatch agent
sudo apt install amazon-cloudwatch-agent

# Configure monitoring
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### Key Metrics to Monitor
- API response time (target: <6 seconds P50)
- Error rate (target: <2%)
- CPU usage (alert if >80%)
- Memory usage (alert if >90%)
- DynamoDB throttles
- API quota usage (Gemini, Groq)

---

## 🔄 Update Deployment

### Backend Updates
```bash
cd Garden_of_Eden
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart eden-backend
```

### Frontend Updates
```bash
cd frontend
git pull origin main
flutter pub get
flutter build apk --release
# Distribute new APK to users
```

---

## 📞 Support

**Backend Status:** http://3.39.177.218:8000/health
**API Documentation:** http://3.39.177.218:8000/docs

**For issues:**
1. Check logs: `sudo journalctl -u eden-backend -n 50`
2. Verify API keys are valid
3. Test with local development setup first
4. Check GitHub Issues for known problems

---

## 📚 Additional Resources

- **Master Specification:** `PROJECT_EDEN_V2_MASTER_SPEC.md`
- **Project Overview:** `PROJECT.md`
- **AWS Deployment:** `AWS_DEPLOYMENT_GUIDE.md` (if needed)
- **API Documentation:** http://localhost:8000/docs (when backend running)

---

**Installation complete! 🎉**

Start having meaningful conversations with your AI mentor!
