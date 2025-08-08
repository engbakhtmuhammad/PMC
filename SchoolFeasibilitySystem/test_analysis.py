#!/usr/bin/env python3
"""
Test script to reproduce the analysis error
"""
import requests
import os

BASE_URL = "http://localhost:5011"

def test_analysis():
    print("🧪 Testing School Feasibility Analysis...")
    
    # Step 1: Load sample data
    print("1. Loading sample data...")
    response = requests.get(f"{BASE_URL}/load-sample")
    if response.status_code != 200:
        print(f"❌ Failed to load sample data: {response.status_code}")
        return False
    print("✅ Sample data loaded")
    
    # Step 2: Test analysis with valid coordinates
    print("2. Testing analysis with coordinates...")
    
    form_data = {
        'school_level': 'Primary',
        'min_distance': '2.0',
        'latitudes[]': ['30.1975', '30.2000'],
        'longitudes[]': ['66.9995', '67.0000'],
        'location_names[]': ['Test Site 1', 'Test Site 2']
    }
    
    print(f"Sending form data: {form_data}")
    
    response = requests.post(f"{BASE_URL}/analyze", data=form_data)
    
    if response.status_code == 200:
        print("✅ Analysis completed successfully!")
        return True
    else:
        print(f"❌ Analysis failed with status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        return False

if __name__ == "__main__":
    try:
        test_analysis()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
