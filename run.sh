#!/bin/bash
# Launcher script for TUI Farm Game

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import textual" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install textual rich --quiet
fi

# Run the game
python main.py
