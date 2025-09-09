# BEF vs Government Schools Comparison System

A modern, elegant Flask web application for comparing the proximity and distribution of BEF (Balochistan Education Foundation) schools and Government schools using GIS mapping and spatial analysis.

## Features

- **File Upload**: Support for CSV and Excel files with automatic column detection
- **Data Validation**: Automatic coordinate validation and cleaning within Pakistan bounds
- **District Selection**: Interactive district selection with statistics
- **Proximity Analysis**: Configurable distance-based analysis (1-50 km radius)
- **Interactive Maps**: Folium-powered maps with school markers and proximity connections
- **Statistical Summary**: Comprehensive analysis statistics and insights
- **CSV Export**: Download detailed results for further analysis
- **Responsive Design**: Modern, government-grade UI with Bootstrap 5

## Requirements

- Python 3.8+
- Flask 2.3+
- pandas 2.0+
- folium 0.14+
- geopy 2.4+
- Other dependencies listed in requirements.txt

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   - Open your browser and go to `http://localhost:5000`

3. **Upload datasets**:
   - Upload government schools dataset (CSV/Excel)
   - Upload BEF schools dataset (CSV/Excel)
   - Required columns: School Name, District, Latitude, Longitude

4. **Configure analysis**:
   - Select districts for analysis
   - Set maximum distance for proximity analysis (1-50 km)
   - Choose analysis type

5. **View results**:
   - Interactive map with school locations and connections
   - Statistical summary and analysis details
   - Download CSV report

## Dataset Requirements

### Required Columns (automatically detected):
- **School Name**: Name of the educational institution
- **District**: Administrative district name
- **Latitude**: Geographic latitude coordinate
- **Longitude**: Geographic longitude coordinate

### File Formats:
- CSV (.csv)
- Excel (.xlsx, .xls)

### Coordinate Requirements:
- Valid latitude/longitude coordinates
- Within Pakistan geographical bounds (23-38°N, 60-78°E)
- Numeric format (degrees decimal)

## Project Structure

```
BEFComparisonSystem_New/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── index.html        # Upload page
│   ├── configure.html    # Configuration page
│   └── results.html      # Results page
├── static/               # Static files (CSS, JS, images)
├── uploads/              # Uploaded files storage
├── downloads/            # Generated CSV files
└── data/                 # Sample data files
```

## API Endpoints

- `GET /` - Main upload page
- `POST /upload` - File upload and processing
- `GET /configure` - Analysis configuration page
- `POST /analyze` - Run proximity analysis
- `GET /download/<filename>` - Download CSV results
- `GET /status` - API status endpoint

## Features in Detail

### Automatic Column Detection
The system automatically detects column names for:
- School names (keywords: name, school, institution)
- Districts (keywords: district, tehsil, region, area)
- Latitude (keywords: lat, latitude, y)
- Longitude (keywords: lon, lng, long, longitude, x)

### Data Cleaning & Validation
- Converts coordinates to numeric format
- Removes invalid/missing coordinates
- Filters coordinates within Pakistan bounds
- Handles various data formats and encodings

### Proximity Analysis
- Configurable distance radius (1-50 km)
- Geodesic distance calculations using geopy
- Identifies government schools with nearby BEF schools
- Creates visual connections on interactive map

### Interactive Mapping
- Folium-based interactive maps
- Blue markers for government schools
- Red markers for BEF schools
- Green lines showing proximity connections
- Popup information for each school

## Troubleshooting

### Common Issues:

1. **File upload errors**: Ensure files are in CSV/Excel format with required columns
2. **Coordinate validation errors**: Check that coordinates are numeric and within Pakistan bounds
3. **No districts showing**: Verify both datasets have valid district information
4. **Map not loading**: Check internet connection for map tiles

### Error Messages:
- Clear error messages guide users through data requirements
- Flash messages provide feedback for all operations
- Validation errors highlight specific data issues

## License

This project is developed for educational and administrative purposes. Please ensure compliance with data privacy and usage policies when handling school location data.

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.
