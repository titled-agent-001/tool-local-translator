#!/bin/bash
cd "$(dirname "$0")"

# Prefer Homebrew Python, fall back to system python3
if command -v /opt/homebrew/bin/python3 &>/dev/null; then
    PYTHON=/opt/homebrew/bin/python3
else
    PYTHON=python3
fi

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
