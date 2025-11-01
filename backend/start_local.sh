#!/bin/bash

# Project Eden V2 - Start Backend Locally

echo "🚀 Starting Project Eden V2 Backend..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "   Run ./setup_local.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "   Run ./setup_local.sh first"
    exit 1
fi

# Check if API keys are set
if grep -q "your_gemini_key_here" .env || grep -q "your_groq_key_here" .env; then
    echo "⚠️  WARNING: API keys not configured in .env"
    echo "   The server will start but AI features won't work"
    echo ""
    echo "   Edit .env and add:"
    echo "   - GEMINI_API_KEY"
    echo "   - GROQ_API_KEY"
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Starting server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

# Start server
python main.py
