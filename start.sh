#!/bin/bash

# NRC Tournament Program Launcher Script
# This script starts the NRC Tournament Program

echo "🎯 Starting NRC Tournament Program..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the launcher
python3 launcher.py

# If the launcher exits, wait for user input before closing
echo ""
echo "Press Enter to close this window..."
read
