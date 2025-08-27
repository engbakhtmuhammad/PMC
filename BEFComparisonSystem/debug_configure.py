#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import analyzer, load_analyzer_state

def debug_configure():
    print("=== Debugging Configure Function ===")
    
    # Load analyzer state
    print("1. Loading analyzer state...")
    load_analyzer_state()
    
    print(f"   Govt schools loaded: {analyzer.govt_schools_df is not None}")
    print(f"   BEF schools loaded: {analyzer.bef_schools_df is not None}")
    
    if analyzer.govt_schools_df is not None:
        print(f"   Govt schools count: {len(analyzer.govt_schools_df)}")
        print(f"   Govt schools columns: {list(analyzer.govt_schools_df.columns)}")
        
        # Check if District column exists
        if 'District' in analyzer.govt_schools_df.columns:
            govt_districts = set(analyzer.govt_schools_df['District'].dropna().unique())
            print(f"   Govt districts: {list(govt_districts)[:5]}...")
        else:
            print("   ERROR: No District column in government schools!")
    
    if analyzer.bef_schools_df is not None:
        print(f"   BEF schools count: {len(analyzer.bef_schools_df)}")
        print(f"   BEF schools columns: {list(analyzer.bef_schools_df.columns)}")
        
        # Check if District column exists
        if 'District' in analyzer.bef_schools_df.columns:
            bef_districts = set(analyzer.bef_schools_df['District'].dropna().unique())
            print(f"   BEF districts: {list(bef_districts)[:5]}...")
        else:
            print("   ERROR: No District column in BEF schools!")
    
    # Test the configure logic
    if analyzer.govt_schools_df is not None and analyzer.bef_schools_df is not None:
        print("\n2. Testing configure logic...")
        
        if 'District' in analyzer.govt_schools_df.columns and 'District' in analyzer.bef_schools_df.columns:
            govt_districts = set(analyzer.govt_schools_df['District'].dropna().unique())
            bef_districts = set(analyzer.bef_schools_df['District'].dropna().unique())
            available_districts = sorted(list(govt_districts.union(bef_districts)))
            
            print(f"   Available districts: {available_districts[:10]}...")
            print(f"   Total districts: {len(available_districts)}")
            
            # Calculate statistics
            district_stats = {}
            for district in available_districts[:5]:  # Just first 5 for testing
                govt_count = len(analyzer.govt_schools_df[analyzer.govt_schools_df['District'] == district])
                bef_count = len(analyzer.bef_schools_df[analyzer.bef_schools_df['District'] == district])
                district_stats[district] = {'govt': govt_count, 'bef': bef_count}
                print(f"   {district}: {govt_count} govt, {bef_count} bef")
        else:
            print("   ERROR: Missing District columns!")
    else:
        print("   ERROR: One or both datasets not loaded!")

if __name__ == "__main__":
    debug_configure() 