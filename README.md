# 🏛️ PMC School Management Systems - Unified Dashboard

## 📋 Overview
A comprehensive dashboard for managing all Balochistan Education Foundation school management systems from a single interface.

## 🏫 Included Systems

### 1. **BEF vs Government Schools Comparison** 🏫
- **Port**: 5041
- **Features**: GIS Mapping, Distance Analysis, Excel Upload, Statistical Comparison
- **Description**: Compare BEF and Government schools with interactive maps and analysis

### 2. **School Upgrade Configurator** ⬆️
- **Port**: 5042  
- **Features**: AI Recommendations, Census Integration, Priority Scoring, Resource Planning
- **Description**: AI-powered school infrastructure upgrade recommendations

### 3. **School Feasibility Analyzer** 📊
- **Port**: 5043
- **Features**: Location Analysis, Demographic Study, Cost Estimation, Risk Assessment
- **Description**: Analyze feasibility for new school locations

### 4. **School Progression Tracker** 📈
- **Port**: 5044
- **Features**: Progress Tracking, Milestone Management, Performance Analytics, Report Generation
- **Description**: Track and manage school development progression

## 🚀 Deployment Options

### Option 1: Fly.io (Recommended)
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly auth signup
fly launch --config fly.toml
fly deploy
```

### Option 2: Local Development
```bash
python dashboard_app.py
# Access at: http://localhost:5040
```

## 🔧 Features

- **🎛️ System Management**: Start/Stop individual systems
- **📊 Real-time Status**: Live monitoring of all systems
- **🔄 Auto-refresh**: Dashboard updates every 30 seconds
- **📱 Responsive Design**: Works on desktop and mobile
- **🌐 Direct Access**: Quick links to running systems
- **📈 Statistics**: Overview of system status and health

## 📁 File Structure
```
PMC/
├── dashboard_app.py           # Main dashboard application
├── wsgi.py                   # WSGI entry point
├── fly.toml                  # Fly.io configuration
├── Procfile                  # Process definition
├── requirements.txt          # Python dependencies
├── templates/
│   ├── dashboard.html        # Main dashboard interface
│   └── system_details.html   # Individual system details
├── BEFComparisonSystem/      # BEF comparison system
├── SchoolUpgradeSystem/      # School upgrade system
├── SchoolFeasibilitySystem/  # Feasibility analysis system
└── SchoolProgressionSystem/  # Progression tracking system
```

## 🌐 Access URLs (After Deployment)

- **Dashboard**: `https://pmc-school-dashboard.fly.dev`
- **Individual Systems**: Accessible through dashboard or direct ports

## 🔒 Security Notes

- Systems run on different ports for isolation
- Dashboard manages system lifecycle
- All systems are containerized and secure

## 📞 Support

For technical support or feature requests, contact the PMC development team.

---

**Built with ❤️ for Balochistan Education Foundation**
