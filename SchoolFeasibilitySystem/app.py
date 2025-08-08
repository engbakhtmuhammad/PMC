import pandas as pd
import numpy as np
import math
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from werkzeug.utils import secure_filename
from geopy.distance import geodesic
import folium
from folium import plugins
import uuid

app = Flask(__name__)
app.secret_key = 'school_feasibility_secret_key_2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Required columns for school data
REQUIRED_COLUMNS = [
    'BemisCode', 'SchoolName', 'District', 'Tehsil', 'SubTehsil', 'UC', 
    'VillageName', 'Gender', 'SchoolLevel', 'FunctionalStatus', 
    'ReasonOfNonFunctional', 'Building', 'BuildingStructure', 'BuildingCondition',
    'SpaceForNewRooms', 'BoundaryWall', 'BoundaryWallStructure', 
    'BoundaryWallCondition', 'ElectricityInSchool', 'TotalStudentProfileEntered',
    'Source', '_xCord', '_yCord'
]

# School level hierarchy
LEVEL_HIERARCHY = {
    'Primary': 1,
    'Middle': 2,
    'High': 3,
    'Higher Secondary': 4
}

# Minimum distances between schools of same level (in km)
MIN_DISTANCES = {
    'Primary': 2.0,      # Primary schools can be closer
    'Middle': 5.0,       # Middle schools need more distance
    'High': 10.0,        # High schools need significant distance
    'Higher Secondary': 15.0  # Higher secondary need maximum distance
}

class SchoolFeasibilityAnalyzer:
    def __init__(self):
        self.schools_df = None
        self.proposed_schools = []
        self.analysis_id = None
        
    def load_data(self, file_path):
        """Load and validate the uploaded CSV file"""
        try:
            # Read CSV file
            self.schools_df = pd.read_csv(file_path)
            
            # Map real data columns to expected format if needed
            if 'TotalStudentProfileEntered' not in self.schools_df.columns:
                for alt_col in ['TotalSchoolProfileStudents', 'TotalStudents', 'Students']:
                    if alt_col in self.schools_df.columns:
                        self.schools_df['TotalStudentProfileEntered'] = self.schools_df[alt_col]
                        break
                else:
                    self.schools_df['TotalStudentProfileEntered'] = 50

            # Handle coordinate columns
            coord_mappings = [
                ('_xCord', ['_xCord', 'Longitude', 'longitude', 'lng', 'lon', 'x_cord', 'xCord']),
                ('_yCord', ['_yCord', 'Latitude', 'latitude', 'lat', 'y_cord', 'yCord'])
            ]
            
            for standard_name, possible_names in coord_mappings:
                if standard_name not in self.schools_df.columns:
                    for alt_name in possible_names:
                        if alt_name in self.schools_df.columns:
                            self.schools_df[standard_name] = self.schools_df[alt_name]
                            print(f"Mapped {alt_name} → {standard_name}")
                            break
                    else:
                        if standard_name == '_xCord':
                            self.schools_df[standard_name] = 67.0  # Default longitude
                        else:
                            self.schools_df[standard_name] = 30.0  # Default latitude

            # Clean data
            self.schools_df = self.schools_df.dropna(subset=['_xCord', '_yCord'])
            self.schools_df['TotalStudentProfileEntered'] = pd.to_numeric(
                self.schools_df['TotalStudentProfileEntered'], errors='coerce'
            ).fillna(50)
            
            # Handle missing columns with defaults
            if 'SchoolLevel' not in self.schools_df.columns:
                self.schools_df['SchoolLevel'] = 'Primary'
            if 'FunctionalStatus' not in self.schools_df.columns:
                self.schools_df['FunctionalStatus'] = 'Functional'
            
            # Filter invalid coordinates
            self.schools_df = self.schools_df[
                (self.schools_df['_xCord'].notna()) &
                (self.schools_df['_yCord'].notna()) &
                (self.schools_df['_xCord'] != 0) &
                (self.schools_df['_yCord'] != 0)
            ]
            
            return True, f"Successfully loaded {len(self.schools_df)} schools"
            
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points"""
        try:
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        except:
            return float('inf')
    
    def find_nearby_schools(self, lat, lon, level, search_radius=20):
        """Find existing schools near proposed coordinates"""
        if self.schools_df is None or len(self.schools_df) == 0:
            return pd.DataFrame()
        
        # Calculate distances to all schools
        self.schools_df['distance_to_proposed'] = self.schools_df.apply(
            lambda row: self.calculate_distance(
                lat, lon, row['_yCord'], row['_xCord']
            ), axis=1
        )
        
        # Filter schools within search radius
        nearby_schools = self.schools_df[
            self.schools_df['distance_to_proposed'] <= search_radius
        ].copy()
        
        return nearby_schools.sort_values('distance_to_proposed')
    
    def analyze_single_location(self, lat, lon, level, search_radius=20, selected_districts=None):
        """Enhanced analysis of feasibility for a single proposed school location"""
        
        # Find nearby schools
        nearby_schools = self.find_nearby_schools(lat, lon, level, search_radius)
        
        # Filter by selected districts if specified
        if selected_districts and 'all' not in selected_districts:
            nearby_schools = nearby_schools[nearby_schools['District'].isin(selected_districts)]
        
        # Get minimum required distance for this school level
        min_distance = MIN_DISTANCES.get(level, 5.0)
        
        # Find schools of same level within minimum distance
        same_level_schools = nearby_schools[
            (nearby_schools['SchoolLevel'] == level) &
            (nearby_schools['distance_to_proposed'] < min_distance)
        ]
        
        # Enhanced feasibility analysis
        is_feasible = len(same_level_schools) == 0
        
        # Population density analysis
        total_students_nearby = nearby_schools['TotalStudentProfileEntered'].sum()
        avg_students_per_school = nearby_schools['TotalStudentProfileEntered'].mean() if len(nearby_schools) > 0 else 0
        
        # Infrastructure analysis
        functional_schools = nearby_schools[nearby_schools['FunctionalStatus'] == 'Functional']
        functional_percentage = (len(functional_schools) / len(nearby_schools) * 100) if len(nearby_schools) > 0 else 0
        
        # Gender analysis
        gender_distribution = nearby_schools['Gender'].value_counts().to_dict() if 'Gender' in nearby_schools.columns else {}
        
        # Create enhanced recommendation
        if is_feasible:
            recommendation = "FEASIBLE"
            base_reason = f"No {level} school within {min_distance}km radius"
            
            # Add density considerations
            if total_students_nearby > 1000 and level in ['Primary', 'Middle']:
                recommendation = "HIGHLY RECOMMENDED"
                reason = f"{base_reason}. High student density ({total_students_nearby} students) indicates strong demand."
                risk_level = "Very Low"
            elif total_students_nearby > 500:
                recommendation = "RECOMMENDED"
                reason = f"{base_reason}. Moderate student density ({total_students_nearby} students) supports new school."
                risk_level = "Low"
            else:
                reason = f"{base_reason}. Low student density ({total_students_nearby} students) - consider community need assessment."
                risk_level = "Low"
        else:
            recommendation = "NOT FEASIBLE"
            nearest_school = same_level_schools.iloc[0]
            distance = round(nearest_school['distance_to_proposed'], 2)
            base_reason = f"{level} school '{nearest_school['SchoolName']}' only {distance}km away (minimum: {min_distance}km)"
            
            # Enhanced conflict analysis
            if distance < min_distance * 0.5:
                risk_level = "Very High"
                reason = f"{base_reason}. CRITICAL: Too close to existing school - may cause enrollment conflicts."
            elif distance < min_distance * 0.75:
                risk_level = "High"
                reason = f"{base_reason}. HIGH RISK: Close proximity may impact both schools' viability."
            else:
                risk_level = "Medium"
                reason = f"{base_reason}. MODERATE RISK: Consider upgrading existing school instead."
        
        # Find nearest schools for each level (for map display)
        nearest_schools_by_level = {}
        for school_level in ['Primary', 'Middle', 'High', 'Higher Secondary']:
            level_schools = nearby_schools[nearby_schools['SchoolLevel'] == school_level]
            if len(level_schools) > 0:
                nearest = level_schools.loc[level_schools['distance_to_proposed'].idxmin()]
                nearest_schools_by_level[school_level] = {
                    'name': nearest['SchoolName'],
                    'distance': round(nearest['distance_to_proposed'], 2),
                    'latitude': nearest['_yCord'],
                    'longitude': nearest['_xCord'],
                    'students': nearest['TotalStudentProfileEntered'],
                    'functional': nearest['FunctionalStatus']
                }
        
        # Count nearby schools by level
        level_counts = nearby_schools['SchoolLevel'].value_counts().to_dict()
        
        return {
            'latitude': lat,
            'longitude': lon,
            'proposed_level': level,
            'recommendation': recommendation,
            'is_feasible': is_feasible,
            'reason': reason,
            'risk_level': risk_level,
            'minimum_distance_required': min_distance,
            'nearest_same_level_distance': same_level_schools['distance_to_proposed'].min() if len(same_level_schools) > 0 else None,
            'nearby_schools_count': len(nearby_schools),
            'same_level_conflicts': len(same_level_schools),
            'level_counts': level_counts,
            'total_students_nearby': total_students_nearby,
            'avg_students_per_school': round(avg_students_per_school, 1),
            'functional_percentage': round(functional_percentage, 1),
            'gender_distribution': gender_distribution,
            'nearest_schools_by_level': nearest_schools_by_level,
            'nearby_schools': nearby_schools.to_dict('records') if len(nearby_schools) <= 20 else nearby_schools.head(20).to_dict('records')
        }
    
    def analyze_multiple_locations(self, proposals, search_radius=20, selected_districts=None):
        """Analyze multiple proposed school locations with enhanced analysis"""
        results = []
        
        for i, proposal in enumerate(proposals):
            lat = float(proposal['latitude'])
            lon = float(proposal['longitude'])
            level = proposal['level']
            name = proposal.get('name', f'Proposed School {i+1}')
            
            analysis = self.analyze_single_location(lat, lon, level, search_radius, selected_districts)
            analysis['proposal_name'] = name
            analysis['proposal_id'] = i + 1
            
            results.append(analysis)
        
        return results
    
    def create_feasibility_map(self, analysis_results):
        """Create enhanced interactive map showing proposed locations and existing schools"""
        if not analysis_results:
            return None
        
        # Calculate center point
        lats = [result['latitude'] for result in analysis_results]
        lons = [result['longitude'] for result in analysis_results]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create map with multiple tile layers
        m = folium.Map(
            location=[center_lat, center_lon], 
            zoom_start=10,
            tiles=None,
            max_zoom=18,
            min_zoom=5
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
        
        # Color mapping for school levels
        level_colors = {
            'Primary': '#3498db',
            'Middle': '#2ecc71', 
            'High': '#f39c12',
            'Higher Secondary': '#e74c3c'
        }
        
        # Add existing schools (smaller markers)
        existing_schools = set()
        for result in analysis_results:
            for school in result['nearby_schools']:
                school_key = (school['_yCord'], school['_xCord'], school['BemisCode'])
                if school_key not in existing_schools:
                    existing_schools.add(school_key)
                    
                    color = level_colors.get(school['SchoolLevel'], '#95a5a6')
                    
                    # Check if this is a nearest school for any proposal
                    is_nearest = False
                    nearest_to_proposals = []
                    for res in analysis_results:
                        for level_name, nearest_info in res.get('nearest_schools_by_level', {}).items():
                            if (abs(nearest_info['latitude'] - school['_yCord']) < 0.001 and 
                                abs(nearest_info['longitude'] - school['_xCord']) < 0.001):
                                is_nearest = True
                                nearest_to_proposals.append(f"{res['proposal_name']} ({level_name})")
                    
                    popup_html = f"""
                    <div style="width: 280px; font-family: 'Poppins', sans-serif;">
                        <h5 style="color: #2c3e50; margin-bottom: 10px; border-bottom: 2px solid {color}; padding-bottom: 5px;">
                            <i class="fas fa-school"></i> {school['SchoolName']}
                        </h5>
                        <p><strong>Level:</strong> <span style="color: {color}; font-weight: bold;">{school['SchoolLevel']}</span></p>
                        <p><strong>District:</strong> {school['District']}</p>
                        <p><strong>Status:</strong> <span style="color: {'green' if school['FunctionalStatus'] == 'Functional' else 'red'};">{school['FunctionalStatus']}</span></p>
                        <p><strong>Students:</strong> {school['TotalStudentProfileEntered']}</p>
                        <p><strong>Distance:</strong> {round(school.get('distance_to_proposed', 0), 2)} km</p>
                    """
                    
                    if is_nearest:
                        popup_html += f"""
                        <div style="background: #fff3cd; padding: 8px; border-radius: 5px; margin-top: 10px; border: 1px solid #ffc107;">
                            <strong>⚠️ Nearest School to:</strong><br>
                            {', '.join(nearest_to_proposals)}
                        </div>
                        """
                    
                    popup_html += "</div>"
                    
                    # Use different styling for nearest schools
                    marker_size = 10 if is_nearest else 6
                    marker_weight = 3 if is_nearest else 2
                    marker_opacity = 1.0 if is_nearest else 0.7
                    
                    folium.CircleMarker(
                        location=[school['_yCord'], school['_xCord']],
                        radius=marker_size,
                        popup=folium.Popup(popup_html, max_width=320),
                        tooltip=f"{school['SchoolName']} ({school['SchoolLevel']})" + (" - NEAREST" if is_nearest else ""),
                        color='white',
                        weight=marker_weight,
                        fill=True,
                        fillColor=color,
                        fillOpacity=marker_opacity
                    ).add_to(m)
        
        # Add proposed school locations (larger markers)
        for result in analysis_results:
            lat = result['latitude']
            lon = result['longitude']
            
            # Choose icon and color based on recommendation
            if result['recommendation'] in ['FEASIBLE', 'RECOMMENDED', 'HIGHLY RECOMMENDED']:
                icon_color = 'green'
                icon_name = 'check'
                marker_color = '#2ecc71'
            else:
                icon_color = 'red'
                icon_name = 'times'
                marker_color = '#e74c3c'
            
            # Enhanced popup with more analysis details
            popup_html = f"""
            <div style="width: 350px; font-family: 'Poppins', sans-serif;">
                <h4 style="color: {marker_color}; margin-bottom: 10px; border-bottom: 3px solid {marker_color}; padding-bottom: 5px;">
                    <i class="fas fa-map-marker-alt"></i> {result['proposal_name']}
                </h4>
                <div style="background: {'#d4edda' if result['is_feasible'] else '#f8d7da'}; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <strong>Status:</strong> <span style="color: {marker_color}; font-weight: bold;">{result['recommendation']}</span>
                </div>
                <p><strong>Proposed Level:</strong> {result['proposed_level']}</p>
                <p><strong>Risk Level:</strong> <span style="color: {'green' if result['risk_level'] == 'Low' else 'orange' if result['risk_level'] == 'Medium' else 'red'};">{result['risk_level']}</span></p>
                <p><strong>Nearby Schools:</strong> {result['nearby_schools_count']}</p>
                <p><strong>Same Level Conflicts:</strong> {result['same_level_conflicts']}</p>
                <p><strong>Total Students Nearby:</strong> {result.get('total_students_nearby', 0)}</p>
                
                <div style="margin: 10px 0;">
                    <strong>Nearest Schools by Level:</strong>
                    <div style="font-size: 12px; margin-top: 5px;">
            """
            
            for level, info in result.get('nearest_schools_by_level', {}).items():
                popup_html += f"""
                        <div style="margin: 2px 0; padding: 3px; background: #f8f9fa; border-radius: 3px;">
                            <strong>{level}:</strong> {info['name']} ({info['distance']} km)
                        </div>
                """
            
            popup_html += f"""
                    </div>
                </div>
                
                <div style="background: #fff3cd; padding: 8px; border-radius: 5px; margin-top: 10px;">
                    <strong>Analysis:</strong> {result['reason']}
                </div>
            </div>
            """
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"📍 {result['proposal_name']} - {result['recommendation']}",
                icon=folium.Icon(
                    color=icon_color,
                    icon=icon_name,
                    prefix='fa'
                )
            ).add_to(m)
            
            # Add radius circle showing minimum distance requirement
            min_distance = result['minimum_distance_required']
            folium.Circle(
                location=[lat, lon],
                radius=min_distance * 1000,  # Convert km to meters
                popup=f"Minimum distance: {min_distance}km for {result['proposed_level']} schools",
                color=marker_color,
                weight=2,
                fill=False,
                opacity=0.5
            ).add_to(m)
            
            # Add lines to nearest schools of same level if conflicts exist
            if result['same_level_conflicts'] > 0:
                for school in result['nearby_schools']:
                    if (school['SchoolLevel'] == result['proposed_level'] and 
                        school['distance_to_proposed'] < result['minimum_distance_required']):
                        folium.PolyLine(
                            locations=[[lat, lon], [school['_yCord'], school['_xCord']]],
                            color='red',
                            weight=3,
                            opacity=0.7,
                            dash_array='10, 5',
                            popup=f"Conflict: {school['SchoolName']} ({round(school['distance_to_proposed'], 2)} km)"
                        ).add_to(m)
        
        # Enhanced legend
        legend_html = '''
        <div style="position: fixed; 
                    top: 10%; left: 20px; 
                    width: 340px; 
                    background-color: rgba(255, 255, 255, 0.98); 
                    border: 3px solid #2c3e50; 
                    border-radius: 15px;
                    z-index: 9999; 
                    font-size: 14px; 
                    font-family: 'Poppins', sans-serif;
                    padding: 20px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                    backdrop-filter: blur(10px);
                    max-height: 80vh;
                    overflow-y: auto;">
        <h4 style="color: #2c3e50; margin: 0 0 15px 0; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 8px;">
            <i class="fas fa-map-marked-alt"></i> Enhanced Feasibility Map
        </h4>
        <div style="margin-bottom: 15px;">
            <h5 style="color: #34495e; margin: 0 0 8px 0; font-size: 15px;">Existing Schools:</h5>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><i class="fa fa-circle" style="color: #3498db; margin-right: 8px;"></i> Primary Schools</p>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><i class="fa fa-circle" style="color: #2ecc71; margin-right: 8px;"></i> Middle Schools</p>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><i class="fa fa-circle" style="color: #f39c12; margin-right: 8px;"></i> High Schools</p>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><i class="fa fa-circle" style="color: #e74c3c; margin-right: 8px;"></i> Higher Secondary</p>
            <p style="margin: 5px 0; font-size: 11px; color: #666;"><strong>Larger markers</strong> = Nearest to proposals</p>
        </div>
        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); padding: 10px; border-radius: 8px; border: 2px solid #fdcb6e; margin-bottom: 15px;">
            <h5 style="color: #856404; margin: 0 0 6px 0; font-size: 15px;">Proposed Schools:</h5>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><i class="fa fa-check" style="color: green; margin-right: 8px;"></i> Feasible Location</p>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><i class="fa fa-times" style="color: red; margin-right: 8px;"></i> Not Feasible</p>
        </div>
        <div style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); padding: 10px; border-radius: 8px; border: 2px solid #dc3545;">
            <h5 style="color: #721c24; margin: 0 0 6px 0; font-size: 15px;">Conflict Indicators:</h5>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><span style="border-bottom: 3px dashed red; margin-right: 8px; width: 15px;"></span> Distance Conflicts</p>
            <p style="margin: 3px 0; display: flex; align-items: center; font-size: 12px;"><i class="fa fa-circle-o" style="color: #666; margin-right: 8px;"></i> Minimum Distance Zones</p>
            <p style="margin: 0; font-size: 10px; color: #721c24; font-weight: 500; margin-top: 5px;">
                Red dashed lines connect conflicting schools
            </p>
        </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m

# Global analyzer instance
analyzer = SchoolFeasibilityAnalyzer()

@app.route('/')
def index():
    return render_template('index_elegant.html', required_columns=REQUIRED_COLUMNS)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(filepath)
        success, message = analyzer.load_data(filepath)
        
        if success:
            # Store filename in session for later use
            session['uploaded_filename'] = filename
            flash(message, 'success')
            return redirect(url_for('configure'))
        else:
            flash(message, 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/configure')
def configure():
    if analyzer.schools_df is None:
        flash('Please upload school data first', 'error')
        return redirect(url_for('index'))
    
    # Get data statistics for the form
    available_districts = sorted(analyzer.schools_df['District'].unique().tolist())
    available_levels = sorted(analyzer.schools_df['SchoolLevel'].unique().tolist())
    available_genders = sorted(analyzer.schools_df['Gender'].unique().tolist())
    
    district_counts = analyzer.schools_df['District'].value_counts().to_dict()
    level_counts = analyzer.schools_df['SchoolLevel'].value_counts().to_dict()
    gender_counts = analyzer.schools_df['Gender'].value_counts().to_dict()
    
    total_schools = len(analyzer.schools_df)
    functional_count = len(analyzer.schools_df[analyzer.schools_df['FunctionalStatus'] == 'Functional'])
    valid_coordinates = len(analyzer.schools_df.dropna(subset=['_xCord', '_yCord']))
    
    # Find coordinate columns dynamically
    lat_col = None
    lng_col = None
    for col in analyzer.schools_df.columns:
        col_lower = col.lower()
        if 'lat' in col_lower or col in ['_yCord', 'Latitude', 'Y']:
            lat_col = col
        elif 'lon' in col_lower or 'lng' in col_lower or col in ['_xCord', 'Longitude', 'X']:
            lng_col = col
    
    # Get the last uploaded filename from session or default
    filename = session.get('uploaded_filename', 'sample_schools.csv')
    
    return render_template('configure_elegant.html',
                         available_districts=available_districts,
                         available_levels=available_levels,
                         available_genders=available_genders,
                         district_counts=district_counts,
                         level_counts=level_counts,
                         gender_counts=gender_counts,
                         total_schools=total_schools,
                         functional_count=functional_count,
                         valid_coordinates=valid_coordinates,
                         filename=filename,
                         school_levels=available_levels,
                         min_distances=MIN_DISTANCES)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Debug: Print all form data
        print("=== ENHANCED ANALYZE ROUTE DEBUG ===")
        print(f"Form data: {dict(request.form)}")
        print(f"Districts: {request.form.getlist('districts')}")
        print(f"School levels: {request.form.getlist('school_levels')}")
        print(f"Min distance: {request.form.get('min_distance')}")
        print(f"Latitudes: {request.form.getlist('latitudes[]')}")
        print(f"Longitudes: {request.form.getlist('longitudes[]')}")
        print(f"Location names: {request.form.getlist('location_names[]')}")
        print("========================")
        
        if analyzer.schools_df is None:
            flash('No data loaded. Please upload a file first.', 'error')
            return redirect(url_for('index'))
        
        # Get form data
        selected_districts = request.form.getlist('districts')
        selected_levels = request.form.getlist('school_levels')
        min_distance = float(request.form.get('min_distance', 2.0))
        latitudes = request.form.getlist('latitudes[]')
        longitudes = request.form.getlist('longitudes[]')
        location_names = request.form.getlist('location_names[]')
        
        # Validate selections
        if not selected_districts or not selected_levels:
            flash('Please select at least one district and one school level.', 'error')
            return redirect(url_for('configure'))
        
        if not latitudes or not longitudes:
            flash('Please provide at least one coordinate pair.', 'error')
            return redirect(url_for('configure'))
        
        if len(latitudes) != len(longitudes):
            flash('Latitude and longitude lists must have the same length.', 'error')
            return redirect(url_for('configure'))
        
        # Convert coordinates to float and prepare proposals
        base_proposals = []
        for i in range(len(latitudes)):
            try:
                # Check for empty or None values
                if not latitudes[i] or not longitudes[i] or latitudes[i].strip() == '' or longitudes[i].strip() == '':
                    flash(f'Empty coordinates for location {i+1}. Please provide valid latitude and longitude.', 'error')
                    return redirect(url_for('configure'))
                
                lat = float(latitudes[i].strip())
                lng = float(longitudes[i].strip())
                
                # Validate coordinate ranges
                if not (-90 <= lat <= 90):
                    flash(f'Invalid latitude {lat} for location {i+1}. Must be between -90 and 90.', 'error')
                    return redirect(url_for('configure'))
                
                if not (-180 <= lng <= 180):
                    flash(f'Invalid longitude {lng} for location {i+1}. Must be between -180 and 180.', 'error')
                    return redirect(url_for('configure'))
                
                name = location_names[i] if i < len(location_names) and location_names[i] and location_names[i].strip() else f"Proposed Site {i+1}"
                
                base_proposals.append({
                    'latitude': lat,
                    'longitude': lng,
                    'name': name
                })
            except (ValueError, TypeError):
                flash(f'Invalid coordinates for location {i+1}', 'error')
                return redirect(url_for('configure'))
        
        print(f"Analyzing {len(base_proposals)} proposed locations for {len(selected_levels)} school levels with {min_distance}km minimum distance")
        print(f"Selected districts: {selected_districts}")
        print(f"Selected levels: {selected_levels}")
        
        # Update minimum distance settings if custom value provided
        if min_distance != 2.0:
            for level in MIN_DISTANCES:
                MIN_DISTANCES[level] = min_distance
        
        # Determine which districts to use for filtering
        districts_filter = None if 'all' in selected_districts else selected_districts
        
        # Determine which levels to analyze
        levels_to_analyze = analyzer.schools_df['SchoolLevel'].unique().tolist() if 'all' in selected_levels else selected_levels
        
        # Create proposals for each location-level combination
        all_proposals = []
        for proposal in base_proposals:
            for level in levels_to_analyze:
                all_proposals.append({
                    'latitude': proposal['latitude'],
                    'longitude': proposal['longitude'],
                    'level': level,
                    'name': f"{proposal['name']} ({level})"
                })
        
        print(f"Generated {len(all_proposals)} total proposals for analysis")
        
        # Perform enhanced feasibility analysis
        all_results = analyzer.analyze_multiple_locations(
            all_proposals, 
            search_radius=20, 
            selected_districts=districts_filter
        )
        
        print(f"Analysis complete. Generated {len(all_results)} results")
        
        # Create enhanced map
        feasibility_map = analyzer.create_feasibility_map(all_results)
        map_html = feasibility_map._repr_html_() if feasibility_map else None
        
        # Calculate enhanced statistics
        total_proposed = len(all_results)
        feasible_count = sum(1 for r in all_results if r['is_feasible'])
        not_feasible_count = total_proposed - feasible_count
        highly_recommended = sum(1 for r in all_results if r['recommendation'] == 'HIGHLY RECOMMENDED')
        recommended = sum(1 for r in all_results if r['recommendation'] == 'RECOMMENDED')
        
        # Risk level distribution
        risk_levels = {}
        for result in all_results:
            risk_level = result['risk_level']
            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        # School level analysis
        level_analysis = {}
        for level in levels_to_analyze:
            level_results = [r for r in all_results if r['proposed_level'] == level]
            level_analysis[level] = {
                'total': len(level_results),
                'feasible': sum(1 for r in level_results if r['is_feasible']),
                'avg_conflicts': sum(r['same_level_conflicts'] for r in level_results) / len(level_results) if level_results else 0,
                'avg_students_nearby': sum(r.get('total_students_nearby', 0) for r in level_results) / len(level_results) if level_results else 0
            }
        
        # Store results in session for download (convert numpy types to native Python types)
        def convert_numpy_types(obj):
            """Convert numpy types to native Python types for JSON serialization"""
            if isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif hasattr(obj, 'tolist'):  # numpy array
                return obj.tolist()
            else:
                return obj
        
        # Convert all results to JSON-serializable format
        serializable_results = convert_numpy_types(all_results)
        serializable_statistics = convert_numpy_types({
            'total_proposed': total_proposed,
            'feasible_count': feasible_count,
            'not_feasible_count': not_feasible_count,
            'highly_recommended': highly_recommended,
            'recommended': recommended,
            'risk_levels': risk_levels,
            'level_analysis': level_analysis
        })
        
        session['latest_results'] = {
            'analysis_results': serializable_results,
            'selected_levels': selected_levels,
            'selected_districts': selected_districts,
            'min_distance': min_distance,
            'timestamp': datetime.now().isoformat(),
            'statistics': serializable_statistics
        }
        
        return render_template('results_elegant.html',
                             results=all_results,
                             school_level=', '.join(levels_to_analyze),
                             selected_levels=selected_levels,
                             selected_districts=selected_districts,
                             min_distance=min_distance,
                             feasible_count=feasible_count,
                             not_feasible_count=not_feasible_count,
                             highly_recommended=highly_recommended,
                             recommended=recommended,
                             total_proposed=total_proposed,
                             risk_levels=risk_levels,
                             level_analysis=level_analysis,
                             map_html=map_html,
                             center_lat=sum(r['latitude'] for r in all_results) / len(all_results) if all_results else 30.0,
                             center_lng=sum(r['longitude'] for r in all_results) / len(all_results) if all_results else 67.0)
        
    except Exception as e:
        print(f"Error in analyze route: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'Error during analysis: {str(e)}', 'error')
        return redirect(url_for('configure'))

@app.route('/load-sample')
def load_sample():
    # For demonstration, create a sample dataset
    sample_data = {
        'BemisCode': ['B001', 'B002', 'B003', 'B004', 'B005'],
        'SchoolName': ['Sample Primary School', 'Sample Middle School', 'Sample High School', 'Sample Secondary School', 'Sample Primary School 2'],
        'District': ['Quetta', 'Quetta', 'Ziarat', 'Ziarat', 'Quetta'],
        'Tehsil': ['Quetta', 'Quetta', 'Ziarat', 'Ziarat', 'Quetta'],
        'SubTehsil': ['Quetta', 'Quetta', 'Ziarat', 'Ziarat', 'Quetta'],
        'UC': ['UC1', 'UC2', 'UC3', 'UC4', 'UC5'],
        'VillageName': ['Village1', 'Village2', 'Village3', 'Village4', 'Village5'],
        'Gender': ['Boys', 'Girls', 'Boys', 'Girls', 'Co-Education'],
        'SchoolLevel': ['Primary', 'Middle', 'High', 'Higher Secondary', 'Primary'],
        'FunctionalStatus': ['Functional', 'Functional', 'Functional', 'Functional', 'Functional'],
        'ReasonOfNonFunctional': ['', '', '', '', ''],
        'Building': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
        'BuildingStructure': ['Concrete', 'Concrete', 'Concrete', 'Concrete', 'Concrete'],
        'BuildingCondition': ['Good', 'Good', 'Good', 'Good', 'Good'],
        'SpaceForNewRooms': ['Yes', 'Yes', 'No', 'No', 'Yes'],
        'BoundaryWall': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
        'BoundaryWallStructure': ['Concrete', 'Concrete', 'Concrete', 'Concrete', 'Concrete'],
        'BoundaryWallCondition': ['Good', 'Good', 'Good', 'Good', 'Good'],
        'ElectricityInSchool': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
        'TotalStudentProfileEntered': [150, 200, 300, 250, 100],
        'Source': ['Government', 'Government', 'Government', 'Government', 'Government'],
        '_xCord': [67.0103, 67.0203, 67.7256, 67.7356, 67.0303],  # Longitude
        '_yCord': [30.1798, 30.1898, 30.3822, 30.3922, 30.1998]   # Latitude
    }
    
    df = pd.DataFrame(sample_data)
    sample_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sample_schools.csv')
    df.to_csv(sample_path, index=False)
    
    success, message = analyzer.load_data(sample_path)
    
    if success:
        flash(f'{message} (Sample data loaded)', 'success')
        return redirect(url_for('configure'))
    else:
        flash(f'Error loading sample data: {message}', 'error')
        return redirect(url_for('index'))

@app.route('/download_results')
def download_results():
    """Download the latest analysis results"""
    try:
        # Get the most recent analysis results from session or use a default
        if 'latest_results' in session:
            results = session['latest_results']
            
            # Create DataFrame from results
            df_results = []
            for i, result in enumerate(results['analysis_results']):
                df_results.append({
                    'Location': result.get('location_name', f'Proposed Site {i+1}'),
                    'Latitude': result['latitude'],
                    'Longitude': result['longitude'],
                    'Feasible': 'Yes' if result['feasible'] else 'No',
                    'Nearest_School': result.get('nearest_school', {}).get('School_Name', 'N/A') if result.get('nearest_school') else 'N/A',
                    'Distance_km': round(result.get('distance_to_nearest', 0), 2) if result.get('distance_to_nearest') else 'N/A',
                    'School_Level': results['school_level'],
                    'Min_Distance_Required_km': results['min_distance'],
                    'Recommendation': 'Recommended' if result['feasible'] else 'Too close to existing school'
                })
            
            df = pd.DataFrame(df_results)
            
            # Create download filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"school_feasibility_analysis_{timestamp}.csv"
            filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            
            # Save to CSV
            df.to_csv(filepath, index=False)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            flash('No analysis results found. Please perform an analysis first.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error downloading results: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return '''
    <html>
    <head><title>School Feasibility System Health Check</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f0f0f0;">
        <h1 style="color: #2563eb;">🏫 School Feasibility System</h1>
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
    app.run(debug=True, port=5012, host='0.0.0.0')
