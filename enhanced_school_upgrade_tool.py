import pandas as pd
import numpy as np
import math
from geopy.distance import geodesic
import folium
from folium import plugins
import json

class SchoolUpgradeAnalyzer:
    def __init__(self, census_file='balochistan_census.csv'):
        """Initialize the analyzer with census data"""
        self.census_file = census_file
        self.schools_df = None
        self.upgrade_candidates = []
        self.search_radius_km = 25  # Default search radius
        
        # School level hierarchy
        self.level_hierarchy = {
            'Primary': 1,
            'Middle': 2,
            'Secondary': 3,
            'High': 4,
            'Higher Secondary': 5
        }
        
        # Reverse mapping for upgrades
        self.upgrade_mapping = {
            'Primary': 'Middle',
            'Middle': 'Secondary',  
            'Secondary': 'High',
            'High': 'Higher Secondary'
        }
    
    def load_data(self):
        """Load and preprocess the census data"""
        print("Loading census data...")
        try:
            self.schools_df = pd.read_csv(self.census_file)
            print(f"Loaded {len(self.schools_df)} schools from census data")
            
            # Clean and preprocess data
            self.schools_df = self.schools_df.dropna(subset=['_xCord', '_yCord', 'SchoolLevel'])
            self.schools_df['StudentEnrollment'] = pd.to_numeric(self.schools_df['StudentEnrollment'], errors='coerce').fillna(0)
            
            # Filter only functional schools
            self.schools_df = self.schools_df[self.schools_df['FunctionalStatus'] == 'Functional']
            
            print(f"After filtering: {len(self.schools_df)} functional schools")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using geodesic distance"""
        try:
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        except:
            return float('inf')
    
    def find_nearby_schools(self, target_school, target_level, radius_km):
        """Find schools of target level within radius"""
        target_lat = target_school['_yCord']  # Note: _yCord is latitude
        target_lon = target_school['_xCord']  # Note: _xCord is longitude
        
        # Filter schools by level and district/tehsil for efficiency
        level_schools = self.schools_df[
            (self.schools_df['SchoolLevel'] == target_level) &
            (self.schools_df['District'] == target_school['District'])
        ].copy()
        
        if len(level_schools) == 0:
            return level_schools
        
        # Calculate distances
        level_schools['distance'] = level_schools.apply(
            lambda row: self.calculate_distance(
                target_lat, target_lon, 
                row['_yCord'], row['_xCord']
            ), axis=1
        )
        
        # Filter by radius
        nearby_schools = level_schools[level_schools['distance'] <= radius_km]
        return nearby_schools.sort_values('distance')
    
    def analyze_upgrade_needs(self, radius_km=25):
        """Analyze schools that need upgrading based on proximity and enrollment"""
        self.search_radius_km = radius_km
        upgrade_candidates = []
        
        print(f"Analyzing upgrade needs within {radius_km}km radius...")
        
        # Group schools by district and tehsil for efficient processing
        districts = self.schools_df['District'].unique()
        
        for district in districts:
            print(f"Processing {district}...")
            district_schools = self.schools_df[self.schools_df['District'] == district]
            
            # Analyze each upgrade level
            for current_level, next_level in self.upgrade_mapping.items():
                current_level_schools = district_schools[
                    district_schools['SchoolLevel'] == current_level
                ]
                
                if len(current_level_schools) == 0:
                    continue
                
                print(f"  Checking {len(current_level_schools)} {current_level} schools for upgrade to {next_level}")
                
                for _, school in current_level_schools.iterrows():
                    # Find nearby schools of the next level
                    nearby_higher = self.find_nearby_schools(school, next_level, radius_km)
                    
                    if len(nearby_higher) == 0:
                        # No higher level school nearby - this school is a candidate for upgrade
                        
                        # Find other schools of the same level nearby to compare enrollment
                        nearby_same_level = self.find_nearby_schools(school, current_level, radius_km)
                        
                        # Check if this school has the highest enrollment among nearby same-level schools
                        if len(nearby_same_level) > 1:
                            # Sort by enrollment (descending) and distance (ascending)
                            nearby_same_level = nearby_same_level.sort_values(
                                ['StudentEnrollment', 'distance'], 
                                ascending=[False, True]
                            )
                            
                            # Only recommend if this school has highest enrollment or is closest with good enrollment
                            if (school['BemisCode'] == nearby_same_level.iloc[0]['BemisCode'] or
                                school['StudentEnrollment'] >= nearby_same_level['StudentEnrollment'].quantile(0.8)):
                                
                                upgrade_candidates.append({
                                    'BemisCode': school['BemisCode'],
                                    'SchoolName': school['SchoolName'],
                                    'District': school['District'],
                                    'Tehsil': school['Tehsil'],
                                    'CurrentLevel': current_level,
                                    'RecommendedLevel': next_level,
                                    'StudentEnrollment': school['StudentEnrollment'],
                                    'Gender': school['Gender'],
                                    'Latitude': school['_yCord'],
                                    'Longitude': school['_xCord'],
                                    'NearbyHigherSchools': 0,
                                    'NearbySameLevelSchools': len(nearby_same_level) - 1,
                                    'Reason': f'No {next_level} school within {radius_km}km, highest enrollment in area'
                                })
                        else:
                            # Only school of this level in the area
                            upgrade_candidates.append({
                                'BemisCode': school['BemisCode'],
                                'SchoolName': school['SchoolName'],
                                'District': school['District'],
                                'Tehsil': school['Tehsil'],
                                'CurrentLevel': current_level,
                                'RecommendedLevel': next_level,
                                'StudentEnrollment': school['StudentEnrollment'],
                                'Gender': school['Gender'],
                                'Latitude': school['_yCord'],
                                'Longitude': school['_xCord'],
                                'NearbyHigherSchools': 0,
                                'NearbySameLevelSchools': 0,
                                'Reason': f'No {next_level} school within {radius_km}km, only {current_level} school in area'
                            })
        
        self.upgrade_candidates = pd.DataFrame(upgrade_candidates)
        print(f"\nFound {len(self.upgrade_candidates)} schools recommended for upgrade")
        return self.upgrade_candidates
    
    def generate_upgraded_schools_excel(self, output_file='upgraded_schools.xlsx'):
        """Generate Excel file with schools that should be upgraded"""
        if self.upgrade_candidates is None or len(self.upgrade_candidates) == 0:
            print("No upgrade candidates found. Run analyze_upgrade_needs() first.")
            return None
        
        # Create upgraded schools dataframe with the exact structure requested
        upgraded_schools = []
        
        for _, candidate in self.upgrade_candidates.iterrows():
            # Get original school data
            original_school = self.schools_df[
                self.schools_df['BemisCode'] == candidate['BemisCode']
            ].iloc[0]
            
            # Create upgraded school record
            upgraded_school = {
                'BemisCode': original_school['BemisCode'],
                'SessionId': original_school['SessionId'],
                'SchoolName': original_school['SchoolName'],
                'District': original_school['District'],
                'Tehsil': original_school['Tehsil'],
                'Gender': original_school['Gender'],
                'SchoolLevel': candidate['RecommendedLevel'],  # This is the upgraded level
                'FunctionalStatus': original_school['FunctionalStatus'],
                'ReasonOfNonFunctional': original_school['ReasonOfNonFunctional'],
                'StudentEnrollment': original_school['StudentEnrollment'],
                'Source': original_school['Source'],
                '_xCord': original_school['_xCord'],
                '_yCord': original_school['_yCord'],
                # Additional upgrade information
                'OriginalLevel': candidate['CurrentLevel'],
                'UpgradeReason': candidate['Reason'],
                'SearchRadius_km': self.search_radius_km
            }
            upgraded_schools.append(upgraded_school)
        
        upgraded_df = pd.DataFrame(upgraded_schools)
        
        # Save to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main upgraded schools sheet
            upgraded_df.to_excel(writer, sheet_name='Upgraded_Schools', index=False)
            
            # Summary sheet
            summary_data = {
                'Upgrade Type': [],
                'Count': [],
                'Districts Affected': []
            }
            
            for upgrade_type in upgraded_df['OriginalLevel'].unique():
                type_data = upgraded_df[upgraded_df['OriginalLevel'] == upgrade_type]
                summary_data['Upgrade Type'].append(f"{upgrade_type} to {type_data['SchoolLevel'].iloc[0]}")
                summary_data['Count'].append(len(type_data))
                summary_data['Districts Affected'].append(len(type_data['District'].unique()))
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # District-wise breakdown
            district_summary = upgraded_df.groupby(['District', 'OriginalLevel']).size().reset_index(name='Count')
            district_summary.to_excel(writer, sheet_name='District_Breakdown', index=False)
        
        print(f"Upgraded schools Excel file saved as: {output_file}")
        print(f"Total schools to be upgraded: {len(upgraded_df)}")
        
        # Print summary
        print("\nUpgrade Summary:")
        for upgrade_type in upgraded_df['OriginalLevel'].unique():
            type_data = upgraded_df[upgraded_df['OriginalLevel'] == upgrade_type]
            target_level = type_data['SchoolLevel'].iloc[0]
            print(f"  {upgrade_type} → {target_level}: {len(type_data)} schools")
        
        return upgraded_df
    
    def create_upgrade_map(self, output_file='school_upgrades_map.html'):
        """Create an interactive map showing upgrade recommendations"""
        if self.upgrade_candidates is None or len(self.upgrade_candidates) == 0:
            print("No upgrade candidates found. Run analyze_upgrade_needs() first.")
            return None
        
        # Calculate center point
        center_lat = self.upgrade_candidates['Latitude'].mean()
        center_lon = self.upgrade_candidates['Longitude'].mean()
        
        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
        
        # Color mapping for upgrade types
        upgrade_colors = {
            'Primary': 'blue',
            'Middle': 'green',
            'Secondary': 'orange',
            'High': 'red'
        }
        
        # Add markers for each upgrade candidate
        for _, school in self.upgrade_candidates.iterrows():
            color = upgrade_colors.get(school['CurrentLevel'], 'gray')
            
            popup_html = f"""
            <b>{school['SchoolName']}</b><br>
            BEMIS: {school['BemisCode']}<br>
            District: {school['District']}<br>
            Tehsil: {school['Tehsil']}<br>
            <hr>
            <b>Upgrade:</b> {school['CurrentLevel']} → {school['RecommendedLevel']}<br>
            <b>Enrollment:</b> {school['StudentEnrollment']}<br>
            <b>Reason:</b> {school['Reason']}
            """
            
            folium.Marker(
                location=[school['Latitude'], school['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{school['SchoolName']} ({school['CurrentLevel']} → {school['RecommendedLevel']})",
                icon=folium.Icon(color=color, icon='arrow-up')
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 140px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px">
        <p><b>School Upgrade Recommendations</b></p>
        <p><i class="fa fa-map-marker" style="color:blue"></i> Primary to Middle</p>
        <p><i class="fa fa-map-marker" style="color:green"></i> Middle to Secondary</p>
        <p><i class="fa fa-map-marker" style="color:orange"></i> Secondary to High</p>
        <p><i class="fa fa-map-marker" style="color:red"></i> High to Higher Secondary</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        m.save(output_file)
        print(f"Interactive map saved as: {output_file}")
        return m

# Main execution function
def main():
    # Initialize analyzer
    analyzer = SchoolUpgradeAnalyzer('balochistan_census.csv')
    
    # Load data
    if not analyzer.load_data():
        print("Failed to load data. Please check the file path.")
        return
    
    # Analyze upgrade needs
    print("\n" + "="*50)
    print("SCHOOL UPGRADE ANALYSIS")
    print("="*50)
    
    upgrade_candidates = analyzer.analyze_upgrade_needs(radius_km=25)
    
    if len(upgrade_candidates) > 0:
        # Generate upgraded schools Excel file
        print("\n" + "-"*30)
        print("GENERATING EXCEL FILE")
        print("-"*30)
        upgraded_schools = analyzer.generate_upgraded_schools_excel('upgraded_schools_final.xlsx')
        
        # Create interactive map
        print("\n" + "-"*30)
        print("CREATING INTERACTIVE MAP")
        print("-"*30)
        analyzer.create_upgrade_map('school_upgrades_visualization.html')
        
        # Save detailed analysis
        upgrade_candidates.to_csv('upgrade_analysis_detailed.csv', index=False)
        print("Detailed analysis saved as: upgrade_analysis_detailed.csv")
        
    else:
        print("No schools found that need upgrading based on current criteria.")

if __name__ == "__main__":
    main()
