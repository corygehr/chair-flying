#!/bin/bash
# Chair Flying Launcher for macOS and Linux
# This shell script makes it easy to run the Chair Flying application on Unix-like systems

echo "============================================================"
echo "Chair Flying - Aviation Training Practice"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.7 or higher:"
    echo "  - macOS: Install from https://www.python.org/downloads/"
    echo "           or use Homebrew: brew install python3"
    echo "  - Linux: Use your package manager (e.g., apt install python3)"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.7"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" &> /dev/null; then
    echo "ERROR: Python 3.7 or higher is required"
    echo ""
    echo "Your current Python version: $PYTHON_VERSION"
    echo ""
    echo "Please upgrade Python from:"
    echo "  - macOS: https://www.python.org/downloads/"
    echo "           or use Homebrew: brew upgrade python3"
    echo "  - Linux: Use your package manager"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "ERROR: config.json not found"
    echo ""
    echo "Please create config.json in the same folder as this script."
    echo "See README.md for instructions."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Check if maneuvers file exists
MANEUVERS_FILE=$(python3 -c "import json; print(json.load(open('config.json'))['maneuvers_file'])" 2>/dev/null)
if [ ! -f "$MANEUVERS_FILE" ]; then
    echo "ERROR: Maneuvers file not found"
    echo ""
    echo "Please create the maneuvers file specified in config.json."
    echo "See README.md for instructions."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Run the application
echo "Starting Chair Flying..."
echo ""
python3 chair_flying.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo ""
    echo "An error occurred. Press Enter to close this window."
    read
fi
