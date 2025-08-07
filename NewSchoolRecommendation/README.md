# School Feasibility Analysis System

A comprehensive Flask-based web application for the Government of Balochistan to analyze the feasibility of establishing new schools at proposed coordinates by checking proximity to existing schools.

## 🏛️ Overview

The School Feasibility Analysis System enables government officials and planners to:
- Upload existing school data (CSV/Excel format)
- Input proposed coordinates for new school locations
- Analyze feasibility based on configurable distance requirements
- Visualize results on interactive maps
- Generate comprehensive reports for decision-making

## ✨ Key Features

### 📊 Data Management
- **CSV/Excel Upload**: Support for existing school data with validation
- **Data Cleaning**: Automatic handling of missing coordinates and invalid data
- **Flexible Schema**: Adaptable to various data formats

### 📍 Coordinate Analysis
- **Batch Processing**: Analyze multiple proposed locations simultaneously
- **Level-specific Analysis**: Different requirements for Primary, Middle, High, and Higher Secondary schools
- **Proximity Checking**: Distance-based feasibility calculations using geodesic measurements

### 🗺️ Interactive Visualization
- **Folium Maps**: Interactive maps with color-coded markers
- **Multi-layer Display**: Existing schools vs. proposed locations
- **Feasibility Indicators**: Visual representation of analysis results

### 📈 Reporting & Analytics
- **Summary Statistics**: Comprehensive overview of analysis results
- **Detailed Reports**: Site-by-site breakdown with recommendations
- **CSV Export**: Downloadable reports for further analysis

## 🛠️ Technical Stack

- **Backend**: Flask (Python 3.8+)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Maps**: Folium with Leaflet.js
- **Data Processing**: Pandas, NumPy
- **Distance Calculations**: Geopy
- **File Handling**: CSV, Excel (openpyxl)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation

1. **Clone or download the project:**
   ```bash
   cd /path/to/your/workspace
   # Project files should be in NewSchoolRecommendation folder
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create required directories:**
   ```bash
   mkdir -p uploads reports static/css templates
   ```

## 🏃‍♂️ Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Application will be available at the local address.**

## 📖 Usage Guide

### Step 1: Upload School Data
1. Navigate to the home page
2. Upload a CSV or Excel file containing existing school data
3. Required columns:
   - `BemisCode`: Unique school identifier
   - `SchoolName`: Name of the school
   - `District`, `Tehsil`, `SubTehsil`, `UC`, `VillageName`: Location details
   - `Gender`: School gender type
   - `SchoolLevel`: Primary/Middle/High/Higher Secondary
   - `FunctionalStatus`: Operational status
   - `_xCord`, `_yCord`: Longitude and Latitude coordinates

### Step 2: Input Proposed Coordinates
1. After successful upload, proceed to coordinate input
2. Add proposed school locations with:
   - Site name
   - Latitude and Longitude coordinates
   - District selection
3. Configure analysis parameters:
   - Minimum distance requirements for each school level
   - Maximum search radius

### Step 3: Analyze Results
1. Submit coordinates for analysis
2. View comprehensive results including:
   - Summary statistics
   - Interactive map visualization
   - Detailed site-by-site analysis
   - Feasibility recommendations

### Step 4: Download Reports
1. Export analysis results as CSV
2. Share reports with stakeholders
3. Use data for planning decisions

## ⚙️ Configuration

### Distance Parameters
The system uses configurable minimum distances for different school levels:

- **Primary Schools**: Default 1.0 km
- **Middle Schools**: Default 2.0 km
- **High Schools**: Default 3.0 km
- **Higher Secondary Schools**: Default 5.0 km

### Search Settings
- **Maximum Search Radius**: Default 10.0 km (configurable)

## 📁 Project Structure

```
NewSchoolRecommendation/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .github/
│   └── copilot-instructions.md     # Development guidelines
├── templates/
│   ├── index.html                  # File upload page
│   ├── coordinate_input.html       # Coordinate input form
│   └── results.html                # Analysis results display
├── static/
│   └── css/
│       └── enhanced-styles.css     # Custom styling
├── uploads/                        # Uploaded files storage
└── reports/                        # Generated reports storage
```

## 🔒 Security Features

- **File Validation**: Secure file upload with type checking
- **Input Sanitization**: Protection against malicious input
- **Size Limits**: Maximum file size restrictions (50MB)
- **Path Security**: Secure filename handling

## 🎨 User Interface

- **Government-style Design**: Professional, clean interface
- **Responsive Layout**: Mobile-friendly design
- **Accessibility**: WCAG compliant features
- **Interactive Elements**: Smooth animations and transitions

## 🚨 Error Handling

- **Comprehensive Validation**: Data format and coordinate validation
- **User-friendly Messages**: Clear error descriptions
- **Graceful Degradation**: Fallback options for edge cases
- **Logging**: Detailed error logging for debugging

## 📊 Analysis Methodology

### Feasibility Calculation
The system determines feasibility based on:
1. **Distance Requirements**: Minimum distances from existing schools of each level
2. **Proximity Analysis**: Geodesic distance calculations
3. **Scoring System**: Weighted feasibility scores (0-100)
4. **Recommendations**: Automated suggestions based on analysis

### Map Visualization
- **Color Coding**: 
  - 🟢 Green: Feasible locations
  - 🔴 Red: Not feasible locations
  - 🔵 Blue: Existing schools
- **Interactive Features**: Clickable markers with detailed information
- **Zoom Controls**: Multiple zoom levels for detailed inspection

## 🧪 Testing

The application includes comprehensive testing capabilities:
- Data validation testing
- Coordinate analysis testing
- Map generation testing
- Report generation testing

## 🤝 Contributing

This project follows Government of Balochistan development standards:
- Clean, readable code with comprehensive comments
- PEP 8 Python style guidelines
- Responsive, accessible UI design
- Comprehensive error handling

## 📞 Support

For technical support or questions:
- Review the error messages and logs
- Check the requirements and installation steps
- Ensure all dependencies are properly installed
- Verify data format requirements

## 📄 License

Developed for the Government of Balochistan under official government guidelines.

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - File upload and validation
  - Coordinate analysis
  - Interactive mapping
  - Report generation

## 🎯 Future Enhancements

Planned features for future releases:
- Batch coordinate upload via CSV
- Advanced filtering and search capabilities
- Historical analysis tracking
- API endpoints for integration
- Multi-language support
- Advanced analytics dashboard
- GIS integration
- Demographic analysis integration

---

**Government of Balochistan - School Feasibility Analysis System**  
*Empowering data-driven educational infrastructure planning*
