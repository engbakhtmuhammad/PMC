# 🏫 Balochistan School Feasibility Analysis System

An elegant, comprehensive web application for analyzing the feasibility of new school locations in Balochistan Province, Pakistan. This system helps education planners determine optimal locations for new schools by analyzing proximity to existing educational institutions.

![System Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-red)
![License](https://img.shields.io/badge/License-Government%20Use-yellow)

## 🎯 Key Features

### 📊 **Smart Feasibility Analysis**
- **Level-based Analysis**: Analyzes feasibility based on school level (Primary, Middle, High, Higher Secondary)
- **Distance Calculations**: Uses precise geodesic distance calculations
- **Configurable Thresholds**: Customizable minimum distance requirements
- **Multi-location Support**: Analyze multiple proposed sites simultaneously

### 🗺️ **Interactive Visualization**
- **Dynamic Maps**: Real-time map generation with Folium integration
- **Color-coded Markers**: Visual distinction between feasible and non-feasible locations
- **Detailed Popups**: Comprehensive information for each location
- **Legend Support**: Clear understanding of map symbols

### 📈 **Comprehensive Reporting**
- **Statistical Summaries**: Detailed analysis statistics
- **Export Capabilities**: Download results as CSV reports
- **Visual Analytics**: Charts and graphs for data insights
- **Print-friendly**: Optimized layouts for document generation

### 🎨 **Modern UI/UX**
- **Government Branding**: Official Balochistan government styling
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Accessibility**: WCAG compliant design elements
- **Progressive Enhancement**: Works with and without JavaScript

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser
- Internet connection (for map tiles)

### Installation & Running

1. **Clone or Download the System**
   ```bash
   cd SchoolFeasibilitySystem
   ```

2. **Start the Server**
   ```bash
   ./start_feasibility_server.sh
   ```
   
   Or manually:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

3. **Access the Application**
   - Open your browser to: `http://localhost:5011`
   - Health check: `http://localhost:5011/health`

## 📋 System Workflow

### Step 1: Data Upload
- Upload CSV file with existing school data
- System validates required columns automatically
- Supports Excel (.xlsx) files as well
- Real-time validation feedback

**Required Columns:**
- `BemisCode`, `SchoolName`, `District`, `Tehsil`, `SubTehsil`
- `UC`, `VillageName`, `Gender`, `SchoolLevel`, `FunctionalStatus`
- `ReasonOfNonFunctional`, `Building`, `BuildingStructure`
- `BuildingCondition`, `SpaceForNewRooms`, `BoundaryWall`
- `BoundaryWallStructure`, `BoundaryWallCondition`
- `ElectricityInSchool`, `TotalStudentProfileEntered`
- `Source`, `_xCord`, `_yCord`

### Step 2: Configuration
- Select proposed school level
- Set minimum distance threshold
- Add multiple proposed coordinates
- Specify location names (optional)

### Step 3: Analysis & Results
- Automated feasibility analysis
- Interactive map visualization
- Detailed results table
- Statistical summary
- Download comprehensive report

## 🔧 System Configuration

### School Level Hierarchy
- **Primary**: Entry-level education
- **Middle**: Intermediate education
- **High**: Secondary education  
- **Higher Secondary**: Pre-university education

### Default Distance Thresholds
- **Primary Schools**: 2.0 km minimum
- **Middle Schools**: 5.0 km minimum
- **High Schools**: 10.0 km minimum
- **Higher Secondary**: 15.0 km minimum

### File Upload Limits
- Maximum file size: 50MB
- Supported formats: CSV, Excel (.xlsx)
- UTF-8 encoding recommended

## 🎨 Design System

### Color Palette
- **Primary**: `#2563eb` (Blue)
- **Secondary**: `#0891b2` (Cyan)
- **Success**: `#059669` (Green)
- **Warning**: `#d97706` (Orange)
- **Danger**: `#dc2626` (Red)
- **Info**: `#0284c7` (Light Blue)

### Typography
- **Font Family**: Poppins (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800
- **Responsive**: Fluid typography scaling

### Components
- **Cards**: Glass morphism with backdrop blur
- **Buttons**: 3D elevation with hover animations
- **Forms**: Floating labels with validation states
- **Maps**: Bordered containers with legends

## 📊 Technical Architecture

### Backend Stack
- **Framework**: Flask 2.3+
- **Data Processing**: Pandas, NumPy
- **Geospatial**: GeoPy, Folium
- **File Handling**: OpenPyXL for Excel support

### Frontend Stack
- **CSS Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.4
- **Animations**: AOS (Animate On Scroll)
- **Maps**: Leaflet.js with OpenStreetMap

### Data Flow
1. **Upload**: CSV/Excel → Pandas DataFrame
2. **Validation**: Column checking → Error reporting
3. **Analysis**: Coordinate processing → Distance calculations
4. **Visualization**: Folium map generation → HTML output
5. **Export**: Results compilation → CSV download

## 🔒 Security Features

- **Input Validation**: Comprehensive form validation
- **File Security**: Secure filename handling
- **Session Management**: Temporary data storage
- **Error Handling**: Graceful error recovery
- **SQL Injection Prevention**: Parameterized queries (when applicable)

## 📱 Browser Compatibility

### Supported Browsers
- **Chrome**: 90+ (Recommended)
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

### Mobile Support
- **iOS Safari**: 14+
- **Chrome Mobile**: 90+
- **Samsung Internet**: 14+

## 🛠️ Development & Customization

### Environment Setup
```bash
# Development mode
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Custom Styling
- Edit `static/css/elegant-enhancements.css`
- Modify CSS variables for color scheme changes
- Update template files in `templates/` directory

### API Extensions
- Add custom routes in `app.py`
- Extend analysis algorithms in analyzer classes
- Implement additional export formats

## 📈 Performance Optimization

### File Processing
- Chunked CSV reading for large files
- Efficient DataFrame operations
- Memory-conscious data handling

### Map Rendering
- Optimized marker clustering
- Lazy loading for large datasets
- Responsive map sizing

### Caching Strategy
- Session-based result storage
- Browser caching for static assets
- Optimized image delivery

## 🧪 Testing

### Manual Testing Checklist
- [ ] File upload with valid/invalid data
- [ ] Coordinate input validation
- [ ] Analysis accuracy verification
- [ ] Map rendering on different screen sizes
- [ ] Download functionality
- [ ] Error handling scenarios

### Sample Data
- Use provided sample CSV files
- Test with various school level combinations
- Verify distance calculations manually

## 🆘 Troubleshooting

### Common Issues

**File Upload Fails**
- Check file size (< 50MB)
- Verify CSV format and encoding
- Ensure all required columns are present

**Map Not Loading**
- Check internet connection
- Verify coordinate validity
- Clear browser cache

**Analysis Errors**
- Validate coordinate format (decimal degrees)
- Check for missing data in uploaded file
- Ensure proper school level selection

### Debug Mode
```bash
export FLASK_DEBUG=1
python app.py
```

## 📞 Support & Contact

### Government Support
- **Department**: Education Department, Government of Balochistan
- **Technical Support**: Available during business hours
- **Documentation**: This README and inline help

### System Maintenance
- Regular updates for security patches
- Data backup recommendations
- Performance monitoring guidelines

## 📄 License & Usage

This software is developed for the **Government of Balochistan** for official educational planning purposes. Unauthorized distribution or commercial use is prohibited.

### Usage Rights
- ✅ Government educational planning
- ✅ Academic research (with permission)
- ✅ Non-commercial analysis
- ❌ Commercial redistribution
- ❌ Unauthorized modifications

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with full feasibility analysis
- Elegant UI matching SchoolUpgradeSystem design
- Complete map integration
- CSV/Excel upload support
- Multi-coordinate analysis
- Download functionality

### Future Enhancements
- [ ] Database integration
- [ ] User authentication system
- [ ] Advanced analytics dashboard
- [ ] GIS data integration
- [ ] Mobile app development

---

**© 2025 Government of Balochistan | Education Department**

*Built with ❤️ for better education planning in Balochistan*
