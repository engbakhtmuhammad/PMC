#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""
import os
import sys

# Add the BEFComparisonSystem directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'BEFComparisonSystem'))

# Import the Flask app
from app import app

# WSGI application entry point
application = app

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 5040))
    app.run(host='0.0.0.0', port=port, debug=False)
