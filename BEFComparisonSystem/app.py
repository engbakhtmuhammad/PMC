import pandas as pd
import numpy as np
import math
import os
import json
import pickle
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from geopy.distance import geodesic
import folium
from folium import plugins
import uuid
from math import radians, sin, cos, asin, sqrt

app = Flask(__name__)
app.secret_key = 'bef_comparison_secret_key_2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['DATA_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER'], app.config['DATA_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Maximum search radius for analysis (in km)
MAX_SEARCH_RADIUS = 50.0

class BEFComparisonAnalyzer:
    def __init__(self):
        self.govt_schools_df = None
        self.bef_schools_df = None
        self.analysis_results = None
        
    def load_government_schools_data(self, file_path):
        """Load government schools dataset with comprehensive data"""
        try:
            # Read CSV file
            self.govt_schools_df = pd.read_csv(file_path)
            
            # Handle coordinate columns
            coord_mappings = [
                ('_xCord', ['_xCord', 'Longitude', 'longitude', 'lng', 'lon', 'x_cord', 'xCord']),
                ('_yCord', ['_yCord', 'Latitude', 'latitude', 'lat', 'y_cord', 'yCord'])
            ]
            
            for standard_name, possible_names in coord_mappings:
                if standard_name not in self.govt_schools_df.columns:
                    for alt_name in possible_names:
                        if alt_name in self.govt_schools_df.columns:
                            self.govt_schools_df[standard_name] = self.govt_schools_df[alt_name]
                            print(f"Gov: Mapped {alt_name} → {standard_name}")
                            break
                    else:
                        if standard_name == '_xCord':
                            self.govt_schools_df[standard_name] = 67.0  # Default longitude
                        else:
                            self.govt_schools_df[standard_name] = 30.0  # Default latitude

            # Standard column mappings for government schools
            column_mappings = {
                'SchoolName': ['SchoolName', 'Name', 'School_Name', 'school_name'],
                'SchoolLevel': ['SchoolLevel', 'Level', 'School_Level', 'Type'],
                'District': ['District', 'district', 'DISTRICT'],
                'Tehsil': ['Tehsil', 'tehsil', 'TEHSIL'],
                'UC': ['UC', 'uc', 'Union_Council', 'union_council'],
                'Village': ['Village', 'village', 'VILLAGE', 'VillageName'],
                'Gender': ['Gender', 'gender', 'GENDER', 'Gender_Type'],
                'BEMISCode': ['BEMISCode', 'BEMIS', 'BemisCode', 'EMIS', 'SchoolCode', 'Code'],
                'BoundaryWall': ['BoundaryWall', 'Boundary_Wall', 'boundary_wall', 'Wall'],
                'Building': ['Building', 'building', 'BUILDING', 'BuildingCondition'],
                'Rooms': ['Rooms', 'rooms', 'ROOMS', 'TotalRooms', 'ClassRooms'],
                'Toilets': ['Toilets', 'toilets', 'TOILETS', 'Toilet', 'WashRooms'],
                'Enrollment': ['Enrollment', 'enrollment', 'ENROLLMENT', 'TotalEnrollment', 'Students']
            }
            
            # Apply column mappings
            for standard_col, alternatives in column_mappings.items():
                if standard_col not in self.govt_schools_df.columns:
                    for alt_name in alternatives:
                        if alt_name in self.govt_schools_df.columns:
                            self.govt_schools_df[standard_col] = self.govt_schools_df[alt_name]
                            print(f"Gov: Mapped {alt_name} → {standard_col}")
                            break
                    else:
                        # Provide defaults for missing columns
                        if standard_col == 'SchoolName':
                            self.govt_schools_df[standard_col] = 'Unknown Government School'
                        elif standard_col == 'SchoolLevel':
                            self.govt_schools_df[standard_col] = 'Primary'
                        elif standard_col == 'BEMISCode':
                            self.govt_schools_df[standard_col] = [f"GOV-{i+1}" for i in range(len(self.govt_schools_df))]
                        else:
                            self.govt_schools_df[standard_col] = 'N/A'

            # Clean data
            self.govt_schools_df = self.govt_schools_df.dropna(subset=['_xCord', '_yCord'])
            self.govt_schools_df = self.govt_schools_df[
                (self.govt_schools_df['_xCord'].notna()) &
                (self.govt_schools_df['_yCord'].notna()) &
                (self.govt_schools_df['_xCord'] != 0) &
                (self.govt_schools_df['_yCord'] != 0)
            ]
            
            # Convert coordinates to numeric
            self.govt_schools_df['_xCord'] = pd.to_numeric(self.govt_schools_df['_xCord'], errors='coerce')
            self.govt_schools_df['_yCord'] = pd.to_numeric(self.govt_schools_df['_yCord'], errors='coerce')
            
            # Normalize district names to prevent duplicates
            if 'District' in self.govt_schools_df.columns:
                self.govt_schools_df['District'] = self.govt_schools_df['District'].astype(str).str.strip().str.title()
                print("Gov: Normalized district names to Title Case")
            
            # Remove rows with invalid coordinates after conversion
            self.govt_schools_df = self.govt_schools_df.dropna(subset=['_xCord', '_yCord'])
            
            print(f"Loaded {len(self.govt_schools_df)} government schools")
            return True, f"Successfully loaded {len(self.govt_schools_df)} government schools"
            
        except Exception as e:
            return False, f"Error loading government schools file: {str(e)}"

    def load_bef_schools_data(self, file_path):
        """Load BEF schools dataset"""
        try:
            # Read CSV file
            self.bef_schools_df = pd.read_csv(file_path)
            
            # Handle coordinate columns
            coord_mappings = [
                ('_xCord', ['_xCord', 'Longitude', 'longitude', 'lng', 'lon', 'x_cord', 'xCord']),
                ('_yCord', ['_yCord', 'Latitude', 'latitude', 'lat', 'y_cord', 'yCord'])
            ]
            
            for standard_name, possible_names in coord_mappings:
                if standard_name not in self.bef_schools_df.columns:
                    for alt_name in possible_names:
                        if alt_name in self.bef_schools_df.columns:
                            self.bef_schools_df[standard_name] = self.bef_schools_df[alt_name]
                            print(f"BEF: Mapped {alt_name} → {standard_name}")
                            break

            # Standard column mappings for BEF schools (limited data)
            column_mappings = {
                'SchoolName': ['SchoolName', 'Name', 'School_Name', 'school_name'],
                'District': ['District', 'district', 'DISTRICT'],
                'Tehsil': ['Tehsil', 'tehsil', 'TEHSIL'],
                'UC': ['UC', 'uc', 'Union_Council', 'union_council']
            }
            
            # Apply column mappings
            for standard_col, alternatives in column_mappings.items():
                if standard_col not in self.bef_schools_df.columns:
                    for alt_name in alternatives:
                        if alt_name in self.bef_schools_df.columns:
                            self.bef_schools_df[standard_col] = self.bef_schools_df[alt_name]
                            print(f"BEF: Mapped {alt_name} → {standard_col}")
                            break
                    else:
                        # Provide defaults
                        if standard_col == 'SchoolName':
                            self.bef_schools_df[standard_col] = 'Unknown BEF School'
                        else:
                            self.bef_schools_df[standard_col] = 'N/A'

            # Set all BEF schools as Primary level
            self.bef_schools_df['SchoolLevel'] = 'Primary'
            self.bef_schools_df['SchoolType'] = 'BEF'
            
            # Clean data
            self.bef_schools_df = self.bef_schools_df.dropna(subset=['_xCord', '_yCord'])
            self.bef_schools_df = self.bef_schools_df[
                (self.bef_schools_df['_xCord'].notna()) &
                (self.bef_schools_df['_yCord'].notna()) &
                (self.bef_schools_df['_xCord'] != 0) &
                (self.bef_schools_df['_yCord'] != 0)
            ]
            
            # Convert coordinates to numeric
            self.bef_schools_df['_xCord'] = pd.to_numeric(self.bef_schools_df['_xCord'], errors='coerce')
            self.bef_schools_df['_yCord'] = pd.to_numeric(self.bef_schools_df['_yCord'], errors='coerce')
            
            # Normalize district names to prevent duplicates
            if 'District' in self.bef_schools_df.columns:
                self.bef_schools_df['District'] = self.bef_schools_df['District'].astype(str).str.strip().str.title()
                print("BEF: Normalized district names to Title Case")
            
            # Remove rows with invalid coordinates after conversion
            self.bef_schools_df = self.bef_schools_df.dropna(subset=['_xCord', '_yCord'])
            
            print(f"Loaded {len(self.bef_schools_df)} BEF schools")
            return True, f"Successfully loaded {len(self.bef_schools_df)} BEF schools"
            
        except Exception as e:
            return False, f"Error loading BEF schools file: {str(e)}"

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate haversine distance between two points"""
        try:
            # Convert to float to handle string inputs
            lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
            
            # Check for invalid coordinates
            if any(pd.isna([lat1, lon1, lat2, lon2])) or any(coord == 0 for coord in [lat1, lon1, lat2, lon2]):
                return float('inf')
            
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            
            # Earth radius in kilometers
            r = 6371
            
            return r * c
            
        except (ValueError, TypeError) as e:
            print(f"Invalid coordinates: lat1={lat1}, lon1={lon1}, lat2={lat2}, lon2={lon2}, error={e}")
            return float('inf')

    def analyze_comparison(self, selected_districts=None, max_distance=MAX_SEARCH_RADIUS):
        """Analyze BEF schools in relation to government schools"""
        if self.govt_schools_df is None or self.bef_schools_df is None:
            return None
        
        print(f"=== ANALYZE_COMPARISON DEBUG START ===")
        print(f"Selected districts: {selected_districts}")
        print(f"Max distance: {max_distance}")
        
        # CRITICAL FIX: Ensure coordinates are numeric before analysis
        # Convert _yCord and _xCord to numeric values to fix "must be real number, not str" error
        for df_name, df in [("govt_schools", self.govt_schools_df), ("bef_schools", self.bef_schools_df)]:
            print(f"Converting coordinates for {df_name}")
            df['_yCord'] = pd.to_numeric(df['_yCord'], errors='coerce')
            df['_xCord'] = pd.to_numeric(df['_xCord'], errors='coerce')
            # Remove rows with invalid coordinates
            before_count = len(df)
            df.dropna(subset=['_yCord', '_xCord'], inplace=True)
            after_count = len(df)
            print(f"{df_name}: {before_count} -> {after_count} schools (removed {before_count - after_count} with invalid coords)")
        
        # Filter by districts if specified
        govt_schools = self.govt_schools_df.copy()
        bef_schools = self.bef_schools_df.copy()
        
        if selected_districts and 'all' not in selected_districts:
            govt_schools = govt_schools[govt_schools['District'].isin(selected_districts)]
            bef_schools = bef_schools[bef_schools['District'].isin(selected_districts)]
        
        print(f"After district filtering: {len(govt_schools)} govt schools, {len(bef_schools)} BEF schools")
        
        # Debug coordinate types after conversion
        if not bef_schools.empty:
            print(f"BEF coordinate types after conversion: _yCord: {type(bef_schools['_yCord'].iloc[0])}, _xCord: {type(bef_schools['_xCord'].iloc[0])}")
        if not govt_schools.empty:
            print(f"Govt coordinate types after conversion: _yCord: {type(govt_schools['_yCord'].iloc[0])}, _xCord: {type(govt_schools['_xCord'].iloc[0])}")
        
        results = {
            'bef_analysis': [],
            'district_summary': {},
            'overall_stats': {}
        }
        
        # Analyze each BEF school
        debug_count = 0
        for _, bef_school in bef_schools.iterrows():
            bef_analysis = {
                'bef_school': bef_school.to_dict(),
                'nearest_govt_schools': [],
                'distances': []
            }
            
            # Debug first few schools to confirm coordinate types
            if debug_count < 2:
                print(f"Processing BEF School {debug_count}: coords - lat: {bef_school['_yCord']} (type: {type(bef_school['_yCord'])}), lon: {bef_school['_xCord']} (type: {type(bef_school['_xCord'])})")
                debug_count += 1
            
            # Find nearest government schools
            for _, govt_school in govt_schools.iterrows():                
                distance = self.haversine_distance(
                    bef_school['_yCord'], bef_school['_xCord'],
                    govt_school['_yCord'], govt_school['_xCord']
                )
                
                if distance <= max_distance:
                    govt_data = govt_school.to_dict()
                    govt_data['distance_km'] = round(distance, 2)
                    bef_analysis['nearest_govt_schools'].append(govt_data)
                    bef_analysis['distances'].append(distance)
            
            # Sort by distance
            bef_analysis['nearest_govt_schools'].sort(key=lambda x: x['distance_km'])
            bef_analysis['min_distance'] = min(bef_analysis['distances']) if bef_analysis['distances'] else None
            bef_analysis['avg_distance'] = np.mean(bef_analysis['distances']) if bef_analysis['distances'] else None
            bef_analysis['govt_schools_nearby'] = len(bef_analysis['nearest_govt_schools'])
            
            results['bef_analysis'].append(bef_analysis)
        
        # District-wise summary
        for district in bef_schools['District'].unique():
            if pd.isna(district):
                continue
                
            district_bef = bef_schools[bef_schools['District'] == district]
            district_govt = govt_schools[govt_schools['District'] == district]
            
            results['district_summary'][district] = {
                'bef_schools_count': len(district_bef),
                'govt_schools_count': len(district_govt),
                'govt_levels': district_govt['SchoolLevel'].value_counts().to_dict() if not district_govt.empty else {}
            }
        
        # Overall statistics
        results['overall_stats'] = {
            'total_bef_schools': len(bef_schools),
            'total_govt_schools': len(govt_schools),
            'districts_analyzed': len(results['district_summary']),
            'avg_min_distance': np.mean([b['min_distance'] for b in results['bef_analysis'] if b['min_distance'] is not None])
        }
        
        self.analysis_results = results
        return results

    def create_comparison_map(self, analysis_results=None):
        """Create interactive map showing BEF and Government schools"""
        if analysis_results is None:
            analysis_results = self.analysis_results
            
        if not analysis_results or self.govt_schools_df is None or self.bef_schools_df is None:
            return None
        
        # Calculate map center
        all_lats = list(self.govt_schools_df['_yCord']) + list(self.bef_schools_df['_yCord'])
        all_lons = list(self.govt_schools_df['_xCord']) + list(self.bef_schools_df['_xCord'])
        
        center_lat = np.mean(all_lats)
        center_lon = np.mean(all_lons)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles=None
        )
        
        # Add tile layers
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='Street Map',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite View',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Color mapping for government school levels
        govt_level_colors = {
            'Primary': '#3498db',
            'Middle': '#f39c12',
            'High': '#2ecc71',
            'Higher Secondary': '#e74c3c'
        }
        
        # Add government schools
        govt_group = folium.FeatureGroup(name='Government Schools').add_to(m)
        for _, school in self.govt_schools_df.iterrows():
            level = school.get('SchoolLevel', 'Primary')
            color = govt_level_colors.get(level, '#95a5a6')
            
            popup_content = f"""
            <div style='width:300px;font-family:Arial;'>
                <h5 style='margin:0 0 8px 0;color:#2c3e50;'>{school.get('SchoolName', 'N/A')}</h5>
                <p style='margin:2px 0;font-size:12px;'><strong>BEMIS Code:</strong> {school.get('BEMISCode', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Level:</strong> {level}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>District:</strong> {school.get('District', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Tehsil:</strong> {school.get('Tehsil', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>UC:</strong> {school.get('UC', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Village:</strong> {school.get('Village', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Gender:</strong> {school.get('Gender', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Boundary Wall:</strong> {school.get('BoundaryWall', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Building:</strong> {school.get('Building', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Rooms:</strong> {school.get('Rooms', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Toilets:</strong> {school.get('Toilets', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Enrollment:</strong> {school.get('Enrollment', 'N/A')}</p>
            </div>
            """
            
            folium.Marker(
                location=[school['_yCord'], school['_xCord']],
                popup=folium.Popup(popup_content, max_width=350),
                tooltip=f"Gov: {school.get('SchoolName', 'N/A')} ({level})",
                icon=folium.Icon(
                    color='blue' if level == 'Primary' else 'orange' if level == 'Middle' else 'green' if level == 'High' else 'red',
                    icon='school',
                    prefix='fa'
                )
            ).add_to(govt_group)
        
        # Add BEF schools with distinct styling
        bef_group = folium.FeatureGroup(name='BEF Schools').add_to(m)
        for _, school in self.bef_schools_df.iterrows():
            popup_content = f"""
            <div style='width:250px;font-family:Arial;background:#fff3cd;padding:8px;border-radius:5px;'>
                <h5 style='margin:0 0 8px 0;color:#856404;'>{school.get('SchoolName', 'N/A')}</h5>
                <p style='margin:2px 0;font-size:12px;'><strong>Type:</strong> BEF Primary School</p>
                <p style='margin:2px 0;font-size:12px;'><strong>District:</strong> {school.get('District', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>Tehsil:</strong> {school.get('Tehsil', 'N/A')}</p>
                <p style='margin:2px 0;font-size:12px;'><strong>UC:</strong> {school.get('UC', 'N/A')}</p>
            </div>
            """
            
            folium.Marker(
                location=[school['_yCord'], school['_xCord']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"BEF: {school.get('SchoolName', 'N/A')}",
                icon=folium.Icon(
                    color='purple',
                    icon='graduation-cap',
                    prefix='fa'
                )
            ).add_to(bef_group)
        
        # Add distance connections for close schools (optional visualization)
        connection_group = folium.FeatureGroup(name='Connections (< 5km)', show=False).add_to(m)
        for bef_analysis in analysis_results['bef_analysis']:
            bef_school = bef_analysis['bef_school']
            for govt_school in bef_analysis['nearest_govt_schools'][:3]:  # Show only closest 3
                if govt_school['distance_km'] < 5:  # Only show very close connections
                    folium.PolyLine(
                        locations=[
                            [bef_school['_yCord'], bef_school['_xCord']],
                            [govt_school['_yCord'], govt_school['_xCord']]
                        ],
                        color='purple',
                        weight=1,
                        opacity=0.5,
                        dash_array='5,5'
                    ).add_to(connection_group)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>School Types</b></p>
        <p><i class="fa fa-school" style="color:blue"></i> Gov Primary</p>
        <p><i class="fa fa-school" style="color:orange"></i> Gov Middle</p>
        <p><i class="fa fa-school" style="color:green"></i> Gov High</p>
        <p><i class="fa fa-school" style="color:red"></i> Gov Higher Sec</p>
        <p><i class="fa fa-graduation-cap" style="color:purple"></i> BEF Primary</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m

# Global analyzer instance
analyzer = BEFComparisonAnalyzer()

def save_analyzer_state():
    """Save analyzer state to disk"""
    try:
        state_file = os.path.join(app.config['DATA_FOLDER'], 'bef_analyzer.pkl')
        
        state = {
            'govt_schools_df': analyzer.govt_schools_df,
            'bef_schools_df': analyzer.bef_schools_df,
            'analysis_results': analyzer.analysis_results
        }
        
        with open(state_file, 'wb') as f:
            pickle.dump(state, f)
        return True
    except Exception as e:
        print(f"Error saving analyzer state: {e}")
        return False

def load_analyzer_state():
    """Load analyzer state from disk"""
    try:
        state_file = os.path.join(app.config['DATA_FOLDER'], 'bef_analyzer.pkl')
        
        if os.path.exists(state_file):
            with open(state_file, 'rb') as f:
                state = pickle.load(f)
            
            analyzer.govt_schools_df = state.get('govt_schools_df')
            analyzer.bef_schools_df = state.get('bef_schools_df')
            analyzer.analysis_results = state.get('analysis_results')
            
            return True
    except Exception as e:
        print(f"Error loading analyzer state: {e}")
    return False

@app.route('/')
def index():
    # Load existing analyzer state
    load_analyzer_state()
    
    return render_template('index.html')

@app.route('/upload_govt_schools', methods=['POST'])
def upload_govt_schools():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not (file.filename.lower().endswith('.csv') or 
            file.filename.lower().endswith('.xlsx') or 
            file.filename.lower().endswith('.xls')):
        return jsonify({'success': False, 'message': 'Invalid file type. Please upload a CSV or Excel file.'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'govt_schools_{filename}')
    
    try:
        file.save(filepath)
        
        # Convert Excel to CSV if needed
        csv_filepath = filepath
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
            csv_filename = f'govt_schools_{filename.rsplit(".", 1)[0]}.csv'
            csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            df.to_csv(csv_filepath, index=False)
        
        success, message = analyzer.load_government_schools_data(csv_filepath)
        
        if success:
            save_analyzer_state()
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/upload_bef_schools', methods=['POST'])
def upload_bef_schools():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not (file.filename.lower().endswith('.csv') or 
            file.filename.lower().endswith('.xlsx') or 
            file.filename.lower().endswith('.xls')):
        return jsonify({'success': False, 'message': 'Invalid file type. Please upload a CSV or Excel file.'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'bef_schools_{filename}')
    
    try:
        file.save(filepath)
        
        # Convert Excel to CSV if needed
        csv_filepath = filepath
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
            csv_filename = f'bef_schools_{filename.rsplit(".", 1)[0]}.csv'
            csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            df.to_csv(csv_filepath, index=False)
        
        success, message = analyzer.load_bef_schools_data(csv_filepath)
        
        if success:
            save_analyzer_state()
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/status')
def get_status():
    """Get current upload status"""
    load_analyzer_state()
    
    status = {
        'govt_schools_loaded': analyzer.govt_schools_df is not None,
        'bef_schools_loaded': analyzer.bef_schools_df is not None,
        'total_govt_schools': len(analyzer.govt_schools_df) if analyzer.govt_schools_df is not None else 0,
        'total_bef_schools': len(analyzer.bef_schools_df) if analyzer.bef_schools_df is not None else 0,
        'ready_for_analysis': (analyzer.govt_schools_df is not None and analyzer.bef_schools_df is not None)
    }
    
    return jsonify(status)

@app.route('/configure')
def configure():
    # Load existing analyzer state
    load_analyzer_state()
    
    # Check if both datasets are loaded
    if analyzer.govt_schools_df is None or analyzer.bef_schools_df is None:
        flash('Please upload both government schools and BEF schools data', 'error')
        return redirect(url_for('index'))
    
    # Get available districts from both datasets
    govt_districts = set(analyzer.govt_schools_df['District'].dropna().unique())
    bef_districts = set(analyzer.bef_schools_df['District'].dropna().unique())
    available_districts = sorted(list(govt_districts.union(bef_districts)))
    
    # Calculate statistics
    district_stats = {}
    for district in available_districts:
        govt_count = len(analyzer.govt_schools_df[analyzer.govt_schools_df['District'] == district])
        bef_count = len(analyzer.bef_schools_df[analyzer.bef_schools_df['District'] == district])
        district_stats[district] = {'govt': govt_count, 'bef': bef_count}
    
    return render_template('configure.html',
                         available_districts=available_districts,
                         district_stats=district_stats,
                         total_govt_schools=len(analyzer.govt_schools_df),
                         total_bef_schools=len(analyzer.bef_schools_df))

@app.route('/load_sample_data')
def load_sample_data():
    """Load sample data for testing purposes"""
    try:
        # Create sample government schools data
        govt_sample = {
            'School Name': ['Govt Primary School A', 'Govt High School B', 'Govt Middle School C', 'Govt Secondary School D'],
            'District': ['Quetta', 'Killa Saifullah', 'Ziarat', 'Quetta'],
            'Latitude': [30.1798, 30.7058, 30.3753, 30.1995],
            'Longitude': [66.9750, 68.8658, 67.7251, 66.9595],
            'Level': ['Primary', 'Secondary', 'Middle', 'Secondary'],
            'Type': ['Government', 'Government', 'Government', 'Government']
        }
        
        # Create sample BEF schools data
        bef_sample = {
            'School Name': ['BEF School Alpha', 'BEF School Beta', 'BEF School Gamma'],
            'District': ['Quetta', 'Killa Saifullah', 'Ziarat'],
            'Latitude': [30.1850, 30.7100, 30.3800],
            'Longitude': [66.9800, 68.8700, 67.7300],
            'Level': ['Primary', 'Secondary', 'Primary'],
            'Type': ['BEF', 'BEF', 'BEF']
        }
        
        # Load into analyzer
        analyzer.govt_schools_df = pd.DataFrame(govt_sample)
        analyzer.bef_schools_df = pd.DataFrame(bef_sample)
        
        # Standardize columns
        analyzer.govt_schools_df = analyzer.govt_schools_df.rename(columns={
            'Latitude': '_yCord',
            'Longitude': '_xCord'
        })
        analyzer.bef_schools_df = analyzer.bef_schools_df.rename(columns={
            'Latitude': '_yCord', 
            'Longitude': '_xCord'
        })
        
        # Save state
        save_analyzer_state()
        
        return jsonify({
            'success': True,
            'message': 'Sample data loaded successfully',
            'govt_schools': len(analyzer.govt_schools_df),
            'bef_schools': len(analyzer.bef_schools_df)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading sample data: {str(e)}'
        })

@app.route('/districts')
def get_districts():
    """Get available districts for frontend"""
    try:
        # Load existing analyzer state
        load_analyzer_state()
        
        if analyzer.govt_schools_df is None or analyzer.bef_schools_df is None:
            return jsonify({
                'success': False,
                'message': 'Please upload both datasets first',
                'districts': []
            })
        
        # Get available districts from both datasets
        govt_districts = set(analyzer.govt_schools_df['District'].dropna().unique())
        bef_districts = set(analyzer.bef_schools_df['District'].dropna().unique())
        available_districts = sorted(list(govt_districts.union(bef_districts)))
        
        # Calculate statistics for each district
        districts_data = []
        for district in available_districts:
            govt_count = len(analyzer.govt_schools_df[analyzer.govt_schools_df['District'] == district])
            bef_count = len(analyzer.bef_schools_df[analyzer.bef_schools_df['District'] == district])
            
            districts_data.append({
                'name': district,
                'govt_schools': govt_count,
                'bef_schools': bef_count,
                'total_schools': govt_count + bef_count
            })
        
        return jsonify({
            'success': True,
            'districts': districts_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading districts: {str(e)}',
            'districts': []
        })

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Load existing analyzer state
        load_analyzer_state()
        
        if analyzer.govt_schools_df is None or analyzer.bef_schools_df is None:
            flash('Please upload both datasets first', 'error')
            return redirect(url_for('index'))
        
        # Get form data
        selected_districts = request.form.getlist('districts')
        max_distance = float(request.form.get('max_distance', MAX_SEARCH_RADIUS))
        
        print(f"=== BEF COMPARISON ANALYSIS DEBUG ===")
        print(f"Selected districts: {selected_districts}")
        print(f"Max distance: {max_distance}")
        print(f"Govt schools count: {len(analyzer.govt_schools_df)}")
        print(f"BEF schools count: {len(analyzer.bef_schools_df)}")
        
        # Perform comparison analysis
        analysis_results = analyzer.analyze_comparison(selected_districts, max_distance)
        
        if not analysis_results:
            flash('Analysis failed. Please check your data and try again.', 'error')
            return redirect(url_for('configure'))
        
        # Create map
        comparison_map = analyzer.create_comparison_map(analysis_results)
        map_html = comparison_map._repr_html_() if comparison_map else None
        
        # Extract stats for template
        stats = analysis_results.get('overall_stats', {})
        
        # Add additional computed stats for the template
        bef_analysis = analysis_results.get('bef_analysis', [])
        if bef_analysis:
            # Calculate additional stats that the template expects
            distances = [b.get('min_distance', 0) for b in bef_analysis if b.get('min_distance') is not None]
            stats['avg_distance'] = np.mean(distances) if distances else 0
            stats['schools_within_threshold'] = sum(1 for b in bef_analysis if b.get('min_distance', float('inf')) <= max_distance)
            stats['coverage_percentage'] = (stats['schools_within_threshold'] / len(bef_analysis) * 100) if bef_analysis else 0
        else:
            stats['avg_distance'] = 0
            stats['schools_within_threshold'] = 0
            stats['coverage_percentage'] = 0
        
        print(f"Stats being passed to template: {stats}")
        
        # Save state
        save_analyzer_state()
        
        return render_template('results.html',
                             analysis_results=analysis_results,
                             stats=stats,
                             selected_districts=selected_districts,
                             max_distance=max_distance,
                             map_html=map_html)
        
    except Exception as e:
        print(f"Error in analyze route: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'Error during analysis: {str(e)}', 'error')
        return redirect(url_for('configure'))

@app.route('/test_results')
def test_results():
    """Test route to verify results template with sample data"""
    # Create sample analysis results for testing
    bef_analysis = []
    for i in range(5):
        bef_analysis.append({
            'bef_school': {
                'School_Name': f'BEF School {i+1}',
                'District': 'Quetta',
                '_yCord': 30.1798 + (i * 0.01),
                '_xCord': 66.9750 + (i * 0.01),
                'School_Level': 'Middle'
            },
            'nearest_govt_schools': [
                {
                    'School_Name': f'Govt School {j+1}',
                    'District': 'Quetta', 
                    '_yCord': 30.1798 + (j * 0.005),
                    '_xCord': 66.9750 + (j * 0.005),
                    'distance_km': 0.5 + (j * 0.2)
                }
                for j in range(3)
            ],
            'distances': [0.5, 0.7, 0.9],
            'min_distance': 0.5,
            'govt_schools_nearby': 3
        })
    
    # District summary
    district_summary = {
        'Quetta': {
            'bef_schools_count': 5,
            'govt_schools_count': 150,
            'govt_levels': {'Primary': 80, 'Middle': 50, 'High': 20}
        }
    }
    
    # Overall statistics
    overall_stats = {
        'total_bef_schools': 5,
        'total_govt_schools': 150,
        'districts_analyzed': 1,
        'avg_min_distance': 0.65
    }
    
    analysis_results = {
        'bef_analysis': bef_analysis,
        'district_summary': district_summary,
        'overall_stats': overall_stats
    }
    
    # Create stats for template
    stats = overall_stats.copy()
    distances = [b.get('min_distance', 0) for b in bef_analysis if b.get('min_distance') is not None]
    stats['avg_distance'] = np.mean(distances) if distances else 0
    stats['schools_within_threshold'] = len(bef_analysis)  # All within threshold for test
    stats['coverage_percentage'] = 100.0  # 100% coverage for test
    
    return render_template('results.html',
                         analysis_results=analysis_results,
                         stats=stats,
                         selected_districts=['Quetta'],
                         max_distance=5.0,
                         map_html='<div>Test Map Placeholder</div>')

@app.route('/download_results')
def download_results():
    """Download the comparison analysis results"""
    try:
        load_analyzer_state()
        
        if not analyzer.analysis_results:
            return jsonify({'error': 'No analysis results found. Please perform an analysis first.'}), 404
        
        results = analyzer.analysis_results
        
        # Create detailed DataFrame
        df_results = []
        for bef_analysis in results['bef_analysis']:
            bef_school = bef_analysis['bef_school']
            
            row = {
                'BEF_School_Name': bef_school.get('SchoolName', ''),
                'BEF_District': bef_school.get('District', ''),
                'BEF_Tehsil': bef_school.get('Tehsil', ''),
                'BEF_UC': bef_school.get('UC', ''),
                'BEF_Latitude': bef_school.get('_yCord', ''),
                'BEF_Longitude': bef_school.get('_xCord', ''),
                'Nearby_Govt_Schools_Count': bef_analysis.get('govt_schools_nearby', 0),
                'Min_Distance_to_Govt_School_KM': bef_analysis.get('min_distance', ''),
                'Avg_Distance_to_Govt_Schools_KM': bef_analysis.get('avg_distance', ''),
                'Nearest_Govt_School_Name': '',
                'Nearest_Govt_School_BEMIS': '',
                'Nearest_Govt_School_Level': '',
                'Nearest_Distance_KM': ''
            }
            
            # Add nearest government school details
            if bef_analysis['nearest_govt_schools']:
                nearest = bef_analysis['nearest_govt_schools'][0]
                row.update({
                    'Nearest_Govt_School_Name': nearest.get('SchoolName', ''),
                    'Nearest_Govt_School_BEMIS': nearest.get('BEMISCode', ''),
                    'Nearest_Govt_School_Level': nearest.get('SchoolLevel', ''),
                    'Nearest_Distance_KM': nearest.get('distance_km', '')
                })
            
            df_results.append(row)
        
        df = pd.DataFrame(df_results)
        
        # Create download filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bef_govt_comparison_analysis_{timestamp}.csv"
        filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        # Return the file as attachment
        return send_file(filepath, 
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=filename)
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': f'Error generating download: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return '''
    <html>
    <head><title>BEF-Government Schools Comparison System</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f0f0f0;">
        <h1 style="color: #2563eb;">🏫 BEF-Government Schools Comparison System</h1>
        <h2 style="color: #059669;">✅ Server is Running!</h2>
        <p><strong>Server Time:</strong> ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
        <p><strong>Your IP:</strong> ''' + request.remote_addr + '''</p>
        <p><strong>Server Host:</strong> ''' + request.host + '''</p>
        <p style="margin-top: 30px;">
            <a href="/" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Go to Main Application
            </a>
        </p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🏫 BEF-Government Schools Comparison System")
    print("=" * 50)
    print(f"📊 Server starting...")
    print(f"🌐 Access the application at: http://localhost:5041")
    print(f"🛑 Use Ctrl+C to stop the server")
    print("=" * 50)
    
    # Get port from environment variable (for deployment) or use default
    import os
    port = int(os.environ.get('PORT', 5041))
    
    app.run(debug=False, host='0.0.0.0', port=port)
