#!/bin/bash
echo "🏫 Starting Balochistan School Feasibility Analysis System..."
echo "=========================================================="
echo ""
echo "📍 System URL: http://localhost:5011"
echo "🔍 Health Check: http://localhost:5011/health"
echo ""
echo "📊 Features:"
echo "   • CSV Upload and Validation"
echo "   • Feasibility Analysis by School Level"
echo "   • Interactive Map Visualization"
echo "   • Download Analysis Reports"
echo ""
echo "Starting server..."
echo ""

# Change to the SchoolFeasibilitySystem directory
cd "$(dirname "$0")"

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Setting up Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "📦 Installing/updating dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Start the Flask application
echo "🚀 Starting Flask server on port 5011..."
echo ""
python app.py
