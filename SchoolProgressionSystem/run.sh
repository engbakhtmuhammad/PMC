#!/bin/bash

# School Progression System Startup Script
# This script starts the Flask application for the School Progression Analysis System

echo "🏫 Starting School Progression Analysis System..."
echo "📍 Government of Balochistan - Education Department"
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python is not installed or not in PATH"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install requirements if they don't exist
if [ ! -d "venv" ] || [ ! -f "venv/lib/python*/site-packages/flask" ]; then
    echo "📦 Installing required packages..."
    pip install -r requirements.txt
fi

echo "🚀 Starting Flask application..."
echo "🌐 Application will be available at: http://localhost:5013"
echo "📊 Access the School Progression Analysis System in your web browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Start the Flask application
$PYTHON_CMD app.py
