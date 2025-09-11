# School Upgrade Analysis Tool - User Guide

## 📋 Overview
This tool analyzes the Balochistan census data to identify schools that need to be upgraded from Primary to Middle, Middle to Secondary, Secondary to High, and High to Higher Secondary levels based on proximity and enrollment criteria.

## 🎯 Key Features

### 1. **Smart Upgrade Logic**
- Identifies schools that lack higher-level institutions within a specified radius
- Prioritizes schools with highest enrollment in their area
- Considers geographical proximity to avoid redundant upgrades

### 2. **Multiple Output Formats**
- **Excel File**: Complete upgraded schools data with original structure
- **Interactive Map**: Visual representation of upgrade recommendations
- **Detailed CSV**: Comprehensive analysis with reasoning

### 3. **Flexible Parameters**
- Adjustable search radius (default: 25km)
- Minimum enrollment filters
- District-specific analysis

## 📊 Generated Files

### Main Analysis Files
1. **`upgraded_schools_final.xlsx`** - Primary output with 3 sheets:
   - `Upgraded_Schools`: Schools with upgraded levels
   - `Summary`: Upgrade type breakdown
   - `District_Breakdown`: District-wise statistics

2. **`school_upgrades_visualization.html`** - Interactive map
3. **`upgrade_analysis_detailed.csv`** - Detailed analysis data

### Column Structure (Excel Output)
- `BemisCode` - School identifier
- `SessionId` - Session information
- `SchoolName` - Name of the school
- `District` - District name
- `Tehsil` - Tehsil name
- `Gender` - Boys/Girls/Mixed
- `SchoolLevel` - **UPGRADED LEVEL** (target level)
- `FunctionalStatus` - Functional/Non-Functional
- `ReasonOfNonFunctional` - If applicable
- `StudentEnrollment` - Current enrollment
- `Source` - Data source (EMIS/RTSM)
- `_xCord` - Longitude coordinate
- `_yCord` - Latitude coordinate
- `OriginalLevel` - Current level before upgrade
- `UpgradeReason` - Explanation for upgrade recommendation
- `SearchRadius_km` - Search radius used

## 🚀 How to Use

### Basic Usage
```bash
# Activate virtual environment
source .venv/bin/activate

# Run basic analysis (25km radius)
python enhanced_school_upgrade_tool.py
```

### Advanced Usage with Custom Parameters
```bash
# Custom radius (20km)
python school_upgrade_configurator.py --radius 20

# With minimum enrollment filter (50 students)
python school_upgrade_configurator.py --radius 25 --min-enrollment 50

# Custom output prefix
python school_upgrade_configurator.py --output my_analysis

# Compare different radius values
python school_upgrade_configurator.py --compare
```

## 📈 Analysis Results Summary

### Latest Analysis (25km radius):
- **Total Schools Analyzed**: 1,314 functional schools
- **Schools Recommended for Upgrade**: 56 schools
- **Districts Covered**: PISHIN (34 schools), QUETTA (22 schools)

### Upgrade Breakdown:
- **Middle → Secondary**: 48 schools
- **High → Higher Secondary**: 8 schools

### Top Schools by Enrollment (being upgraded):
1. GBMIDS AHMED KHAN ZAI (Quetta) - 888 students
2. GBMIDS YATE ROAD (Quetta) - 859 students
3. GBMIDS MUSLIM ITEHAD COLONY (Quetta) - 812 students

## 🔧 Technical Details

### Algorithm Logic:
1. **Load Data**: Filter functional schools from census
2. **District Processing**: Analyze each district separately
3. **Proximity Check**: Find schools within specified radius
4. **Enrollment Comparison**: Select highest enrollment schools in areas lacking higher-level institutions
5. **Generate Outputs**: Create Excel, map, and CSV files

### Search Criteria:
- Schools must be functional
- No higher-level school within search radius
- Must have highest or top 80th percentile enrollment among similar schools in area

## 📁 File Organization

```
PMC/
├── balochistan_census.csv                    # Input data
├── enhanced_school_upgrade_tool.py          # Main analysis script
├── school_upgrade_configurator.py           # Parameter configuration tool
├── upgraded_schools_final.xlsx              # Main Excel output
├── school_upgrades_visualization.html       # Interactive map
├── upgrade_analysis_detailed.csv            # Detailed analysis
└── test_analysis_*.* files                  # Test outputs
```

## 🎨 Map Visualization

The interactive map shows:
- **Blue markers**: Primary schools recommended for Middle upgrade
- **Green markers**: Middle schools recommended for Secondary upgrade
- **Orange markers**: Secondary schools recommended for High upgrade
- **Red markers**: High schools recommended for Higher Secondary upgrade

Click on any marker to see:
- School details (name, BEMIS code, district)
- Current and recommended levels
- Student enrollment
- Upgrade reasoning

## 🔄 Comparison Analysis

Use the comparison feature to understand how different radius values affect recommendations:

```bash
python school_upgrade_configurator.py --compare
```

This generates `radius_comparison_analysis.csv` showing upgrade counts for different radius values (15km, 20km, 25km, 30km, 35km).

## 💡 Tips for Best Results

1. **Radius Selection**: 
   - 25km works well for rural areas
   - Consider 15-20km for urban areas
   - Use comparison analysis to find optimal radius

2. **Enrollment Filters**:
   - Use minimum enrollment to focus on viable schools
   - Consider 50+ students for sustainability

3. **District Focus**:
   - Results can be filtered by district in Excel
   - Each district has different upgrade patterns

## 🛠️ Troubleshooting

### Common Issues:
1. **"No schools found"**: Try increasing radius or reducing minimum enrollment
2. **Missing coordinates**: Some schools may lack GPS data
3. **Large file sizes**: Use enrollment filters for focused analysis

### Requirements:
- Python 3.9+
- Required packages: pandas, numpy, folium, geopy, openpyxl

## 📞 Support

For questions or modifications, check:
1. Error messages in terminal output
2. Generated log files
3. Data quality in source CSV file

---

**Last Updated**: July 29, 2025
**Version**: 2.0
**Data Source**: Balochistan Education Census
