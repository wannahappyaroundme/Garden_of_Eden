#!/bin/bash

# Project Eden V2 - Local Backend Setup Script
# This script sets up the backend to run locally without Docker

echo "🌟 Project Eden V2 - Local Backend Setup"
echo "========================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python found"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env from template..."

    cat > .env << 'EOF'
# Project Eden V2 - Environment Variables

# Google Gemini API (FREE - get from https://ai.google.dev/)
GEMINI_API_KEY=your_gemini_key_here

# Groq API for Whisper STT (FREE - get from https://console.groq.com/)
GROQ_API_KEY=your_groq_key_here

# AWS Credentials (optional - can use DynamoDB Local)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# DynamoDB Configuration
USE_LOCAL_DYNAMODB=true
DYNAMODB_ENDPOINT=http://localhost:8000
DYNAMODB_TABLE_PREFIX=eden_v2_

# Edge TTS (no API key needed - free unlimited)

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:*,http://192.168.*:*

EOF

    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys:"
    echo "   - GEMINI_API_KEY (get from https://ai.google.dev/)"
    echo "   - GROQ_API_KEY (get from https://console.groq.com/)"
    echo ""
    echo "   Run: nano .env"
    echo ""
else
    echo "✅ .env file exists"
    echo ""
fi

# Check if using local DynamoDB
echo "🗄️  DynamoDB Configuration..."
if grep -q "USE_LOCAL_DYNAMODB=true" .env; then
    echo "   Using LOCAL DynamoDB (no AWS needed)"
    echo "   ⚠️  Note: You'll need to install DynamoDB Local separately"
    echo "   Or change USE_LOCAL_DYNAMODB=false to use AWS"
else
    echo "   Using AWS DynamoDB"
    echo "   Make sure AWS credentials are set in .env"
fi
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys: nano .env"
echo "2. Start the server: ./start_local.sh"
echo "   OR: source venv/bin/activate && python main.py"
echo ""
