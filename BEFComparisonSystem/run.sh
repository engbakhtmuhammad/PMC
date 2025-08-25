#!/bin/bash

# BEF-Government Schools Comparison System
# Startup Script

echo "🏫 Starting BEF-Government Schools Comparison System..."
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements"
    exit 1
fi

echo "✅ Requirements installed successfully"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p downloads
mkdir -p static/css
mkdir -p templates

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Clear any existing data
echo "🧹 Clearing existing session data..."
rm -f *.pkl

echo ""
echo "🚀 Starting the application..."
echo "📍 The application will be available at: http://localhost:5000"
echo "📊 Use Ctrl+C to stop the server"
echo ""

# Start the Flask application
python app.py
