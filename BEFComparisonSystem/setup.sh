#!/bin/bash

# BEF Comparison System Setup Script
echo "Setting up BEF vs Government Schools Comparison System..."

# Navigate to project directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists in parent directory
if [ ! -d "../.venv" ]; then
    echo "Creating virtual environment..."
    cd ..
    python3 -m venv .venv
    cd BEFComparisonSystem_New
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
../.venv/bin/pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To start the application, run:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  cd BEFComparisonSystem_New"
echo "  ../.venv/bin/python app.py"
