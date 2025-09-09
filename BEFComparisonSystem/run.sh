#!/bin/bash

# BEF Comparison System Startup Script
echo "Starting BEF vs Government Schools Comparison System..."

# Navigate to project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment and start Flask app
echo "Starting Flask application..."
echo "Access the application at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"

../.venv/bin/python app.py
