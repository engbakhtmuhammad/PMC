# School Progression Analysis System

A comprehensive web application for analyzing school progression paths in Balochistan, Pakistan. This system helps educational planners identify the nearest progression schools for students transitioning between educational levels (Primary → Middle → High → Higher Secondary).

## Features

### 🎯 Core Functionality
- **Two-Phase Upload System**: Upload complete school database first, then target schools for analysis
- **Intelligent Progression Mapping**: Automatically finds nearest progression schools based on educational levels
- **Distance-Based Analysis**: Configurable maximum distance parameters for realistic recommendations
- **District Filtering**: Focus analysis on specific districts or analyze all districts

### 📊 Advanced Analytics
- **Interactive Map Visualization**: Folium-powered maps with connecting lines between target and progression schools
- **Comprehensive Reporting**: Detailed CSV reports with distance calculations and school information
- **Statistical Summary**: Analysis overview with success rates and average distances
- **Flexible School Type Filtering**: Include/exclude government or private schools

### 🎨 Modern UI/UX
- **Government-Grade Design**: Professional, accessible interface following government design standards
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices
- **Elegant Animations**: Smooth transitions and loading states for better user experience
- **Drag & Drop Upload**: Intuitive file upload with progress indicators

## School Level Progression Logic

The system follows the standard Pakistani education system progression:
- **Primary** → **Middle School**
- **Middle** → **High School** 
- **High** → **Higher Secondary**
- **Higher Secondary** → (No progression within basic education)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd /path/to/SchoolProgressionSystem
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your web browser and navigate to: `http://localhost:5013`

## Data Format Requirements

### School Database CSV Format
Your complete school database should include these columns (exact names not required - the system will map them):
- **School Name**: Name of the school
- **Latitude**: Geographic latitude coordinate
- **Longitude**: Geographic longitude coordinate  
- **District**: District name
- **Level**: School level (Primary, Middle, High, Higher Secondary)
- **Type** (optional): Government/Private classification

### Target Schools CSV Format
The target schools file should follow the same format as the complete database. These are the schools for which you want to find progression options.

### Sample Data
The system includes sample data for testing. Click "Try with Sample Data" on the main page to explore the functionality.

## Usage Guide

### Step 1: Upload Complete School Database
1. Navigate to the main page
2. Upload your complete school database CSV/Excel file in the first upload area
3. Click "Upload School Database" to process the file

### Step 2: Upload Target Schools
1. Upload the target schools file in the second upload area
2. Click "Upload Target Schools" to process the file

### Step 3: Configure Analysis
1. After both uploads, you'll be redirected to the configuration page
2. Select the target district or choose "All Districts"
3. Set the maximum search distance (1-100 km)
4. Choose additional filters (school type, sorting preferences)
5. Click "Start Analysis"

### Step 4: Review Results
1. View the interactive map showing progression connections
2. Review the detailed results table with distance calculations
3. Download CSV reports and interactive maps
4. Use search functionality to find specific schools

## File Structure

```
SchoolProgressionSystem/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── templates/
│   ├── index_elegant.html         # Main upload page
│   ├── configure_elegant.html     # Configuration page
│   └── results_elegant.html       # Results display page
└── static/
    └── css/
        └── elegant-enhancements.css # Additional styling
```

## API Endpoints

- `GET /` - Main upload page
- `POST /upload_full_schools` - Upload complete school database
- `POST /upload_target_schools` - Upload target schools
- `GET /configure` - Configuration page
- `POST /configure` - Process configuration and run analysis
- `GET /results` - Display analysis results
- `GET /download_csv` - Download results as CSV
- `GET /download_map` - Download interactive map as HTML
- `POST /load_sample_data` - Load sample data for testing
- `GET /health` - Health check endpoint

## Technical Details

### Backend Components
- **Flask Web Framework**: Handles routing and server logic
- **Pandas**: Data processing and CSV handling
- **NumPy**: Numerical computations for distance calculations
- **Scikit-learn**: Haversine distance calculations
- **Folium**: Interactive map generation
- **Openpyxl**: Excel file support

### Key Classes
- **SchoolProgressionAnalyzer**: Core analysis engine
  - Data loading and validation
  - Progression path identification
  - Distance calculations
  - Map generation
  - Report creation

### Data Processing
1. **Column Mapping**: Flexible CSV column detection and mapping
2. **Data Validation**: Ensures required fields are present and valid
3. **Geographic Calculations**: Haversine formula for accurate distance measurements
4. **Level Mapping**: Standardizes school level terminology

## Configuration Options

### Distance Parameters
- **Range**: 1-100 kilometers
- **Default**: 20 kilometers
- **Purpose**: Limits search radius for realistic commuting distances

### School Type Filters
- **All Schools**: Include both government and private schools
- **Government Only**: Include only government schools
- **Private Only**: Include only private schools

### Sorting Options
- **Distance**: Sort by nearest schools first
- **Alphabetical**: Sort by school name
- **District**: Sort by district name

## Troubleshooting

### Common Issues

1. **File Upload Errors**
   - Ensure CSV files have proper encoding (UTF-8 recommended)
   - Check that required columns are present
   - Verify file size is under 50MB

2. **No Progression Found**
   - Increase maximum distance parameter
   - Check if target schools are at the highest level (Higher Secondary)
   - Verify district names match between datasets

3. **Map Not Loading**
   - Ensure geographic coordinates are valid
   - Check internet connection for map tiles
   - Verify browser supports modern JavaScript

### Data Quality Tips
- Ensure latitude/longitude coordinates are accurate
- Use consistent district name spelling
- Standardize school level terminology
- Remove duplicate entries

## Contributing

This system is designed for the Government of Balochistan Education Department. For modifications or enhancements, please ensure:
- Code follows existing style and structure
- New features include proper error handling
- UI changes maintain accessibility standards
- Documentation is updated accordingly

## License

Developed for the Government of Balochistan - Education Department. All rights reserved.

## Support

For technical support or questions about the School Progression Analysis System, please contact the development team or refer to the system documentation.

---

**Government of Balochistan - Education Department**  
*Empowering Education Through Technology*
