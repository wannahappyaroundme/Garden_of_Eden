#!/bin/bash

# Project Eden V2 - Backend Setup Script

echo "🌟 Project Eden V2 - Backend Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.12+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment created and activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - AWS_ACCESS_KEY_ID"
    echo "   - AWS_SECRET_ACCESS_KEY"
    echo "   - GEMINI_API_KEY"
    echo "   - GROQ_API_KEY"
    echo ""
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs temp_audio

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Create DynamoDB tables: python -m services.dynamodb_service_v2"
echo "3. Run the server: python main.py"
echo ""
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo ""
