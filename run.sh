#!/bin/bash

echo "Starting Killa Saifullah School Location Checker..."
echo "======================================================"
echo "Application will be available at: http://localhost:5001"
echo ""

# Navigate to project directory
cd /Users/macbookpro/Desktop/PMC

# Activate virtual environment and run the app
source .venv/bin/activate && python app.py

echo ""
echo "Application stopped."
