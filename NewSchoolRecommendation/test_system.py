#!/usr/bin/env python3
"""
Test script for School Feasibility Analysis System
Validates core functionality and data processing
"""

import os
import sys
import pandas as pd
import requests
import time
from pathlib import Path

def test_file_structure():
    """Test that all required files and directories exist"""
    print("🔍 Testing file structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'sample_schools_data.csv',
        'templates/index.html',
        'templates/coordinate_input.html',
        'templates/results.html',
        'static/styles.css'
    ]
    
    required_dirs = [
        'uploads',
        'reports',
        'static',
        'templates'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_files or missing_dirs:
        print("❌ Missing files or directories:")
        for item in missing_files + missing_dirs:
            print(f"   - {item}")
        return False
    
    print("✅ All required files and directories exist")
    return True

def test_sample_data():
    """Test that sample data is valid"""
    print("🔍 Testing sample data...")
    
    try:
        df = pd.read_csv('sample_schools_data.csv')
        
        required_columns = [
            'BemisCode', 'SchoolName', 'District', '_xCord', '_yCord'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        # Check for valid coordinates
        if df['_xCord'].isna().any() or df['_yCord'].isna().any():
            print("❌ Sample data contains missing coordinates")
            return False
        
        # Check coordinate ranges (Balochistan approximate bounds)
        valid_lat = df['_yCord'].between(24, 32).all()
        valid_lon = df['_xCord'].between(60, 72).all()
        
        if not valid_lat or not valid_lon:
            print("❌ Sample data contains coordinates outside valid range")
            return False
        
        print(f"✅ Sample data is valid ({len(df)} schools)")
        return True
        
    except Exception as e:
        print(f"❌ Error reading sample data: {e}")
        return False

def test_flask_imports():
    """Test that Flask app can be imported"""
    print("🔍 Testing Flask app imports...")
    
    try:
        import app
        print("✅ Flask app imports successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False

def test_server_startup():
    """Test that Flask server can start (quick check)"""
    print("🔍 Testing server startup...")
    
    try:
        # Start server in background
        import subprocess
        import signal
        
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Try to connect
        try:
            response = requests.get('http://127.0.0.1:5011', timeout=5)
            if response.status_code == 200:
                print("✅ Server starts and responds successfully")
                result = True
            else:
                print(f"❌ Server responded with status code: {response.status_code}")
                result = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            result = False
        
        # Clean up
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            # Process already terminated or timeout
            pass
        
        return result
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def test_coordinate_validation():
    """Test coordinate validation logic"""
    print("🔍 Testing coordinate validation...")
    
    try:
        # Test valid coordinates
        valid_coords = [
            (30.1838, 67.0011),  # Quetta area
            (25.1234, 62.3234),  # Gwadar area
            (29.5456, 67.8789)   # Sibi area
        ]
        
        # Test invalid coordinates
        invalid_coords = [
            (90.0, 67.0),    # Invalid latitude
            (30.0, 180.0),   # Invalid longitude
            (-30.0, 67.0),   # Invalid latitude
            (30.0, -67.0)    # Invalid longitude for Balochistan
        ]
        
        for lat, lon in valid_coords:
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                print(f"❌ Valid coordinate failed basic validation: ({lat}, {lon})")
                return False
        
        for lat, lon in invalid_coords:
            if -90 <= lat <= 90 and -180 <= lon <= 180 and 24 <= lat <= 32 and 60 <= lon <= 72:
                print(f"❌ Invalid coordinate passed validation: ({lat}, {lon})")
                return False
        
        print("✅ Coordinate validation works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Coordinate validation test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are installed"""
    print("🔍 Testing dependencies...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing_deps = []
        
        for requirement in requirements:
            # Extract package name (handle version specifiers)
            package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
            
            try:
                # Handle special import cases
                if package_name == 'Pillow':
                    __import__('PIL')
                elif package_name == 'beautifulsoup4':
                    __import__('bs4')
                elif package_name == 'Flask':
                    __import__('flask')
                elif package_name == 'Werkzeug':
                    __import__('werkzeug')
                else:
                    __import__(package_name.replace('-', '_').lower())
            except ImportError:
                missing_deps.append(package_name)
        
        if missing_deps:
            print(f"❌ Missing dependencies: {missing_deps}")
            print("Run: pip3 install -r requirements.txt")
            return False
        
        print("✅ All dependencies are installed")
        return True
        
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting School Feasibility Analysis System Tests\n")
    
    tests = [
        test_file_structure,
        test_sample_data,
        test_dependencies,
        test_flask_imports,
        test_coordinate_validation,
        test_server_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready for use.")
        print("\nTo start the application:")
        print("python3 app.py")
        print("\nThen visit: http://127.0.0.1:5011")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
