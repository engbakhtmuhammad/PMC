#!/bin/bash

# School Progression System Setup Script
# This script sets up the development environment for the School Progression Analysis System

echo "🏫 School Progression Analysis System - Setup"
echo "📍 Government of Balochistan - Education Department"
echo "=========================================="
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python 3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Python found: $(python --version)"
else
    echo "❌ Error: Python is not installed or not in PATH"
    echo "Please install Python 3.8 or higher and try again."
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

echo ""

# Check if pip is available
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ Error: pip is not installed"
    echo "Please install pip and try again."
    exit 1
fi

echo "✅ pip found: $($PIP_CMD --version)"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
$PYTHON_CMD -m venv venv

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment created successfully"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing required packages..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All packages installed successfully"
else
    echo "❌ Failed to install some packages"
    echo "Please check the error messages above and try again."
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Run: ./run.sh"
echo "   OR"
echo "2. Run: source venv/bin/activate && python app.py"
echo ""
echo "The application will be available at: http://localhost:5013"
echo ""
echo "📖 For more information, see README.md"
echo "=========================================="
