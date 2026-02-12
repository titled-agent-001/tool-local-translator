#!/bin/bash
cd "$(dirname "$0")"

# Prefer Homebrew Python, fall back to system python3
if command -v /opt/homebrew/bin/python3 &>/dev/null; then
    PYTHON=/opt/homebrew/bin/python3
else
    PYTHON=python3
fi

# ── Ollama Setup ──
if ! command -v ollama &>/dev/null; then
    echo "❌ Ollama is not installed. Install it with: brew install ollama"
    echo "   Or visit https://ollama.com/download"
    exit 1
fi

# Start Ollama if not already running
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "🦙 Starting Ollama..."
    ollama serve &>/dev/null &
    sleep 3
fi

# Pull model if not available
MODEL="qwen2.5:7b"
if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
    echo "📥 Pulling model $MODEL (this may take a few minutes on first run)..."
    ollama pull "$MODEL"
fi

# ── Python Setup ──
# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    $PYTHON -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Launch the app
echo "🚀 Starting tool-local-translator..."
echo "   Open http://localhost:8080 in your browser"
echo ""
python app/main.py
