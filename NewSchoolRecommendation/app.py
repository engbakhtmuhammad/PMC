import pandas as pd
import numpy as np
import math
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from geopy.distance import geodesic
import folium
from folium import plugins
import uuid

app = Flask(__name__)
app.secret_key = 'school_feasibility_secret_key_2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['REPORTS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Required columns for school data
REQUIRED_COLUMNS = [
    'BemisCode', 'SchoolName', 'District', 'Tehsil', 'SubTehsil', 'UC', 
    'VillageName', 'Gender', 'SchoolLevel', 'FunctionalStatus', 
    'Building', 'BuildingCondition', 'ElectricityInSchool', 
    'TotalStudentProfileEntered', '_xCord', '_yCord'
]

# School level hierarchy for recommendations
LEVEL_HIERARCHY = {
    'Primary': 1,
    'Middle': 2,
    'High': 3,
    'Higher Secondary': 4
}

class SchoolFeasibilityAnalyzer:
    def __init__(self):
        self.schools_df = None
        self.analysis_results = []
        self.analysis_id = None
        
    def load_schools_data(self, file_path):
        """Load and validate the uploaded CSV file with existing schools"""
        try:
            # Read CSV file
            self.schools_df = pd.read_csv(file_path)
            
            # Handle coordinate columns with multiple possible names
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
            
            # Handle missing columns with defaults
            if 'TotalStudentProfileEntered' not in self.schools_df.columns:
                self.schools_df['TotalStudentProfileEntered'] = 50
            
            if 'SchoolLevel' not in self.schools_df.columns:
                self.schools_df['SchoolLevel'] = 'Primary'
            
            if 'FunctionalStatus' not in self.schools_df.columns:
                self.schools_df['FunctionalStatus'] = 'Functional'
            
            # Clean and validate data
            self.schools_df = self.schools_df.dropna(subset=['_xCord', '_yCord'])
            self.schools_df['TotalStudentProfileEntered'] = pd.to_numeric(
                self.schools_df['TotalStudentProfileEntered'], errors='coerce'
            ).fillna(50)
            
            # Filter out invalid coordinates
            self.schools_df = self.schools_df[
                (self.schools_df['_xCord'].notna()) &
                (self.schools_df['_yCord'].notna()) &
                (self.schools_df['_xCord'] != 0) &
                (self.schools_df['_yCord'] != 0) &
                (self.schools_df['_yCord'].between(-90, 90)) &
                (self.schools_df['_xCord'].between(-180, 180))
            ]
            
            return True, f"Successfully loaded {len(self.schools_df)} schools with valid coordinates"
            
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using geodesic calculation"""
        try:
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        except:
            return float('inf')
    
    def analyze_coordinate_feasibility(self, lat, lon, district=None, analysis_params=None):
        """Analyze feasibility of building a school at given coordinates"""
        if self.schools_df is None:
            return {
                'feasible': False,
                'reason': 'No school data loaded',
                'nearby_schools': [],
                'recommendations': []
            }
        
        # Default analysis parameters
        if analysis_params is None:
            analysis_params = {
                'min_distance_km': 2.0,
                'primary_min_distance': 1.0,
                'middle_min_distance': 2.0,
                'high_min_distance': 3.0,
                'higher_secondary_min_distance': 5.0,
                'max_search_radius': 10.0
            }
        
        # Filter schools by district if specified
        schools_to_check = self.schools_df.copy()
        if district and district != 'all':
            schools_to_check = schools_to_check[schools_to_check['District'] == district]
        
        # Calculate distances to all schools
        schools_to_check['distance'] = schools_to_check.apply(
            lambda row: self.calculate_distance(
                lat, lon, row['_yCord'], row['_xCord']
            ), axis=1
        )
        
        # Find nearby schools within search radius
        nearby_schools = schools_to_check[
            schools_to_check['distance'] <= analysis_params['max_search_radius']
        ].sort_values('distance')
        
        # Analyze feasibility by school level
        level_analysis = {}
        overall_feasible = True
        issues = []
        recommendations = []
        
        # Check minimum distances for each school level
        for level, min_dist_key in [
            ('Primary', 'primary_min_distance'),
            ('Middle', 'middle_min_distance'), 
            ('High', 'high_min_distance'),
            ('Higher Secondary', 'higher_secondary_min_distance')
        ]:
            min_distance = analysis_params[min_dist_key]
            level_schools = nearby_schools[nearby_schools['SchoolLevel'] == level]
            
            if len(level_schools) > 0:
                closest_distance = level_schools['distance'].min()
                closest_school = level_schools.iloc[0]
                
                level_analysis[level] = {
                    'closest_distance': closest_distance,
                    'min_required': min_distance,
                    'feasible': closest_distance >= min_distance,
                    'closest_school': {
                        'name': closest_school['SchoolName'],
                        'distance': closest_distance,
                        'bemis_code': closest_school['BemisCode']
                    }
                }
                
                if closest_distance < min_distance:
                    overall_feasible = False
                    issues.append(f"Too close to {level} school '{closest_school['SchoolName']}' ({closest_distance:.2f}km, minimum: {min_distance}km)")
            else:
                level_analysis[level] = {
                    'closest_distance': None,
                    'min_required': min_distance,
                    'feasible': True,
                    'closest_school': None
                }
                recommendations.append(f"Good location for {level} school - no nearby {level} schools found")
        
        # Generate overall recommendation
        if overall_feasible:
            if len(nearby_schools) == 0:
                recommendation = "HIGHLY RECOMMENDED - No schools within 10km radius"
                feasibility_score = 10
            elif len(nearby_schools) <= 2:
                recommendation = "RECOMMENDED - Limited nearby schools, good for new establishment"
                feasibility_score = 8
            else:
                recommendation = "FEASIBLE - Some nearby schools but acceptable distances maintained"
                feasibility_score = 6
        else:
            recommendation = "NOT RECOMMENDED - Too close to existing schools"
            feasibility_score = 2
        
        return {
            'feasible': overall_feasible,
            'feasibility_score': feasibility_score,
            'recommendation': recommendation,
            'issues': issues,
            'level_analysis': level_analysis,
            'nearby_schools': nearby_schools.head(10).to_dict('records'),
            'recommendations': recommendations,
            'total_nearby': len(nearby_schools),
            'analysis_params': analysis_params
        }
    
    def batch_analyze_coordinates(self, coordinates_list, analysis_params=None):
        """Analyze multiple coordinates for feasibility"""
        self.analysis_id = str(uuid.uuid4())
        results = []
        
        for i, coord_data in enumerate(coordinates_list):
            lat = coord_data.get('latitude')
            lon = coord_data.get('longitude')
            district = coord_data.get('district', 'all')
            name = coord_data.get('name', f'Proposed Site {i+1}')
            
            if lat is None or lon is None:
                result = {
                    'site_id': i+1,
                    'name': name,
                    'latitude': lat,
                    'longitude': lon,
                    'district': district,
                    'feasible': False,
                    'reason': 'Invalid coordinates provided',
                    'analysis': None
                }
            else:
                analysis = self.analyze_coordinate_feasibility(lat, lon, district, analysis_params)
                result = {
                    'site_id': i+1,
                    'name': name,
                    'latitude': lat,
                    'longitude': lon,
                    'district': district,
                    'feasible': analysis['feasible'],
                    'feasibility_score': analysis.get('feasibility_score', 0),
                    'recommendation': analysis.get('recommendation', ''),
                    'analysis': analysis
                }
            
            results.append(result)
        
        self.analysis_results = results
        return results
    
    def create_feasibility_map(self, analysis_results=None):
        """Create an interactive map showing feasibility analysis"""
        if analysis_results is None:
            analysis_results = self.analysis_results
        
        if not analysis_results or self.schools_df is None:
            return None
        
        # Calculate map center from proposed sites
        valid_coords = [(r['latitude'], r['longitude']) for r in analysis_results 
                       if r['latitude'] is not None and r['longitude'] is not None]
        
        if not valid_coords:
            return None
        
        center_lat = sum(coord[0] for coord in valid_coords) / len(valid_coords)
        center_lon = sum(coord[1] for coord in valid_coords) / len(valid_coords)
        
        # Create map with multiple tile layers
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles=None
        )
        
        # Add tile layers
        folium.TileLayer('OpenStreetMap', name='Street Map', overlay=False, control=True).add_to(m)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri', name='Satellite View', overlay=False, control=True
        ).add_to(m)
        
        # Add existing schools (smaller markers)
        for _, school in self.schools_df.iterrows():
            if pd.isna(school.get('_yCord')) or pd.isna(school.get('_xCord')):
                continue
            
            level_colors = {
                'Primary': '#3498db',
                'Middle': '#2ecc71',
                'High': '#f39c12', 
                'Higher Secondary': '#e74c3c'
            }
            
            color = level_colors.get(school['SchoolLevel'], '#95a5a6')
            
            popup_html = f"""
            <div style="width: 250px; font-family: Arial;">
                <h5 style="color: #2c3e50; margin-bottom: 10px;">
                    🏫 {school['SchoolName']}
                </h5>
                <p><strong>Level:</strong> {school['SchoolLevel']}</p>
                <p><strong>District:</strong> {school['District']}</p>
                <p><strong>Students:</strong> {school['TotalStudentProfileEntered']}</p>
                <p><strong>Status:</strong> {school['FunctionalStatus']}</p>
            </div>
            """
            
            folium.CircleMarker(
                location=[school['_yCord'], school['_xCord']],
                radius=4,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{school['SchoolName']} ({school['SchoolLevel']})",
                color='white',
                weight=1,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(m)
        
        # Add proposed sites with feasibility indicators
        for result in analysis_results:
            if result['latitude'] is None or result['longitude'] is None:
                continue
            
            # Determine marker style based on feasibility
            if result['feasible']:
                icon_color = 'green'
                icon_symbol = 'check'
                marker_color = '#28a745'
            else:
                icon_color = 'red'
                icon_symbol = 'times'
                marker_color = '#dc3545'
            
            # Create detailed popup
            analysis = result.get('analysis', {})
            nearby_count = analysis.get('total_nearby', 0)
            
            popup_html = f"""
            <div style="width: 300px; font-family: Arial;">
                <h4 style="color: {marker_color}; margin-bottom: 10px;">
                    {'✅' if result['feasible'] else '❌'} {result['name']}
                </h4>
                <h5 style="color: #2c3e50;">{result['recommendation']}</h5>
                <p><strong>Feasibility Score:</strong> {result.get('feasibility_score', 0)}/10</p>
                <p><strong>Coordinates:</strong> {result['latitude']:.6f}, {result['longitude']:.6f}</p>
                <p><strong>Nearby Schools:</strong> {nearby_count} within 10km</p>
            """
            
            if analysis.get('issues'):
                popup_html += "<div style='background: #fff3cd; padding: 8px; margin: 8px 0; border-radius: 4px;'>"
                popup_html += "<strong>Issues:</strong><ul>"
                for issue in analysis['issues']:
                    popup_html += f"<li>{issue}</li>"
                popup_html += "</ul></div>"
            
            if analysis.get('recommendations'):
                popup_html += "<div style='background: #d4edda; padding: 8px; margin: 8px 0; border-radius: 4px;'>"
                popup_html += "<strong>Recommendations:</strong><ul>"
                for rec in analysis['recommendations']:
                    popup_html += f"<li>{rec}</li>"
                popup_html += "</ul></div>"
            
            popup_html += "</div>"
            
            folium.Marker(
                location=[result['latitude'], result['longitude']],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{result['name']} - {'FEASIBLE' if result['feasible'] else 'NOT FEASIBLE'}",
                icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix='fa')
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; top: 10px; right: 10px; width: 250px; 
                    background-color: rgba(255, 255, 255, 0.95); border: 2px solid #333; 
                    border-radius: 10px; padding: 15px; font-size: 12px; font-family: Arial;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); z-index: 9999;">
        <h4 style="margin: 0 0 10px 0; color: #2c3e50;">School Feasibility Map</h4>
        <p style="margin: 5px 0;"><i class="fa fa-check" style="color: green;"></i> Feasible Location</p>
        <p style="margin: 5px 0;"><i class="fa fa-times" style="color: red;"></i> Not Feasible</p>
        <hr style="margin: 10px 0;">
        <h5 style="margin: 5px 0; color: #34495e;">Existing Schools:</h5>
        <p style="margin: 3px 0;"><i class="fa fa-circle" style="color: #3498db;"></i> Primary</p>
        <p style="margin: 3px 0;"><i class="fa fa-circle" style="color: #2ecc71;"></i> Middle</p>
        <p style="margin: 3px 0;"><i class="fa fa-circle" style="color: #f39c12;"></i> High</p>
        <p style="margin: 3px 0;"><i class="fa fa-circle" style="color: #e74c3c;"></i> Higher Sec.</p>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        folium.LayerControl().add_to(m)
        
        return m

# Global analyzer instance
analyzer = SchoolFeasibilityAnalyzer()

@app.route('/')
def index():
    """Main page for file upload"""
    return render_template('index.html', required_columns=REQUIRED_COLUMNS)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle school data file upload"""
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
        success, message = analyzer.load_schools_data(filepath)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('coordinate_input'))
        else:
            flash(message, 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/coordinate-input')
def coordinate_input():
    """Page for inputting proposed school coordinates"""
    if analyzer.schools_df is None:
        flash('Please upload school data first', 'error')
        return redirect(url_for('index'))
    
    # Get available districts for filtering
    districts = sorted(analyzer.schools_df['District'].unique().tolist())
    return render_template('coordinate_input.html', districts=districts)

@app.route('/analyze', methods=['POST'])
def analyze_coordinates():
    """Analyze the submitted coordinates for feasibility"""
    if analyzer.schools_df is None:
        flash('Please upload school data first', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get analysis parameters
        analysis_params = {
            'primary_min_distance': float(request.form.get('primary_distance', 1.0)),
            'middle_min_distance': float(request.form.get('middle_distance', 2.0)),
            'high_min_distance': float(request.form.get('high_distance', 3.0)),
            'higher_secondary_min_distance': float(request.form.get('higher_secondary_distance', 5.0)),
            'max_search_radius': float(request.form.get('search_radius', 10.0))
        }
        
        # Parse coordinates from form
        coordinates_data = []
        coordinate_entries = request.form.getlist('coordinates')
        
        for entry in coordinate_entries:
            if entry.strip():
                try:
                    coord_data = json.loads(entry)
                    coordinates_data.append(coord_data)
                except json.JSONDecodeError:
                    continue
        
        if not coordinates_data:
            flash('No valid coordinates provided', 'error')
            return redirect(url_for('coordinate_input'))
        
        # Perform analysis
        results = analyzer.batch_analyze_coordinates(coordinates_data, analysis_params)
        
        # Create map
        map_obj = analyzer.create_feasibility_map(results)
        map_html = map_obj._repr_html_() if map_obj else None
        
        # Calculate summary statistics
        total_sites = len(results)
        feasible_sites = sum(1 for r in results if r['feasible'])
        avg_score = sum(r.get('feasibility_score', 0) for r in results) / total_sites if total_sites > 0 else 0
        
        summary_stats = {
            'total_sites': total_sites,
            'feasible_sites': feasible_sites,
            'not_feasible_sites': total_sites - feasible_sites,
            'feasibility_percentage': (feasible_sites / total_sites * 100) if total_sites > 0 else 0,
            'average_score': avg_score
        }
        
        return render_template('results.html', 
                             results=results, 
                             map_html=map_html,
                             summary_stats=summary_stats,
                             analysis_params=analysis_params,
                             analysis_id=analyzer.analysis_id)
        
    except Exception as e:
        flash(f'Error during analysis: {str(e)}', 'error')
        return redirect(url_for('coordinate_input'))

@app.route('/download-report/<analysis_id>')
def download_report(analysis_id):
    """Download analysis results as CSV"""
    if not analyzer.analysis_results:
        flash('No analysis results available', 'error')
        return redirect(url_for('index'))
    
    try:
        # Create CSV data
        csv_data = []
        for result in analyzer.analysis_results:
            csv_row = {
                'Site_ID': result['site_id'],
                'Site_Name': result['name'],
                'Latitude': result['latitude'],
                'Longitude': result['longitude'],
                'District': result['district'],
                'Feasible': 'Yes' if result['feasible'] else 'No',
                'Feasibility_Score': result.get('feasibility_score', 0),
                'Recommendation': result.get('recommendation', ''),
                'Nearby_Schools_Count': result['analysis'].get('total_nearby', 0) if result.get('analysis') else 0
            }
            
            # Add level-specific analysis
            if result.get('analysis') and result['analysis'].get('level_analysis'):
                for level, analysis in result['analysis']['level_analysis'].items():
                    csv_row[f'{level}_Closest_Distance_km'] = analysis.get('closest_distance')
                    csv_row[f'{level}_Min_Required_km'] = analysis.get('min_required')
                    csv_row[f'{level}_Feasible'] = 'Yes' if analysis.get('feasible') else 'No'
            
            csv_data.append(csv_row)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(csv_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'school_feasibility_analysis_{timestamp}.csv'
        filepath = os.path.join(app.config['REPORTS_FOLDER'], filename)
        
        df.to_csv(filepath, index=False)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'School Feasibility Analysis System',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5011)
