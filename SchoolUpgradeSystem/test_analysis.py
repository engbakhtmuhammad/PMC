#!/usr/bin/env python3
"""
Quick test script to verify the optimized analysis function
"""

import sys
import os
sys.path.append('/Users/macbookpro/Desktop/PMC/SchoolUpgradeSystem')

from app import SchoolUpgradeAnalyzer
import time

def test_analysis():
    print("=" * 60)
    print("TESTING OPTIMIZED SCHOOL ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SchoolUpgradeAnalyzer()
    
    # Load data
    print("Loading census data...")
    file_path = '/Users/macbookpro/Desktop/PMC/SchoolUpgradeSystem/balochistan_census.csv'
    
    start_time = time.time()
    success, message = analyzer.load_data(file_path)
    load_time = time.time() - start_time
    
    if not success:
        print(f"Failed to load data: {message}")
        return
    
    print(f"✓ Data loaded successfully in {load_time:.2f} seconds")
    print(f"✓ {message}")
    
    # Quick data overview
    df = analyzer.schools_df
    print(f"\nData Overview:")
    print(f"- Total schools: {len(df)}")
    print(f"- Districts: {df['District'].nunique()}")
    print(f"- School levels: {df['SchoolLevel'].value_counts().to_dict()}")
    print(f"- Functional status: {df['FunctionalStatus'].value_counts().to_dict()}")
    
    # Test analysis with small radius for speed
    print(f"\nStarting analysis (25km radius)...")
    start_time = time.time()
    
    try:
        upgrade_candidates = analyzer.analyze_upgrade_needs(radius_km=25, max_candidates=100)
        analysis_time = time.time() - start_time
        
        print(f"✓ Analysis completed in {analysis_time:.2f} seconds")
        print(f"✓ Found {len(upgrade_candidates)} upgrade candidates")
        
        if len(upgrade_candidates) > 0:
            print(f"\nSample recommendations:")
            for i, candidate in upgrade_candidates.head(3).iterrows():
                print(f"- {candidate['SchoolName']} ({candidate['District']})")
                print(f"  {candidate['CurrentLevel']} → {candidate['RecommendedLevel']}")
                print(f"  Reason: {candidate['UpgradeReason']}")
                print()
        
        print("=" * 60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True
        
    except Exception as e:
        analysis_time = time.time() - start_time
        print(f"✗ Analysis failed after {analysis_time:.2f} seconds")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_analysis()
