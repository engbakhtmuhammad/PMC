# BEF Comparison System - Data Upload Guide

## Current Issue Resolution

### The Problem:
Your files have **swapped coordinate columns**:

**BEF Schools File** (`BEFSchoolsCoordinates.csv`):
- `_xCord` column contains **latitude** values (26.26...)
- `_yCord` column contains **longitude** values (64.67...)

**Government Schools File** (`balochistan_census.csv`):
- `_xCord` column contains **longitude** values (67.77...)
- `_yCord` column contains **latitude** values (30.42...)

### The Solution Applied:

✅ **Smart Coordinate Detection**: Updated the system to analyze actual coordinate values, not just column names
✅ **Value-Based Detection**: System now checks if values fall in Pakistan's coordinate ranges:
  - **Latitude**: 24°N to 37°N
  - **Longitude**: 61°E to 75°E
✅ **Better Error Messages**: Clear feedback about what went wrong and what columns are available

## Testing Your Data Upload:

### Step 1: Upload Your Files
1. Go to http://127.0.0.1:5000
2. Upload your `balochistan_census.csv` as **Government Schools**
3. Upload your `BEFSchoolsCoordinates.csv` as **BEF Schools**
4. Click **"Process Files and Continue"**

### Step 2: Check the Console Output
The terminal will now show detailed analysis:

```
=== ANALYZING GOVERNMENT SCHOOLS FILE ===
Available columns: ['BemisCode', 'SessionId', 'SchoolName', 'District', ...]
Coordinate candidates: [('_xCord', 155), ('_yCord', 156)]
Column _xCord: average value = 67.77 (longitude detected)
Column _yCord: average value = 30.42 (latitude detected)
Detected longitude column: _xCord
Detected latitude column: _yCord
Final detected columns: {'name': 'SchoolName', 'district': 'District', 'latitude': '_yCord', 'longitude': '_xCord'}

=== ANALYZING BEF SCHOOLS FILE ===
Available columns: ['S.no', 'BemisCode', 'District', 'Tehsil', 'UC', 'SchoolName', '_xCord', '_yCord']
Coordinate candidates: [('_xCord', 7), ('_yCord', 8)]
Column _xCord: average value = 26.26 (latitude detected)
Column _yCord: average value = 64.67 (longitude detected)
Detected latitude column: _xCord
Detected longitude column: _yCord
Final detected columns: {'name': 'SchoolName', 'district': 'District', 'latitude': '_xCord', 'longitude': '_yCord'}

=== CLEANING GOVERNMENT SCHOOLS COORDINATES ===
Cleaned 15270 out of 15270 records
=== CLEANING BEF SCHOOLS COORDINATES ===
Cleaned 690 out of 690 records
```

### Step 3: Expected Success Message
You should see: **"Successfully loaded 15270 government schools and 690 BEF schools"**

## Troubleshooting:

### If You Still See "No Valid Data" Error:

1. **Check Coordinate Ranges**: 
   - Your coordinates should be in decimal degrees
   - Pakistan bounds: 20°N-40°N, 58°E-80°E (we use flexible bounds)

2. **Check Column Names**:
   - School names: Must contain "name", "school", or similar
   - Districts: Must contain "district", "tehsil", or similar
   - Coordinates: Must contain "cord", "lat", "lon", "x", "y", or similar

3. **Check Data Format**:
   - Coordinates must be numbers (not text like "Yes"/"No")
   - No empty cells in coordinate columns
   - Decimal format (not degrees/minutes/seconds)

### Common Issues and Solutions:

❌ **"Could not detect required columns"**
- Solution: Check if your file has columns for school name, district, and coordinates

❌ **"No valid data after cleaning"**
- Solution: Check coordinate values are within Pakistan bounds and are valid numbers

❌ **Page just reloads with no message**
- Solution: Check terminal output for detailed error information

## File Format Examples:

### ✅ Correct Government Schools Format:
```csv
SchoolName,District,_xCord,_yCord
GBMIDS SASSAN MANNA,ZIARAT,67.7759659,30.4279275
```

### ✅ Correct BEF Schools Format:
```csv
SchoolName,District,_xCord,_yCord
Sheer jan Bazaar Haikhan,Awaran,26.2643115,64.6733972
```

## Success Flow:
1. **Upload** → Files are saved and loaded
2. **Column Detection** → System finds name, district, and coordinate columns
3. **Coordinate Validation** → System determines which column is lat vs lon
4. **Data Cleaning** → Invalid coordinates are filtered out
5. **Success** → Redirect to configuration page

## Next Steps After Successful Upload:
- Configure analysis parameters
- Select districts for comparison
- Run the analysis
- View results with interactive maps
- Download CSV reports

---

**Current Status**: ✅ Server running on http://127.0.0.1:5000 with improved coordinate detection
**Expected Result**: Your existing files should now process successfully!
