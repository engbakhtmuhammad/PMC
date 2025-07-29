#!/bin/bash

echo "Setting up Killa Saifullah School Location Checker..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the Flask app: python app.py"
echo "3. Open your browser and go to: http://localhost:5000"
echo ""
echo "Make sure your Excel file has these columns:"
echo "- School Name (or similar)"
echo "- BEMIS Code (or Code)"
echo "- Latitude (or Lat)"
echo "- Longitude (or Lon/Lng)"
echo "- District"
