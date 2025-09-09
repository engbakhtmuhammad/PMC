#!/bin/bash

echo "🏫 BEF Schools Comparison System - Local Startup"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if required packages are installed
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p downloads

# Start the application
echo "🚀 Starting the application..."
echo "🌐 Access your system at: http://localhost:5040"
echo "🌍 Access from other devices at: http://YOUR_IP:5040"
echo "🛑 Press Ctrl+C to stop"
echo "================================================"

python3 app.py
