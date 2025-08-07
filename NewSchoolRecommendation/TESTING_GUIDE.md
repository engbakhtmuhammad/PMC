# Testing Guide - School Feasibility Analysis System

## Overview
This guide provides comprehensive testing instructions for the School Feasibility Analysis System developed for the Government of Balochistan.

## Quick Start Testing

### 1. Start the Application
```bash
cd /Users/macbookpro/Desktop/PMC/NewSchoolRecommendation
python3 app.py
```

The application will start on: http://127.0.0.1:5011

### 2. Test Main Functionality

#### A. CSV Upload Testing
1. Navigate to the home page (http://127.0.0.1:5011)
2. Upload the provided sample file: `sample_schools_data.csv`
3. Verify the upload is successful and data is processed
4. Check that the coordinate input page loads correctly

#### B. Coordinate Input Testing
1. Use these test coordinates for Balochistan region:
   - **Feasible Location**: Latitude: 30.1838, Longitude: 67.0011 (near existing schools)
   - **Non-feasible Location**: Latitude: 30.5000, Longitude: 67.5000 (isolated area)
   - **Edge Case**: Latitude: 30.0000, Longitude: 66.5000 (boundary testing)

2. Test multiple coordinates at once:
   ```
   Coordinate Set 1: 30.1838, 67.0011
   Coordinate Set 2: 30.2500, 67.1000
   Coordinate Set 3: 30.3000, 67.2000
   ```

#### C. Analysis Results Testing
1. Submit coordinates and verify results page loads
2. Check that the interactive map displays correctly with:
   - Existing schools (blue markers)
   - Proposed locations (red/green markers based on feasibility)
   - Radius circles around existing schools
3. Verify feasibility recommendations are logical
4. Test map download functionality
5. Test CSV report download

## Test Data Files

### Primary Test File
- **File**: `sample_schools_data.csv`
- **Records**: 20 schools across different districts in Balochistan
- **Coverage**: Quetta, Pishin, Killa Abdullah, Chaman, Ziarat, Mastung, Kalat, Khuzdar, Lasbela, Gwadar, Turbat, Sibi

### Expected Data Format
```csv
BemisCode,SchoolName,District,Tehsil,SubTehsil,UC,VillageName,Gender,SchoolLevel,FunctionalStatus,Building,BuildingCondition,ElectricityInSchool,TotalStudentProfileEntered,_xCord,_yCord
```

## Test Scenarios

### Scenario 1: Normal Operation
1. Upload valid CSV file
2. Input valid coordinates within Balochistan
3. Verify analysis results and recommendations
4. Download reports successfully

### Scenario 2: Edge Cases
1. Upload CSV with missing coordinates
2. Input coordinates outside Balochistan
3. Input invalid coordinate formats
4. Test with empty coordinate fields

### Scenario 3: File Upload Validation
1. Upload non-CSV files
2. Upload CSV files with wrong column headers
3. Upload empty CSV files
4. Upload very large CSV files

### Scenario 4: Performance Testing
1. Upload CSV with 100+ schools
2. Input 10+ coordinate pairs simultaneously
3. Generate large maps with many markers
4. Test multiple concurrent users (if applicable)

## Expected Results

### Feasibility Analysis
- **High Feasibility**: Coordinates >2km from existing schools
- **Medium Feasibility**: Coordinates 1-2km from existing schools  
- **Low Feasibility**: Coordinates <1km from existing schools

### Map Features
- Interactive zoom and pan
- Clear marker differentiation
- Accurate distance calculations
- Professional styling consistent with government standards

### Reports
- Detailed feasibility scores
- Distance calculations to nearest schools
- Recommendations for school placement
- Export capabilities (CSV, Map image)

## Troubleshooting

### Common Issues
1. **Port Already in Use**: Change port in app.py or kill existing processes
2. **Missing Dependencies**: Run `pip3 install -r requirements.txt`
3. **Upload Errors**: Check file format and column headers
4. **Map Not Loading**: Check internet connection for map tiles

### Log Locations
- Flask logs: Console output
- Upload logs: Check `uploads/` directory
- Error logs: Check console for stack traces

## Performance Benchmarks
- CSV Upload: <5 seconds for files up to 10MB
- Coordinate Analysis: <3 seconds for up to 10 coordinates
- Map Generation: <5 seconds for up to 100 markers
- Report Generation: <2 seconds for standard reports

## Browser Compatibility
- Chrome 90+ (Recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

## Mobile Testing
- Test responsive design on mobile devices
- Verify touch interactions on maps
- Check file upload functionality on mobile

## API Testing (if applicable)
Use tools like Postman or curl to test API endpoints:

```bash
# Test coordinate analysis endpoint
curl -X POST http://127.0.0.1:5011/analyze \
  -H "Content-Type: application/json" \
  -d '{"coordinates": [{"lat": 30.1838, "lon": 67.0011}]}'
```

## Security Testing
1. Test file upload security (malicious files)
2. Verify input validation for coordinates
3. Check for SQL injection vulnerabilities (if database used)
4. Test CSRF protection

## Accessibility Testing
1. Test keyboard navigation
2. Verify screen reader compatibility
3. Check color contrast ratios
4. Test with accessibility tools

---

For additional support or questions, refer to the main README.md file or contact the development team.
