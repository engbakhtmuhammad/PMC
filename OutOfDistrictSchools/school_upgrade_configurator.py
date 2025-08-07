#!/usr/bin/env python3
"""
School Upgrade Configuration Tool
Allows easy adjustment of parameters for school upgrade analysis
"""

import pandas as pd
from enhanced_school_upgrade_tool import SchoolUpgradeAnalyzer
import argparse
import sys

def run_analysis_with_params(radius_km=25, min_enrollment=0, output_prefix="upgraded_schools"):
    """Run analysis with custom parameters"""
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                SCHOOL UPGRADE ANALYSIS                   ║
║                                                          ║
║  Parameters:                                             ║
║  - Search Radius: {radius_km} km                        ║
║  - Minimum Enrollment: {min_enrollment}                 ║
║  - Output Prefix: {output_prefix}                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Initialize analyzer
    analyzer = SchoolUpgradeAnalyzer('balochistan_census.csv')
    
    # Load data
    if not analyzer.load_data():
        print("❌ Failed to load data. Please check the file path.")
        return False
    
    # Apply enrollment filter if specified
    if min_enrollment > 0:
        original_count = len(analyzer.schools_df)
        analyzer.schools_df = analyzer.schools_df[
            analyzer.schools_df['StudentEnrollment'] >= min_enrollment
        ]
        print(f"📊 Filtered schools by minimum enrollment ({min_enrollment}): {original_count} → {len(analyzer.schools_df)} schools")
    
    # Analyze upgrade needs
    upgrade_candidates = analyzer.analyze_upgrade_needs(radius_km=radius_km)
    
    if len(upgrade_candidates) > 0:
        # Generate output files with custom prefix
        excel_file = f"{output_prefix}_r{radius_km}km.xlsx"
        map_file = f"{output_prefix}_map_r{radius_km}km.html" 
        csv_file = f"{output_prefix}_detailed_r{radius_km}km.csv"
        
        print(f"\n📊 Generating files...")
        
        # Generate Excel file
        upgraded_schools = analyzer.generate_upgraded_schools_excel(excel_file)
        
        # Create map
        analyzer.create_upgrade_map(map_file)
        
        # Save detailed CSV
        upgrade_candidates.to_csv(csv_file, index=False)
        
        print(f"""
✅ Analysis Complete! Files generated:
   📄 Excel File: {excel_file}
   🗺️  Map File: {map_file}
   📋 Detail CSV: {csv_file}
        """)
        
        # Print quick statistics
        print("📈 Quick Statistics:")
        print(f"   Total schools recommended for upgrade: {len(upgrade_candidates)}")
        
        upgrade_stats = upgrade_candidates.groupby(['CurrentLevel', 'RecommendedLevel']).size()
        for (current, recommended), count in upgrade_stats.items():
            print(f"   {current} → {recommended}: {count} schools")
        
        # District breakdown
        district_stats = upgrade_candidates['District'].value_counts()
        print(f"\n🏛️  District Breakdown:")
        for district, count in district_stats.items():
            print(f"   {district}: {count} schools")
        
        return True
    else:
        print("❌ No schools found that need upgrading based on current criteria.")
        return False

def main():
    parser = argparse.ArgumentParser(description='School Upgrade Analysis Tool')
    parser.add_argument('--radius', '-r', type=float, default=25.0, 
                       help='Search radius in kilometers (default: 25)')
    parser.add_argument('--min-enrollment', '-e', type=int, default=0,
                       help='Minimum enrollment to consider (default: 0)')
    parser.add_argument('--output', '-o', type=str, default='upgraded_schools',
                       help='Output file prefix (default: upgraded_schools)')
    parser.add_argument('--compare', '-c', action='store_true',
                       help='Run comparison with different radius values')
    
    args = parser.parse_args()
    
    if args.compare:
        print("🔄 Running comparison analysis with different radius values...")
        radii = [15, 20, 25, 30, 35]
        results = []
        
        for radius in radii:
            print(f"\n{'='*20} Radius: {radius}km {'='*20}")
            analyzer = SchoolUpgradeAnalyzer('balochistan_census.csv')
            
            if analyzer.load_data():
                candidates = analyzer.analyze_upgrade_needs(radius_km=radius)
                results.append({
                    'Radius_km': radius,
                    'Total_Upgrades': len(candidates),
                    'Primary_to_Middle': len(candidates[candidates['CurrentLevel'] == 'Primary']),
                    'Middle_to_Secondary': len(candidates[candidates['CurrentLevel'] == 'Middle']),
                    'Secondary_to_High': len(candidates[candidates['CurrentLevel'] == 'Secondary']),
                    'High_to_Higher_Secondary': len(candidates[candidates['CurrentLevel'] == 'High'])
                })
        
        # Save comparison results
        comparison_df = pd.DataFrame(results)
        comparison_df.to_csv('radius_comparison_analysis.csv', index=False)
        
        print(f"\n📊 Radius Comparison Results:")
        print(comparison_df.to_string(index=False))
        print(f"\n💾 Detailed comparison saved to: radius_comparison_analysis.csv")
        
    else:
        # Run single analysis
        success = run_analysis_with_params(
            radius_km=args.radius,
            min_enrollment=args.min_enrollment,
            output_prefix=args.output
        )
        
        if success:
            print(f"\n🎯 To run with different parameters, try:")
            print(f"   python {sys.argv[0]} --radius 30 --min-enrollment 50")
            print(f"   python {sys.argv[0]} --compare  (to compare different radius values)")

if __name__ == "__main__":
    main()
