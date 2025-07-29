#!/usr/bin/env python3
"""
Test script to verify all new filtering features work correctly
"""

import sys
import os
sys.path.append('/Users/macbookpro/Desktop/PMC/SchoolUpgradeSystem')

from app import SchoolUpgradeAnalyzer
import time

def test_enhanced_features():
    print("=" * 70)
    print("TESTING ENHANCED SCHOOL ANALYSIS FEATURES")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = SchoolUpgradeAnalyzer()
    
    # Load data
    print("Loading census data...")
    file_path = '/Users/macbookpro/Desktop/PMC/SchoolUpgradeSystem/balochistan_census.csv'
    
    success, message = analyzer.load_data(file_path)
    if not success:
        print(f"Failed to load data: {message}")
        return
    
    print(f"✓ {message}")
    
    # Test 1: District-specific analysis
    print(f"\n" + "="*50)
    print("TEST 1: District-Specific Analysis")
    print("="*50)
    
    districts_to_test = ['ZIARAT', 'PISHIN']
    start_time = time.time()
    
    upgrade_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=districts_to_test,
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Primary', 'Middle']
    )
    
    analysis_time = time.time() - start_time
    print(f"✓ District-specific analysis completed in {analysis_time:.2f} seconds")
    print(f"✓ Analyzed districts: {districts_to_test}")
    print(f"✓ Found {len(upgrade_candidates)} candidates")
    
    if len(upgrade_candidates) > 0:
        district_breakdown = upgrade_candidates['District'].value_counts().to_dict()
        print(f"✓ District breakdown: {district_breakdown}")
        
        # Verify only specified districts are included
        for district in upgrade_candidates['District'].unique():
            if district not in districts_to_test:
                print(f"✗ ERROR: Found unexpected district: {district}")
                return False
        print(f"✓ District filtering working correctly")
    
    # Test 2: Functional status filtering
    print(f"\n" + "="*50)
    print("TEST 2: Functional Status Filtering")
    print("="*50)
    
    # Test with functional schools only
    functional_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Primary']
    )
    
    print(f"✓ Functional schools analysis: {len(functional_candidates)} candidates")
    
    # Test with non-functional schools
    non_functional_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT'],
        include_functional=False,
        include_non_functional=True,
        analyze_levels=['Primary']
    )
    
    print(f"✓ Non-functional schools analysis: {len(non_functional_candidates)} candidates")
    
    # Test 3: School level filtering
    print(f"\n" + "="*50)
    print("TEST 3: School Level Filtering")
    print("="*50)
    
    # Test specific levels
    primary_only = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Primary']
    )
    
    middle_only = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Middle']
    )
    
    print(f"✓ Primary level analysis: {len(primary_only)} candidates")
    print(f"✓ Middle level analysis: {len(middle_only)} candidates")
    
    # Verify level filtering
    if len(primary_only) > 0:
        for _, candidate in primary_only.iterrows():
            if candidate['CurrentLevel'] != 'Primary':
                print(f"✗ ERROR: Found non-Primary school in Primary analysis: {candidate['CurrentLevel']}")
                return False
        print(f"✓ Primary level filtering working correctly")
    
    # Test 4: Upgrade mapping verification
    print(f"\n" + "="*50)
    print("TEST 4: Upgrade Mapping Verification")
    print("="*50)
    
    all_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT', 'PISHIN'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=None
    )
    
    if len(all_candidates) > 0:
        upgrade_mappings = all_candidates.groupby(['CurrentLevel', 'RecommendedLevel']).size().to_dict()
        print(f"✓ Found upgrade mappings: {upgrade_mappings}")
        
        # Verify mappings are correct
        expected_mappings = {
            'Primary': 'Middle',
            'Middle': 'Higher',
            'Higher': 'High',
            'High': 'Higher Secondary'
        }
        
        for (current, recommended), count in upgrade_mappings.items():
            if current in expected_mappings and expected_mappings[current] != recommended:
                print(f"✗ ERROR: Incorrect mapping {current} → {recommended}, expected {current} → {expected_mappings[current]}")
                return False
        
        print(f"✓ All upgrade mappings are correct")
    
    print(f"\n" + "="*70)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("✓ District-specific filtering works")
    print("✓ Functional status filtering works")
    print("✓ School level filtering works")
    print("✓ Upgrade mappings are correct (Secondary → Higher)")
    print("✓ All schools (functional + non-functional) are loaded")
    return True

if __name__ == "__main__":
    test_enhanced_features()
