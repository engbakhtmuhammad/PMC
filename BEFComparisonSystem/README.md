# BEF-Government Schools Comparison System

A comprehensive web-based system for analyzing the geographic distribution and proximity relationships between Balochistan Education Foundation (BEF) schools and Government schools.

## Features

### 🎯 Core Functionality
- **Dual Dataset Upload**: Support for both Government and BEF school datasets
- **Interactive Mapping**: Folium-powered maps with distinct markers for different school types
- **Proximity Analysis**: Calculate distances between BEF and Government schools
- **District-wise Analysis**: Detailed breakdown by administrative districts
- **Statistical Insights**: Comprehensive metrics and coverage analysis
- **Export Capabilities**: Download results as CSV for further analysis

### 📊 Analysis Types
- **Proximity Analysis**: Distance-based relationships between schools
- **Distribution Analysis**: Geographic spread and density patterns
- **Comprehensive Analysis**: Combined proximity and distribution insights

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with gradient themes
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Interactive Elements**: Drag-and-drop file uploads, real-time progress tracking
- **Elegant Animations**: Smooth transitions and loading states

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start
1. **Clone or Download** the system files
2. **Navigate** to the BEFComparisonSystem directory
3. **Run** the startup script:
   ```bash
   ./run.sh
   ```

The script will automatically:
- Create a virtual environment
- Install all required dependencies
- Set up necessary directories
- Start the Flask application

### Manual Installation
If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads downloads static/css templates

# Start the application
python app.py
```

## Usage Guide

### 1. Data Upload
- **Government Schools**: Upload CSV/Excel file containing government school data
- **BEF Schools**: Upload CSV/Excel file containing BEF school data
- **Required Columns**: Ensure your data includes latitude, longitude, and district information

### 2. Configure Analysis
- **Select Districts**: Choose which districts to include in the analysis
- **Set Distance Threshold**: Define maximum distance for proximity calculations
- **Choose Analysis Type**: Select from proximity, distribution, or comprehensive analysis
- **Output Options**: Configure what to include in results (map, statistics, CSV export)

### 3. View Results
- **Interactive Map**: Explore school locations with click-for-details functionality
- **Statistical Dashboard**: View key metrics and insights
- **District Analysis**: Detailed breakdown for each selected district
- **Download Results**: Export comprehensive data for further analysis

## Data Format Requirements

### Expected Columns
Your CSV/Excel files should include:
- **Latitude**: Decimal degrees (e.g., 30.3753)
- **Longitude**: Decimal degrees (e.g., 69.3451)
- **District**: Administrative district name
- **School Name**: Name of the educational institution
- **Additional Info**: Any other relevant school details

### Sample Data Structure
```csv
School Name,District,Latitude,Longitude,Level,Type
ABC Primary School,Quetta,30.1798,66.9750,Primary,Government
XYZ High School,Killa Saifullah,30.7058,68.8658,Secondary,BEF
```

## Technical Architecture

### Backend Components
- **Flask Framework**: Web application server
- **pandas**: Data processing and analysis
- **folium**: Interactive mapping
- **numpy**: Mathematical computations

### Frontend Technologies
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icon library
- **AOS**: Animation library
- **Custom CSS**: Enhanced styling and transitions

### File Structure
```
BEFComparisonSystem/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── run.sh                # Startup script
├── README.md             # This documentation
├── static/
│   └── css/
│       └── style.css     # Enhanced styling
├── templates/
│   ├── index.html        # Upload interface
│   ├── configure.html    # Analysis configuration
│   └── results.html      # Results display
├── uploads/              # Uploaded files storage
└── downloads/            # Generated exports
```

## Configuration Options

### Distance Analysis
- **Range**: 0.5 km to 50 km
- **Default**: 10 km proximity threshold
- **Use Case**: Adjust based on your analysis requirements

### District Selection
- **Multi-select**: Choose specific districts or all districts
- **Search Function**: Quick filtering of district list
- **Real-time Counts**: See school counts per district

### Output Customization
- **Interactive Map**: Toggle map generation
- **Statistical Summary**: Include/exclude detailed statistics
- **CSV Export**: Enable downloadable results

## Performance Considerations

### Optimal Data Sizes
- **Recommended**: Up to 10,000 schools per dataset
- **Maximum File Size**: 50MB per upload
- **Processing Time**: Varies with dataset size and analysis complexity

### Memory Usage
- Large datasets may require more system memory
- Map generation is memory-intensive for 1000+ schools
- Consider district-based analysis for very large datasets

## Troubleshooting

### Common Issues

**Upload Failures**
- Verify CSV/Excel format is correct
- Check for required columns (latitude, longitude, district)
- Ensure file size is under 50MB limit

**Map Not Loading**
- Refresh the page after analysis completion
- Check browser console for JavaScript errors
- Verify coordinate data is valid (decimal degrees)

**Analysis Errors**
- Ensure at least one district is selected
- Verify both datasets are uploaded successfully
- Check for missing or invalid coordinate data

### Error Messages
- **"No valid coordinates found"**: Check latitude/longitude columns
- **"District not found"**: Verify district name consistency
- **"Upload failed"**: Check file format and size

## Support & Documentation

### Getting Help
1. Check this README for common solutions
2. Verify your data format matches requirements
3. Review console logs for detailed error messages
4. Ensure all dependencies are properly installed

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python Version**: 3.8 or higher
- **Browser**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Memory**: 4GB RAM recommended for large datasets

## License & Credits

This system was developed for educational and research purposes. Feel free to modify and adapt for your specific needs.

### Dependencies
- Flask: Web framework
- pandas: Data analysis library
- folium: Interactive mapping
- Bootstrap: UI framework
- Font Awesome: Icons

## Version History

### v1.0.0 (Current)
- Initial release with core functionality
- Dual dataset upload and comparison
- Interactive mapping and analysis
- Export capabilities
- Responsive web interface

---

For additional support or feature requests, please refer to the system documentation or contact your system administrator.
