import pandas as pd
import numpy as np
import math
import os
import json
import pickle
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from werkzeug.utils import secure_filename
from geopy.distance import geodesic
import folium
from folium import plugins
import uuid
from math import radians, sin, cos, asin, sqrt

app = Flask(__name__)
app.secret_key = 'school_progression_secret_key_2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['DATA_FOLDER'] = 'session_data'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Session configuration
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'school_progression:'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER'], app.config['DATA_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# School level progression mapping
PROGRESSION_MAP = {
    'Primary': 'Middle',
    'Middle': 'High', 
    'High': 'Higher Secondary',
    'Higher Secondary': None  # No progression beyond this
}

# Reverse progression mapping (for finding feeder schools)
FEEDER_MAP = {
    'Middle': 'Primary',
    'High': 'Middle',
    'Higher Secondary': 'High'
}

# Maximum search radius for finding progression schools (in km)
MAX_SEARCH_RADIUS = 25.0

class SchoolProgressionAnalyzer:
    def __init__(self):
        self.all_schools_df = None
        self.target_schools_df = None
        self.analysis_id = None
        # Performance indices
        self.level_index = {}
        self.level_coords = {}  # level -> (lat_array, lon_array)
        
    def build_level_index(self):
        """Pre-build per-level DataFrame and numpy coordinate arrays for fast lookup."""
        self.level_index = {}
        self.level_coords = {}
        if self.all_schools_df is None or 'SchoolLevel' not in self.all_schools_df.columns:
            return
        for level, df_level in self.all_schools_df.groupby('SchoolLevel'):
            df_level = df_level.reset_index(drop=True)
            self.level_index[level] = df_level
            self.level_coords[level] = (
                df_level['_yCord'].to_numpy(dtype=float),
                df_level['_xCord'].to_numpy(dtype=float)
            )
        print(f"Built level index for levels: {list(self.level_index.keys())}")
    
    def load_all_schools_data(self, file_path):
        """Load the complete schools dataset"""
        try:
            # Read CSV file
            self.all_schools_df = pd.read_csv(file_path)
            
            # Handle coordinate columns with various possible names
            coord_mappings = [
                ('_xCord', ['_xCord', 'Longitude', 'longitude', 'lng', 'lon', 'x_cord', 'xCord']),
                ('_yCord', ['_yCord', 'Latitude', 'latitude', 'lat', 'y_cord', 'yCord'])
            ]
            
            for standard_name, possible_names in coord_mappings:
                if standard_name not in self.all_schools_df.columns:
                    for alt_name in possible_names:
                        if alt_name in self.all_schools_df.columns:
                            self.all_schools_df[standard_name] = self.all_schools_df[alt_name]
                            print(f"Mapped {alt_name} → {standard_name}")
                            break
                    else:
                        if standard_name == '_xCord':
                            self.all_schools_df[standard_name] = 67.0  # Default longitude
                        else:
                            self.all_schools_df[standard_name] = 30.0  # Default latitude

            # Handle school level column
            level_mappings = ['SchoolLevel', 'Level', 'School_Level', 'Type']
            if 'SchoolLevel' not in self.all_schools_df.columns:
                for alt_name in level_mappings:
                    if alt_name in self.all_schools_df.columns:
                        self.all_schools_df['SchoolLevel'] = self.all_schools_df[alt_name]
                        print(f"Mapped {alt_name} → SchoolLevel")
                        break
                else:
                    self.all_schools_df['SchoolLevel'] = 'Primary'  # Default

            # Handle school name column
            name_mappings = ['SchoolName', 'Name', 'School_Name', 'school_name']
            if 'SchoolName' not in self.all_schools_df.columns:
                for alt_name in name_mappings:
                    if alt_name in self.all_schools_df.columns:
                        self.all_schools_df['SchoolName'] = self.all_schools_df[alt_name]
                        print(f"Mapped {alt_name} → SchoolName")
                        break
                else:
                    self.all_schools_df['SchoolName'] = 'Unknown School'

            # BEMIS / EMIS code mapping for all schools
            if 'BEMISCode' not in self.all_schools_df.columns:
                code_candidates = ['BEMISCode', 'BEMIS', 'BemisCode', 'EMISCode', 'EMIS', 'SEMIS', 'SEMISCode', 'SchoolCode', 'Code']
                for c in code_candidates:
                    if c in self.all_schools_df.columns:
                        self.all_schools_df['BEMISCode'] = self.all_schools_df[c].astype(str)
                        print(f"Mapped {c} → BEMISCode")
                        break
                else:
                    # generate stable synthetic code if missing
                    self.all_schools_df['BEMISCode'] = [f"SCH-{i+1}" for i in range(len(self.all_schools_df))]
                    print("Generated placeholder BEMISCode values for all schools")
            # Handle district column
            district_mappings = ['District', 'district', 'DISTRICT']
            if 'District' not in self.all_schools_df.columns:
                for alt_name in district_mappings:
                    if alt_name in self.all_schools_df.columns:
                        self.all_schools_df['District'] = self.all_schools_df[alt_name]
                        print(f"Mapped {alt_name} → District")
                        break
                else:
                    self.all_schools_df['District'] = 'Unknown District'

            # Handle gender column
            gender_mappings = ['Gender', 'gender', 'GENDER', 'Gender_Type']
            if 'Gender' not in self.all_schools_df.columns:
                for alt_name in gender_mappings:
                    if alt_name in self.all_schools_df.columns:
                        self.all_schools_df['Gender'] = self.all_schools_df[alt_name]
                        print(f"Mapped {alt_name} → Gender")
                        break
                else:
                    self.all_schools_df['Gender'] = 'Mixed'  # Default gender type

            # Clean data
            self.all_schools_df = self.all_schools_df.dropna(subset=['_xCord', '_yCord'])
            
            # Filter invalid coordinates
            self.all_schools_df = self.all_schools_df[
                (self.all_schools_df['_xCord'].notna()) &
                (self.all_schools_df['_yCord'].notna()) &
                (self.all_schools_df['_xCord'] != 0) &
                (self.all_schools_df['_yCord'] != 0)
            ]
            
            print(f"Loaded {len(self.all_schools_df)} schools from all schools dataset")
            # Build indices for performance
            self.build_level_index()
            return True, f"Successfully loaded {len(self.all_schools_df)} schools"
            
        except Exception as e:
            return False, f"Error loading all schools file: {str(e)}"

    def load_target_schools_data(self, file_path):
        """Load the target schools dataset (schools to find progression for)"""
        try:
            # Read CSV file
            self.target_schools_df = pd.read_csv(file_path)
            
            # Apply same column mappings as all schools
            coord_mappings = [
                ('_xCord', ['_xCord', 'Longitude', 'longitude', 'lng', 'lon', 'x_cord', 'xCord']),
                ('_yCord', ['_yCord', 'Latitude', 'latitude', 'lat', 'y_cord', 'yCord'])
            ]
            
            for standard_name, possible_names in coord_mappings:
                if standard_name not in self.target_schools_df.columns:
                    for alt_name in possible_names:
                        if alt_name in self.target_schools_df.columns:
                            self.target_schools_df[standard_name] = self.target_schools_df[alt_name]
                            print(f"Target: Mapped {alt_name} → {standard_name}")
                            break

            # Handle other columns
            if 'SchoolLevel' not in self.target_schools_df.columns:
                for alt_name in ['Level', 'School_Level', 'Type']:
                    if alt_name in self.target_schools_df.columns:
                        self.target_schools_df['SchoolLevel'] = self.target_schools_df[alt_name]
                        break
                else:
                    self.target_schools_df['SchoolLevel'] = 'Primary'

            if 'SchoolName' not in self.target_schools_df.columns:
                for alt_name in ['Name', 'School_Name', 'school_name']:
                    if alt_name in self.target_schools_df.columns:
                        self.target_schools_df['SchoolName'] = self.target_schools_df[alt_name]
                        break
                else:
                    self.target_schools_df['SchoolName'] = 'Unknown School'
            # BEMIS / EMIS code mapping for target schools
            if 'BEMISCode' not in self.target_schools_df.columns:
                code_candidates = ['BEMISCode', 'BEMIS', 'BemisCode', 'EMISCode', 'EMIS', 'SEMIS', 'SEMISCode', 'SchoolCode', 'Code']
                for c in code_candidates:
                    if c in self.target_schools_df.columns:
                        self.target_schools_df['BEMISCode'] = self.target_schools_df[c].astype(str)
                        print(f"Target: Mapped {c} → BEMISCode")
                        break
                else:
                    self.target_schools_df['BEMISCode'] = [f"TGT-{i+1}" for i in range(len(self.target_schools_df))]
                    print("Generated placeholder BEMISCode values for target schools")
            # Handle district column
            district_mappings = ['District', 'district', 'DISTRICT']
            if 'District' not in self.target_schools_df.columns:
                for alt_name in district_mappings:
                    if alt_name in self.target_schools_df.columns:
                        self.target_schools_df['District'] = self.target_schools_df[alt_name]
                        print(f"Mapped {alt_name} → District")
                        break
                else:
                    self.target_schools_df['District'] = 'Unknown District'

            if 'Gender' not in self.target_schools_df.columns:
                for alt_name in ['gender', 'GENDER', 'Gender_Type']:
                    if alt_name in self.target_schools_df.columns:
                        self.target_schools_df['Gender'] = self.target_schools_df[alt_name]
                        break
                else:
                    self.target_schools_df['Gender'] = 'Mixed'
            
            # Clean data
            self.target_schools_df = self.target_schools_df.dropna(subset=['_xCord', '_yCord'])
            self.target_schools_df = self.target_schools_df[
                (self.target_schools_df['_xCord'].notna()) &
                (self.target_schools_df['_yCord'].notna()) &
                (self.target_schools_df['_xCord'] != 0) &
                (self.target_schools_df['_yCord'] != 0)
            ]
            
            print(f"Loaded {len(self.target_schools_df)} target schools")
            return True, f"Successfully loaded {len(self.target_schools_df)} target schools"
            
        except Exception as e:
            return False, f"Error loading target schools file: {str(e)}"
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points"""
        try:
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        except:
            return float('inf')
    
    def haversine_vectorized(self, lat1, lon1, lats2, lons2):
        """Vectorized haversine distance (km) from a single point to arrays."""
        # Convert to radians
        lat1_r, lon1_r = radians(lat1), radians(lon1)
        lat2_r = np.radians(lats2)
        lon2_r = np.radians(lons2)
        dlat = lat2_r - lat1_r
        dlon = lon2_r - lon1_r
        a = np.sin(dlat/2)**2 + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return 6371.0 * c  # Earth radius km
    
    def find_progression_schools(self, target_school, max_distance=MAX_SEARCH_RADIUS):
        """Find the nearest progression schools for a target school"""
        # Optimized version using pre-built indices
        if self.all_schools_df is None:
            return None
        if not self.level_index:
            self.build_level_index()
        target_level = target_school['SchoolLevel']
        target_lat = target_school['_yCord']
        target_lon = target_school['_xCord']
        progression_level = PROGRESSION_MAP.get(target_level)
        
        if progression_level is None:
            return {
                'target_school': target_school.to_dict(),
                'progression_level': None,
                'message': f"No progression beyond {target_level} level",
                'nearest_schools': [],
                'total_found': 0
            }
        
        if progression_level not in self.level_index:
            return {
                'target_school': target_school.to_dict(),
                'progression_level': progression_level,
                'message': f"No {progression_level} schools found in dataset",
                'nearest_schools': [],
                'total_found': 0
            }
        
        prog_df = self.level_index[progression_level]
        lats, lons = self.level_coords[progression_level]
        # Bounding box pre-filter to reduce computation
        lat_delta = max_distance / 111.0
        lon_delta = max_distance / (111.0 * max(cos(radians(target_lat)), 0.1))
        # Fixed multiline boolean expression with explicit parentheses
        mask_bbox = (
            (lats >= target_lat - lat_delta) &
            (lats <= target_lat + lat_delta) &
            (lons >= target_lon - lon_delta) &
            (lons <= target_lon + lon_delta)
        )
        if not np.any(mask_bbox):
            return {
                'target_school': target_school.to_dict(),
                'current_level': target_level,
                'progression_level': progression_level,
                'message': f"No {progression_level} schools within {max_distance}km",
                'nearest_schools': [],
                'total_found': 0,
                'all_within_radius': 0
            }
        subset_lats = lats[mask_bbox]
        subset_lons = lons[mask_bbox]
        distances = self.haversine_vectorized(target_lat, target_lon, subset_lats, subset_lons)
        within_mask = distances <= max_distance
        if not np.any(within_mask):
            return {
                'target_school': target_school.to_dict(),
                'current_level': target_level,
                'progression_level': progression_level,
                'message': f"No {progression_level} schools within {max_distance}km",
                'nearest_schools': [],
                'total_found': 0,
                'all_within_radius': 0
            }
        # Indices relative to full prog_df
        subset_indices = np.nonzero(mask_bbox)[0][within_mask]
        subset_distances = distances[within_mask]
        order = np.argsort(subset_distances)
        ordered_indices = subset_indices[order]
        ordered_distances = subset_distances[order]
        top_n = 5
        take_indices = ordered_indices[:top_n]
        take_distances = ordered_distances[:top_n]
        top_df = prog_df.iloc[take_indices].copy()
        top_df['distance_km'] = np.round(take_distances, 4)
        result_total = len(ordered_indices)
        return {
            'target_school': target_school.to_dict(),
            'current_level': target_level,
            'progression_level': progression_level,
            'message': f"Found {result_total} {progression_level} schools within {max_distance}km",
            'nearest_schools': top_df.to_dict('records'),
            'total_found': result_total,
            'all_within_radius': result_total
        }
    
    def analyze_all_progressions(self, selected_districts=None, max_distance=MAX_SEARCH_RADIUS):
        """Analyze progression paths for all target schools"""
        if self.target_schools_df is None or self.all_schools_df is None:
            return []
        
        # Filter target schools by district if specified
        target_schools = self.target_schools_df.copy()
        if selected_districts and 'all' not in selected_districts:
            target_schools = target_schools[target_schools['District'].isin(selected_districts)]
        
        results = []
        for _, school in target_schools.iterrows():
            progression_analysis = self.find_progression_schools(school, max_distance)
            results.append(progression_analysis)
        
        return results
    
    def create_progression_map(self, progression_results):
        """Create interactive map showing target schools and their progression options"""
        # Optimized map limiting & clustering
        if not progression_results:
            return None
        MAX_TARGETS_FOR_MAP = 500
        truncated = False
        if len(progression_results) > MAX_TARGETS_FOR_MAP:
            progression_results_for_map = progression_results[:MAX_TARGETS_FOR_MAP]
            truncated = True
        else:
            progression_results_for_map = progression_results
        target_lats = [r['target_school']['_yCord'] for r in progression_results_for_map if r['target_school']]
        target_lons = [r['target_school']['_xCord'] for r in progression_results_for_map if r['target_school']]
        if not target_lats:
            return None
            
        center_lat = sum(target_lats) / len(target_lats)
        center_lon = sum(target_lons) / len(target_lons)
        
        # Create map
        try:
            m = folium.Map(
                location=[center_lat, center_lon], 
                zoom_start=8,
                tiles=None,
                max_zoom=18,
                min_zoom=5
            )
        except Exception as map_err:
            print(f"Folium map creation failed: {map_err}")
            return None
        # Ensure Leaflet assets injection for inline rendering
        folium.utilities.validate_location
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
        
        # Color mapping for school levels
        level_colors = {
            'Primary': '#3498db',
            'Middle': '#2ecc71', 
            'High': '#f39c12',
            'Higher Secondary': '#e74c3c'
        }
        
        from folium.plugins import MarkerCluster
        cluster = MarkerCluster(name='Target Schools').add_to(m)
        
        # Add target schools and their progression schools
        for result in progression_results_for_map:
            target = result['target_school']
            target_lat = target['_yCord']
            target_lon = target['_xCord']
            target_level = target['SchoolLevel']
            
            # Add target school marker
            target_color = level_colors.get(target_level, '#95a5a6')
            
            target_popup = f"""
            <div style='width:260px;font-family:Poppins;'>
            <h5 style='margin:0 0 6px 0;color:#2c3e50;'>{target['SchoolName']}</h5>
            <p style='margin:0;font-size:12px;'><strong>Level:</strong> {target_level}</p>
            <p style='margin:0;font-size:12px;'><strong>District:</strong> {target.get('District','Unknown')}</p>
            <p style='margin:4px 0 0 0;font-size:12px;'><strong>Progression:</strong> {result.get('progression_level','None')}</p>
            </div>
            """
            folium.Marker(
                location=[target_lat, target_lon],
                popup=folium.Popup(target_popup, max_width=300),
                tooltip=f"{target['SchoolName']} ({target_level})",
                icon=folium.Icon(
                    color='blue',
                    icon='star',
                    prefix='fa'
                )
            ).add_to(cluster)
            
            # Limit number of lines to avoid heavy map
            for prog_school in result.get('nearest_schools', [])[:3]:
                prog_lat = prog_school['_yCord']
                prog_lon = prog_school['_xCord']
                prog_level = prog_school['SchoolLevel']
                distance = prog_school.get('distance_km', 0)
                
                prog_color = level_colors.get(prog_level, '#666')
                
                folium.CircleMarker(
                    location=[prog_lat, prog_lon],
                    radius=5,
                    color='white',
                    weight=1,
                    fill=True,
                    fillColor=prog_color,
                    fillOpacity=0.85,
                    tooltip=f"{prog_school['SchoolName']} ({prog_level}) {prog_school.get('distance_km',0):.1f}km"
                ).add_to(m)
                
                folium.PolyLine(
                    locations=[[target_lat, target_lon], [prog_lat, prog_lon]],
                    color=prog_color,
                    weight=1.5,
                    opacity=0.6
                ).add_to(m)
        
        legend_note = '<div style="position:fixed;bottom:10px;right:10px;background:rgba(255,255,255,0.95);padding:8px 12px;border-radius:8px;font-size:12px;z-index:9999;box-shadow:0 2px 6px rgba(0,0,0,0.2);font-family:Poppins;">' + ("Showing first 500 target schools for performance" if truncated else "All target schools displayed") + '</div>'
        m.get_root().html.add_child(folium.Element(legend_note))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m

# Global analyzer instance
analyzer = SchoolProgressionAnalyzer()

def save_analyzer_state():
    """Save analyzer state to disk"""
    try:
        state_file = os.path.join(app.config['DATA_FOLDER'], 'current_analyzer.pkl')
        
        state = {
            'all_schools_df': analyzer.all_schools_df,
            'target_schools_df': analyzer.target_schools_df,
            'analysis_id': analyzer.analysis_id,
            'latest_results': getattr(analyzer, 'latest_results', None)
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
        state_file = os.path.join(app.config['DATA_FOLDER'], 'current_analyzer.pkl')
        
        if os.path.exists(state_file):
            with open(state_file, 'rb') as f:
                state = pickle.load(f)
            
            analyzer.all_schools_df = state.get('all_schools_df')
            analyzer.target_schools_df = state.get('target_schools_df')
            analyzer.analysis_id = state.get('analysis_id')
            analyzer.latest_results = state.get('latest_results')
            
            return True
    except Exception as e:
        print(f"Error loading analyzer state: {e}")
    return False

@app.route('/')
def index():
    # Load existing analyzer state
    load_analyzer_state()
    
    return render_template('index_elegant.html')

@app.route('/upload_all_schools', methods=['POST'])
def upload_all_schools():
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
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'all_schools_{filename}')
    
    try:
        file.save(filepath)
        
        # Convert Excel to CSV if needed
        csv_filepath = filepath
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
            csv_filename = f'all_schools_{filename.rsplit(".", 1)[0]}.csv'
            csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            df.to_csv(csv_filepath, index=False)
        
        success, message = analyzer.load_all_schools_data(csv_filepath)
        
        if success:
            save_analyzer_state()  # Save state to disk
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/upload_target_schools', methods=['POST'])
def upload_target_schools():
    # Load state first to check if all schools are loaded
    load_analyzer_state()
    
    # Check if all schools are loaded
    if analyzer.all_schools_df is None:
        return jsonify({'success': False, 'message': 'Please upload all schools data first'}), 400
    
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
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'target_schools_{filename}')
    
    try:
        file.save(filepath)
        
        # Convert Excel to CSV if needed
        csv_filepath = filepath
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
            csv_filename = f'target_schools_{filename.rsplit(".", 1)[0]}.csv'
            csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            df.to_csv(csv_filepath, index=False)
        
        success, message = analyzer.load_target_schools_data(csv_filepath)
        
        if success:
            save_analyzer_state()  # Save state to disk
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/load-sample')
def load_sample():
    """Load sample data for testing the progression system"""
    try:
        # Load sample all schools data
        all_schools_path = 'data/sample_full_schools.csv'
        if os.path.exists(all_schools_path):
            success, message = analyzer.load_all_schools_data(all_schools_path)
            
            if success:
                save_analyzer_state()  # Save state to disk
                
                # Load sample target schools data
                target_schools_path = 'data/sample_target_schools.csv'
                if os.path.exists(target_schools_path):
                    success2, message2 = analyzer.load_target_schools_data(target_schools_path)
                    
                    if success2:
                        save_analyzer_state()  # Save state to disk
                        
                        flash(f"Sample data loaded successfully: {len(analyzer.all_schools_df)} total schools, {len(analyzer.target_schools_df)} target schools", 'success')
                        return redirect(url_for('configure'))
                    else:
                        flash(f"Error loading target schools: {message2}", 'error')
                else:
                    flash("Sample target schools file not found", 'error')
            else:
                flash(f"Error loading all schools: {message}", 'error')
        else:
            flash("Sample all schools file not found", 'error')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
    
    return redirect(url_for('index'))

@app.route('/configure')
def configure():
    # Load existing analyzer state
    load_analyzer_state()
    
    # Check if both datasets are loaded in the analyzer
    if analyzer.all_schools_df is None or analyzer.target_schools_df is None:
        flash('Please upload both all schools and target schools data', 'error')
        return redirect(url_for('index'))
    
    # Get data statistics
    available_districts = sorted(analyzer.target_schools_df['District'].unique().tolist())
    available_levels = sorted(analyzer.target_schools_df['SchoolLevel'].unique().tolist())
    
    district_counts = analyzer.target_schools_df['District'].value_counts().to_dict()
    level_counts = analyzer.target_schools_df['SchoolLevel'].value_counts().to_dict()
    
    total_target_schools = len(analyzer.target_schools_df)
    total_all_schools = len(analyzer.all_schools_df)
    
    return render_template('configure_elegant.html',
                         available_districts=available_districts,
                         available_levels=available_levels,
                         district_counts=district_counts,
                         level_counts=level_counts,
                         total_target_schools=total_target_schools,
                         total_all_schools=total_all_schools,
                         all_schools_filename='all_schools.csv',
                         target_schools_filename='target_schools.csv')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Load existing analyzer state
        load_analyzer_state()
        
        if analyzer.all_schools_df is None or analyzer.target_schools_df is None:
            flash('Please upload both datasets first', 'error')
            return redirect(url_for('index'))
        
        # Get form data
        selected_districts = request.form.getlist('districts')
        max_distance = float(request.form.get('max_distance', MAX_SEARCH_RADIUS))
        
        print(f"=== PROGRESSION ANALYSIS DEBUG ===")
        print(f"Selected districts: {selected_districts}")
        print(f"Max distance: {max_distance}")
        print(f"Target schools count: {len(analyzer.target_schools_df)}")
        print(f"All schools count: {len(analyzer.all_schools_df)}")
        
        # Perform progression analysis
        progression_results = analyzer.analyze_all_progressions(selected_districts, max_distance)
        
        # Create map
        progression_map = analyzer.create_progression_map(progression_results)
        map_html = progression_map._repr_html_() if progression_map else None
        
        # Calculate statistics
        total_analyzed = len(progression_results)
        schools_with_progression = sum(1 for r in progression_results if r.get('total_found', 0) > 0)
        schools_without_progression = total_analyzed - schools_with_progression
        
        # Level distribution analysis
        level_analysis = {}
        for level in ['Primary', 'Middle', 'High', 'Higher Secondary']:
            level_results = [r for r in progression_results if r['target_school']['SchoolLevel'] == level]
            if level_results:
                level_analysis[level] = {
                    'count': len(level_results),
                    'with_progression': sum(1 for r in level_results if r.get('total_found', 0) > 0),
                    'avg_options': sum(r.get('total_found', 0) for r in level_results) / len(level_results),
                    'progression_to': PROGRESSION_MAP.get(level, 'None')
                }
        
        # Store results for potential download and save state
        analyzer.latest_results = {
            'progression_results': progression_results,
            'selected_districts': selected_districts,
            'max_distance': max_distance,
            'total_analyzed': total_analyzed,
            'schools_with_progression': schools_with_progression,
            'schools_without_progression': schools_without_progression,
            'level_analysis': level_analysis
        }
        save_analyzer_state()  # Save the state with results
        
        return render_template('results_elegant.html',
                             results=progression_results,
                             selected_districts=selected_districts,
                             max_distance=max_distance,
                             total_analyzed=total_analyzed,
                             schools_with_progression=schools_with_progression,
                             schools_without_progression=schools_without_progression,
                             level_analysis=level_analysis,
                             map_html=map_html,
                             progression_map=PROGRESSION_MAP)
        
    except Exception as e:
        print(f"Error in analyze route: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'Error during analysis: {str(e)}', 'error')
        return redirect(url_for('configure'))

@app.route('/download_results')
def download_results():
    """Download the latest progression analysis results"""
    try:
        # Load state to get the latest results
        load_analyzer_state()
        if not hasattr(analyzer, 'latest_results') or analyzer.latest_results is None:
            return jsonify({'error': 'No analysis results found. Please perform an analysis first.'}), 404
        results = analyzer.latest_results
        # Create detailed DataFrame matching SchoolUpgradeSystem format
        df_results = []
        for i, result in enumerate(results['progression_results']):
            target = result['target_school']
            row = {
                'Target_BEMIS_Code': target.get('BEMISCode',''),
                'SchoolName': target['SchoolName'],
                'District': target.get('District', 'Unknown'),
                'CurrentLevel': target['SchoolLevel'],
                'RecommendedProgression': result.get('progression_level', 'None'),
                'Gender': target.get('Gender', 'Mixed'),
                'Priority': 'High' if i < 10 else 'Medium' if i < 50 else 'Standard',
                'Target_School_Latitude': target['_yCord'],
                'Target_School_Longitude': target['_xCord'],
                'Total_Progression_Schools_Found': result.get('total_found', 0),
                'Analysis_Message': result.get('message', ''),
                'Nearest_Progression_School': '',
                'Nearest_Progression_BEMIS_Code': '',
                'Distance_to_Nearest_KM': '',
                'Progression_School_District': ''
            }
            if result.get('nearest_schools') and len(result['nearest_schools']) > 0:
                nearest = result['nearest_schools'][0]
                row.update({
                    'Nearest_Progression_School': nearest.get('SchoolName',''),
                    'Nearest_Progression_BEMIS_Code': nearest.get('BEMISCode',''),
                    'Distance_to_Nearest_KM': round(nearest.get('distance_km', 0), 2),
                    'Progression_School_District': nearest.get('District', 'Unknown')
                })
            df_results.append(row)
        df = pd.DataFrame(df_results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"school_progression_analysis_{timestamp}.csv"
        filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        df.to_csv(filepath, index=False)
        return send_file(filepath, mimetype='text/csv', as_attachment=True, download_name=filename)
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': f'Error generating download: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return '''
    <html>
    <head><title>School Progression System Health Check</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f0f0f0;">
        <h1 style="color: #2563eb;">🏫 School Progression System</h1>
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

def load_existing_files(all_filename='all_schools.csv', target_filename='target_schools.csv'):
    """Attempt to load existing renamed files from uploads folder or root/data folder.
    Returns dict with results for UI consumption."""
    locations_to_check = [
        app.config['UPLOAD_FOLDER'],
        'data',
        '.',
    ]
    results = {
        'all_schools': {'loaded': False, 'path': None, 'message': ''},
        'target_schools': {'loaded': False, 'path': None, 'message': ''}
    }
    # Load all schools first
    for loc in locations_to_check:
        candidate = os.path.join(loc, all_filename)
        if os.path.exists(candidate):
            success, message = analyzer.load_all_schools_data(candidate)
            results['all_schools']['loaded'] = success
            results['all_schools']['path'] = candidate
            results['all_schools']['message'] = message
            break
    if not results['all_schools']['loaded']:
        results['all_schools']['message'] = f"{all_filename} not found in standard locations"
    # Only attempt target if all loaded
    if results['all_schools']['loaded']:
        for loc in locations_to_check:
            candidate = os.path.join(loc, target_filename)
            if os.path.exists(candidate):
                success, message = analyzer.load_target_schools_data(candidate)
                results['target_schools']['loaded'] = success
                results['target_schools']['path'] = candidate
                results['target_schools']['message'] = message
                break
        if not results['target_schools']['loaded']:
            results['target_schools']['message'] = f"{target_filename} not found in standard locations"
    save_analyzer_state()
    return results

@app.route('/load-renamed', methods=['POST'])
def load_renamed():
    """Endpoint to load existing renamed files (all_schools.csv & target_schools.csv) without manual upload."""
    try:
        data = request.get_json(silent=True) or {}
        all_name = data.get('all_filename', 'all_schools.csv')
        target_name = data.get('target_filename', 'target_schools.csv')
        load_results = load_existing_files(all_name, target_name)
        status_code = 200 if load_results['all_schools']['loaded'] else 404
        return jsonify({'success': load_results['all_schools']['loaded'], 'results': load_results}), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/status')
def get_status():
    """Get current upload status with existence checks"""
    # Load existing analyzer state
    load_analyzer_state()
    # Check for commonly named files presence
    common_all = any(os.path.exists(os.path.join(p, 'all_schools.csv')) for p in [app.config['UPLOAD_FOLDER'], 'data', '.'])
    common_target = any(os.path.exists(os.path.join(p, 'target_schools.csv')) for p in [app.config['UPLOAD_FOLDER'], 'data', '.'])
    status = {
        'all_schools_loaded': analyzer.all_schools_df is not None,
        'target_schools_loaded': analyzer.target_schools_df is not None,
        'total_all_schools': len(analyzer.all_schools_df) if analyzer.all_schools_df is not None else 0,
        'total_target_schools': len(analyzer.target_schools_df) if analyzer.target_schools_df is not None else 0,
        'ready_for_analysis': (analyzer.all_schools_df is not None and analyzer.target_schools_df is not None),
        'existing_all_file': common_all,
        'existing_target_file': common_target
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5020)
