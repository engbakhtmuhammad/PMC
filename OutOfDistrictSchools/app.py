import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from werkzeug.utils import secure_filename
from shapely.geometry import Point, Polygon
import folium
from folium import plugins
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Approximate boundary coordinates for Killa Saifullah district
# These are rough coordinates - you may need to adjust based on exact district boundaries
KILLA_SAIFULLAH_BOUNDARIES = [
    (30.8500, 68.7500),  # North-West
    (30.8500, 69.2000),  # North-East
    (30.4500, 69.2000),  # South-East
    (30.4500, 68.7500),  # South-West
    (30.8500, 68.7500)   # Close the polygon
]

def is_point_in_killa_saifullah(lat, lon):
    """Check if a point (lat, lon) is within Killa Saifullah district boundaries"""
    try:
        point = Point(lon, lat)
        polygon = Polygon(KILLA_SAIFULLAH_BOUNDARIES)
        return polygon.contains(point)
    except:
        return False

def allowed_file(filename):
    """Check if uploaded file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xlsx', 'xls']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read Excel file
            df = pd.read_excel(filepath)
            
            # Expected columns: school name, bemis code, latitude, longitude, district
            expected_columns = ['school_name', 'bemis_code', 'latitude', 'longitude', 'district']
            
            # Check if required columns exist (case insensitive)
            df_columns_lower = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Map actual columns to expected columns
            column_mapping = {}
            for i, col in enumerate(df.columns):
                col_lower = col.lower().replace(' ', '_').strip()
                if 'school' in col_lower and 'name' in col_lower:
                    column_mapping[col] = 'school_name'
                elif 'bemis' in col_lower or 'code' in col_lower:
                    column_mapping[col] = 'bemis_code'
                elif 'lat' in col_lower:
                    column_mapping[col] = 'latitude'
                elif 'lon' in col_lower or 'lng' in col_lower:
                    column_mapping[col] = 'longitude'
                elif 'district' in col_lower:
                    column_mapping[col] = 'district'
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Check for missing required columns
            missing_cols = [col for col in expected_columns if col not in df.columns]
            if missing_cols:
                flash(f'Missing required columns: {", ".join(missing_cols)}')
                return redirect(url_for('index'))
            
            # Clean and validate data
            df = df.dropna(subset=['latitude', 'longitude'])
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df = df.dropna(subset=['latitude', 'longitude'])
            
            # Check which schools are in Killa Saifullah
            df['in_killa_saifullah'] = df.apply(
                lambda row: is_point_in_killa_saifullah(row['latitude'], row['longitude']), 
                axis=1
            )
            
            # Separate schools
            schools_in_district = df[df['in_killa_saifullah']].copy()
            schools_outside_district = df[~df['in_killa_saifullah']].copy()
            
            # Save processed data
            schools_in_district.to_csv('static/schools_in_killa_saifullah.csv', index=False)
            schools_outside_district.to_csv('static/schools_outside_killa_saifullah.csv', index=False)
            
            return render_template('results.html', 
                                 schools_in=schools_in_district.to_dict('records'),
                                 schools_out=schools_outside_district.to_dict('records'),
                                 total_schools=len(df),
                                 schools_in_count=len(schools_in_district),
                                 schools_out_count=len(schools_outside_district))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload an Excel file (.xlsx or .xls)')
        return redirect(url_for('index'))

@app.route('/map')
def show_map():
    """Display interactive map with all schools"""
    try:
        # Read processed data
        schools_in = pd.read_csv('static/schools_in_killa_saifullah.csv')
        schools_out = pd.read_csv('static/schools_outside_killa_saifullah.csv')
        
        # Create map centered on Killa Saifullah
        m = folium.Map(location=[30.65, 68.975], zoom_start=10)
        
        # Add district boundary
        folium.Polygon(
            locations=[(lat, lon) for lon, lat in KILLA_SAIFULLAH_BOUNDARIES],
            color='red',
            weight=3,
            fillColor='red',
            fillOpacity=0.1,
            popup='Killa Saifullah District Boundary'
        ).add_to(m)
        
        # Add schools inside district (green markers)
        for _, school in schools_in.iterrows():
            folium.Marker(
                [school['latitude'], school['longitude']],
                popup=f"""
                <b>{school['school_name']}</b><br>
                BEMIS Code: {school['bemis_code']}<br>
                District: {school['district']}<br>
                <a href='https://www.google.com/maps?q={school['latitude']},{school['longitude']}' target='_blank'>
                Navigate on Google Maps</a>
                """,
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
        
        # Add schools outside district (red markers)
        for _, school in schools_out.iterrows():
            folium.Marker(
                [school['latitude'], school['longitude']],
                popup=f"""
                <b>{school['school_name']}</b><br>
                BEMIS Code: {school['bemis_code']}<br>
                District: {school['district']}<br>
                <a href='https://www.google.com/maps?q={school['latitude']},{school['longitude']}' target='_blank'>
                Navigate on Google Maps</a>
                """,
                icon=folium.Icon(color='red', icon='exclamation-sign')
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px;
                    ">
        <p><b>Legend</b></p>
        <p><i class="fa fa-map-marker fa-2x" style="color:green"></i> Schools in District</p>
        <p><i class="fa fa-map-marker fa-2x" style="color:red"></i> Schools outside District</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m._repr_html_()
        
    except Exception as e:
        return f"Error creating map: {str(e)}"

@app.route('/navigate/<float:lat>/<float:lon>')
def navigate(lat, lon):
    """Redirect to Google Maps for navigation"""
    google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    return redirect(google_maps_url)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
