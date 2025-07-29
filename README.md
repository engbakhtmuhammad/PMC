# Killa Saifullah School Location Checker

A web application to verify if schools are located within the Killa Saifullah district boundaries based on their GPS coordinates.

## Features

- **Excel File Upload**: Upload Excel files containing school data
- **Location Verification**: Automatically checks if schools are within Killa Saifullah district
- **Interactive Map**: View all schools on an interactive map with district boundaries
- **Navigation Integration**: Direct links to Google Maps for each school location
- **Data Export**: Download filtered results as CSV files
- **Responsive Design**: Modern, mobile-friendly interface

## Required Excel Columns

Your Excel file should contain the following columns (case-insensitive):
- **School Name** (or any column containing "school" and "name")
- **BEMIS Code** (or any column containing "bemis" or "code")
- **Latitude** (or any column containing "lat")
- **Longitude** (or any column containing "lon" or "lng")
- **District** (or any column containing "district")

## Installation

### Automatic Setup (Recommended)

1. Make the setup script executable:
   ```bash
   chmod +x setup.sh
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

### Manual Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Activate the virtual environment (if not already active):
   ```bash
   source venv/bin/activate
   ```

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```

## Usage

1. **Upload Excel File**: Click on the upload area and select your Excel file
2. **View Results**: The application will display:
   - Total number of schools processed
   - Schools located within Killa Saifullah district
   - Schools located outside the district boundaries
3. **Navigate to Locations**: Click the "Navigate" button next to any school to open Google Maps
4. **View Interactive Map**: Click "View Interactive Map" to see all schools plotted on a map
5. **Download Results**: Use the download buttons to save filtered results as CSV files

## District Boundaries

The application uses approximate coordinates for Killa Saifullah district boundaries:
- North-West: (30.8500, 68.7500)
- North-East: (30.8500, 69.2000)
- South-East: (30.4500, 69.2000)
- South-West: (30.4500, 68.7500)

**Note**: These are approximate boundaries. For precise verification, use the navigation buttons to check actual locations.

## File Structure

```
PMC/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
├── README.md             # This file
├── templates/            # HTML templates
│   ├── index.html        # Upload page
│   └── results.html      # Results page
├── static/               # Static files (CSS downloads)
├── uploads/              # Uploaded Excel files
└── killa_saifullah_gps.xlsx  # Your original data file
```

## Features Explained

### 1. Location Verification
The application uses the Shapely library to create a polygon representing Killa Saifullah district and checks if each school's coordinates fall within this boundary.

### 2. Interactive Map
Built with Folium, the map shows:
- Green markers: Schools within the district
- Red markers: Schools outside the district
- Red boundary: District boundaries
- Clickable markers with school information

### 3. Navigation Integration
Each school has a direct link to Google Maps with the exact coordinates, allowing you to:
- Get directions to the school
- Verify the actual location
- Use Street View for visual confirmation

### 4. Data Processing
The application:
- Automatically detects column names (flexible naming)
- Cleans and validates coordinate data
- Handles missing or invalid data gracefully
- Exports results in CSV format

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed in the virtual environment
2. **File Upload Errors**: Ensure your Excel file has the required columns
3. **Coordinate Issues**: Check that latitude/longitude values are numeric and valid
4. **Map Not Loading**: Check your internet connection (maps require online access)

### Error Messages

- **"Missing required columns"**: Your Excel file doesn't have the expected column names
- **"Invalid file type"**: Only .xlsx and .xls files are supported
- **"Error processing file"**: Check your Excel file for formatting issues

## Customization

### Adjusting District Boundaries
To modify the district boundaries, edit the `KILLA_SAIFULLAH_BOUNDARIES` list in `app.py`:

```python
KILLA_SAIFULLAH_BOUNDARIES = [
    (30.8500, 68.7500),  # North-West
    (30.8500, 69.2000),  # North-East
    (30.4500, 69.2000),  # South-East
    (30.4500, 68.7500),  # South-West
    (30.8500, 68.7500)   # Close the polygon
]
```

### Styling
The application uses Bootstrap 5 for styling. You can customize the appearance by modifying the CSS in the HTML templates.

## Dependencies

- **Flask**: Web framework
- **Pandas**: Data processing
- **NumPy**: Numerical operations
- **OpenPyXL**: Excel file reading
- **Shapely**: Geometric operations
- **Folium**: Interactive maps
- **Werkzeug**: WSGI utilities

## License

This project is open source and available under the MIT License.
