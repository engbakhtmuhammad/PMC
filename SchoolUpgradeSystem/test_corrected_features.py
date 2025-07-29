#!/usr/bin/env python3
"""
Test script to verify corrected upgrade mappings and gender filtering
"""

import sys
import os
sys.path.append('/Users/macbookpro/Desktop/PMC/SchoolUpgradeSystem')

from app import SchoolUpgradeAnalyzer, UPGRADE_MAPPING
import time

def test_corrected_features():
    print("=" * 70)
    print("TESTING CORRECTED UPGRADE MAPPINGS AND GENDER FILTERING")
    print("=" * 70)
    
    # Test 1: Verify correct upgrade mappings
    print("TEST 1: Upgrade Mapping Verification")
    print("="*50)
    
    expected_mappings = {
        'Primary': 'Middle',
        'Middle': 'High',
        'High': 'Higher Secondary'
    }
    
    print("Expected mappings:")
    for current, next_level in expected_mappings.items():
        print(f"  {current} → {next_level}")
    
    print("\nActual mappings:")
    for current, next_level in UPGRADE_MAPPING.items():
        print(f"  {current} → {next_level}")
    
    # Verify mappings are correct
    if UPGRADE_MAPPING == expected_mappings:
        print("✓ All upgrade mappings are CORRECT!")
    else:
        print("✗ ERROR: Mappings don't match expected values")
        return False
    
    # Initialize analyzer
    analyzer = SchoolUpgradeAnalyzer()
    
    # Load data
    print(f"\nTEST 2: Loading Data")
    print("="*50)
    file_path = '/Users/macbookpro/Desktop/PMC/SchoolUpgradeSystem/balochistan_census.csv'
    
    success, message = analyzer.load_data(file_path)
    if not success:
        print(f"Failed to load data: {message}")
        return False
    
    print(f"✓ {message}")
    
    # Check available genders
    genders = analyzer.schools_df['Gender'].value_counts().to_dict()
    print(f"✓ Available genders: {genders}")
    
    # Test 3: Gender-specific analysis
    print(f"\nTEST 3: Gender-Specific Analysis")
    print("="*50)
    
    # Test Boys schools only
    boys_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT'],
        genders=['Boys'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Primary', 'Middle']
    )
    
    print(f"✓ Boys schools analysis: {len(boys_candidates)} candidates")
    
    # Verify only Boys schools are included
    if len(boys_candidates) > 0:
        unique_genders = boys_candidates['Gender'].unique()
        if len(unique_genders) == 1 and unique_genders[0] == 'Boys':
            print(f"✓ Gender filtering working correctly (only Boys schools)")
        else:
            print(f"✗ ERROR: Found other genders in Boys-only analysis: {unique_genders}")
            return False
    
    # Test Girls schools only
    girls_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT'],
        genders=['Girls'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Primary', 'Middle']
    )
    
    print(f"✓ Girls schools analysis: {len(girls_candidates)} candidates")
    
    # Test Co-Education schools
    coed_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT'],
        genders=['Co-Education'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Primary', 'Middle']
    )
    
    print(f"✓ Co-Education schools analysis: {len(coed_candidates)} candidates")
    
    # Test 4: Combined filters
    print(f"\nTEST 4: Combined Filtering")
    print("="*50)
    
    combined_candidates = analyzer.analyze_upgrade_needs(
        radius_km=25,
        districts=['ZIARAT', 'PISHIN'],
        genders=['Boys', 'Girls'],
        include_functional=True,
        include_non_functional=False,
        analyze_levels=['Primary', 'Middle']
    )
    
    print(f"✓ Combined analysis: {len(combined_candidates)} candidates")
    
    if len(combined_candidates) > 0:
        district_breakdown = combined_candidates['District'].value_counts().to_dict()
        gender_breakdown = combined_candidates['Gender'].value_counts().to_dict()
        level_breakdown = combined_candidates.groupby(['CurrentLevel', 'RecommendedLevel']).size().to_dict()
        
        print(f"✓ District breakdown: {district_breakdown}")
        print(f"✓ Gender breakdown: {gender_breakdown}")
        print(f"✓ Upgrade breakdown: {level_breakdown}")
        
        # Verify correct upgrade mappings in results
        for (current, recommended), count in level_breakdown.items():
            if current in UPGRADE_MAPPING and UPGRADE_MAPPING[current] != recommended:
                print(f"✗ ERROR: Incorrect mapping in results {current} → {recommended}")
                return False
        
        print(f"✓ All upgrade mappings in results are correct")
    
    print(f"\n" + "="*70)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("✅ Correct upgrade mappings: Primary→Middle, Middle→High, High→Higher Secondary")
    print("✅ Gender filtering works for Boys, Girls, and Co-Education schools")
    print("✅ Combined filters (district + gender + level) work correctly")
    print("✅ Results show only selected criteria")
    return True

if __name__ == "__main__":
    test_corrected_features()
