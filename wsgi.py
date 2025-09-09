#!/usr/bin/env python3
"""
WSGI entry point for PMC Dashboard deployment
"""
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app from production dashboard
from dashboard_production import app

# WSGI application entry point
application = app

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 5040))
    app.run(host='0.0.0.0', port=port, debug=False)
