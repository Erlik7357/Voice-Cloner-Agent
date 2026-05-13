#!/bin/bash
# Voice Cloner Test Runner for Linux/Mac

echo ""
echo "========================================"
echo "  VOICE CLONER - TEST RUNNER"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not installed"
    echo "Please install Python 3.11+ first"
    exit 1
fi

echo "Checking dependencies..."
if ! python3 -c "import TTS" 2>/dev/null; then
    echo ""
    echo "Installing required packages..."
    echo "This may take 2-5 minutes on first run."
    echo ""
    pip3 install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "Starting test pipeline..."
echo ""

python3 test_madara.py
