import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import folium
from folium.plugins import MarkerCluster

app = Flask(__name__)
app.secret_key = 'gov_bef_map_secret_2025'
app.config['UPLOAD_FOLDER'] = 'GovBEFMap/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flexible column name handling
LAT_CANDIDATES = ['Latitude', 'latitude', 'lat', '_yCord', 'y', 'Y', 'Lat']
LON_CANDIDATES = ['Longitude', 'longitude', 'lon', 'lng', '_xCord', 'x', 'X', 'Long', 'Longitute']
NAME_CANDIDATES = ['SchoolName', 'School Name', 'Name', 'name']
DISTRICT_CANDIDATES = ['District', 'district', 'DISTRICT']


def read_schools_csv(path: str) -> pd.DataFrame:
	"""Read a CSV and normalize to columns: name, lat, lon, district (optional)."""
	df = pd.read_csv(path)
	# find lat/lon
	lat_col = next((c for c in LAT_CANDIDATES if c in df.columns), None)
	lon_col = next((c for c in LON_CANDIDATES if c in df.columns), None)
	name_col = next((c for c in NAME_CANDIDATES if c in df.columns), None)
	dist_col = next((c for c in DISTRICT_CANDIDATES if c in df.columns), None)
	if not lat_col or not lon_col:
		raise ValueError('Latitude/Longitude column not found in CSV')
	# build normalized frame
	ndf = pd.DataFrame()
	ndf['name'] = df[name_col] if name_col else 'School'
	ndf['lat'] = pd.to_numeric(df[lat_col], errors='coerce')
	ndf['lon'] = pd.to_numeric(df[lon_col], errors='coerce')
	if dist_col:
		ndf['district'] = df[dist_col].astype(str)
	# filter invalid
	ndf = ndf.dropna(subset=['lat', 'lon'])
	ndf = ndf[(ndf['lat'] != 0) & (ndf['lon'] != 0)]
	return ndf


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/plot', methods=['POST'])
def plot():
	try:
		gov_file = request.files.get('gov_csv')
		bef_file = request.files.get('bef_csv')
		if not gov_file or not bef_file:
			flash('Please select both files', 'error')
			return redirect(url_for('index'))

		gov_name = secure_filename(gov_file.filename)
		bef_name = secure_filename(bef_file.filename)
		gov_path = os.path.join(app.config['UPLOAD_FOLDER'], f'gov_{gov_name}')
		bef_path = os.path.join(app.config['UPLOAD_FOLDER'], f'bef_{bef_name}')
		gov_file.save(gov_path)
		bef_file.save(bef_path)

		gov_df = read_schools_csv(gov_path)
		bef_df = read_schools_csv(bef_path)

		# determine center
		all_lats = list(gov_df['lat']) + list(bef_df['lat'])
		all_lons = list(gov_df['lon']) + list(bef_df['lon'])
		center = [sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)] if all_lats else [30.2, 67.0]

		m = folium.Map(location=center, zoom_start=7, tiles=None)
		folium.TileLayer('OpenStreetMap', name='Street').add_to(m)
		folium.TileLayer(
			tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
			attr='Esri', name='Satellite'
		).add_to(m)

		gov_cluster = MarkerCluster(name='Government Schools').add_to(m)
		bef_cluster = MarkerCluster(name='BEF Schools').add_to(m)

		# Government markers: blue building icon
		for _, row in gov_df.iterrows():
			popup = folium.Popup(f"<b>{row.get('name','Government School')}</b>", max_width=250)
			folium.Marker(
				location=[row['lat'], row['lon']],
				popup=popup,
				icon=folium.Icon(color='blue', icon='building', prefix='fa')
			).add_to(gov_cluster)

		# BEF markers: green graduation-cap icon
		for _, row in bef_df.iterrows():
			popup = folium.Popup(f"<b>{row.get('name','BEF School')}</b>", max_width=250)
			folium.Marker(
				location=[row['lat'], row['lon']],
				popup=popup,
				icon=folium.Icon(color='green', icon='graduation-cap', prefix='fa')
			).add_to(bef_cluster)

		folium.LayerControl(collapsed=False).add_to(m)
		map_html = m._repr_html_()
		return render_template('results.html', map_html=map_html, gov_count=len(gov_df), bef_count=len(bef_df))
	except Exception as e:
		flash(f'Error: {e}', 'error')
		return redirect(url_for('index'))


if __name__ == '__main__':
	port = int(os.environ.get('PORT', '5055'))
	print(f"Starting GovBEFMap on http://localhost:{port}")
	app.run(debug=True, host='0.0.0.0', port=port) 