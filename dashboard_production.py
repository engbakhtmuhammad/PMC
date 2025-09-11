"""
PMC School Management Systems - Unified Dashboard (Smart Version)
A comprehensive dashboard that works locally and in production
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pmc_dashboard_secret_key_2025'

# Add system paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'BEFComparisonSystem'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'SchoolUpgradeSystem'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'SchoolFeasibilitySystem'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'SchoolProgressionSystem'))

# Try to import the actual systems
try:
    # Import BEF Comparison System
    from BEFComparisonSystem import app as bef_app
    bef_available = True
except Exception as e:
    print(f"BEF System not available: {e}")
    bef_available = False

try:
    # Import School Upgrade System
    from SchoolUpgradeSystem import app as upgrade_app
    upgrade_available = True
except Exception as e:
    print(f"School Upgrade System not available: {e}")
    upgrade_available = False

# System configurations
SYSTEMS = {
    'bef_comparison': {
        'name': 'BEF vs Government Schools Comparison',
        'description': 'Compare BEF and Government schools with GIS mapping and distance analysis',
        'icon': '🏫',
        'features': ['GIS Mapping', 'Distance Analysis', 'Excel Upload', 'Statistical Comparison'],
        'url': '/bef_system',
        'available': bef_available,
        'status': 'available' if bef_available else 'demo'
    },
    'school_upgrade': {
        'name': 'School Upgrade Configurator', 
        'description': 'AI-powered school infrastructure upgrade recommendations',
        'icon': '⬆️',
        'features': ['AI Recommendations', 'Census Integration', 'Priority Scoring', 'Resource Planning'],
        'url': '/upgrade_system',
        'available': upgrade_available,
        'status': 'available' if upgrade_available else 'demo'
    },
    'school_feasibility': {
        'name': 'School Feasibility Analyzer',
        'description': 'Analyze feasibility for new school locations',
        'icon': '📊', 
        'features': ['Location Analysis', 'Demographic Study', 'Cost Estimation', 'Risk Assessment'],
        'url': '/feasibility_system',
        'available': False,  # Not implemented yet
        'status': 'demo'
    },
    'school_progression': {
        'name': 'School Progression Tracker',
        'description': 'Track and monitor school development progress',
        'icon': '📈',
        'features': ['Progress Monitoring', 'Timeline Tracking', 'Milestone Management', 'Reporting'],
        'url': '/progression_system',
        'available': False,  # Not implemented yet
        'status': 'demo'
    }
}

@app.route('/')
def dashboard():
    """Main dashboard page"""
    stats = {
        'total_systems': len(SYSTEMS),
        'active_systems': len([s for s in SYSTEMS.values() if s['status'] == 'available']),
        'total_features': sum(len(s['features']) for s in SYSTEMS.values()),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    return render_template('dashboard_production.html', systems=SYSTEMS, stats=stats)

@app.route('/api/stats')
def api_stats():
    """API endpoint for system statistics"""
    return jsonify({
        'total_systems': len(SYSTEMS),
        'active_systems': len([s for s in SYSTEMS.values() if s['status'] == 'available']),
        'total_features': sum(len(s['features']) for s in SYSTEMS.values()),
        'last_updated': datetime.now().isoformat(),
        'systems': {k: v['status'] for k, v in SYSTEMS.items()}
    })

@app.route('/system/<system_id>')
def system_info(system_id):
    """Get detailed information about a specific system"""
    if system_id not in SYSTEMS:
        return jsonify({'error': 'System not found'}), 404
    
    system = SYSTEMS[system_id].copy()
    system['id'] = system_id
    return jsonify(system)

# Routes for actual systems
@app.route('/bef_system')
@app.route('/bef_system/')
@app.route('/bef_system/<path:path>')
def bef_system(path=''):
    """BEF Comparison System Integration"""
    if not SYSTEMS['bef_comparison']['available']:
        return render_template('system_demo.html', 
                             system=SYSTEMS['bef_comparison'],
                             system_id='bef_comparison')
    
    # Import and run the actual BEF system
    import subprocess
    import threading
    import time
    
    # Check if BEF system is running
    try:
        import requests
        response = requests.get('http://localhost:5041', timeout=2)
        if response.status_code == 200:
            return redirect('http://localhost:5041')
    except:
        pass
    
    # Start BEF system
    def start_bef():
        os.chdir(os.path.join(os.path.dirname(__file__), 'BEFComparisonSystem'))
        subprocess.run(['python3', 'app.py'])
    
    threading.Thread(target=start_bef, daemon=True).start()
    time.sleep(3)  # Wait for startup
    return redirect('http://localhost:5041')

@app.route('/upgrade_system')
@app.route('/upgrade_system/')  
@app.route('/upgrade_system/<path:path>')
def upgrade_system(path=''):
    """School Upgrade System Integration"""
    if not SYSTEMS['school_upgrade']['available']:
        return render_template('system_demo.html',
                             system=SYSTEMS['school_upgrade'],
                             system_id='school_upgrade')
    
    # Import and run the actual upgrade system
    import subprocess
    import threading
    import time
    
    # Check if Upgrade system is running
    try:
        import requests
        response = requests.get('http://localhost:5042', timeout=2)
        if response.status_code == 200:
            return redirect('http://localhost:5042')
    except:
        pass
    
    # Start Upgrade system
    def start_upgrade():
        os.chdir(os.path.join(os.path.dirname(__file__), 'SchoolUpgradeSystem'))
        subprocess.run(['python3', 'app.py'])
    
    threading.Thread(target=start_upgrade, daemon=True).start()
    time.sleep(3)  # Wait for startup
    return redirect('http://localhost:5042')

@app.route('/feasibility_system')
def feasibility_system():
    """School Feasibility System (Demo)"""
    return render_template('system_demo.html',
                         system=SYSTEMS['school_feasibility'],
                         system_id='school_feasibility')

@app.route('/progression_system')
def progression_system():
    """School Progression System (Demo)"""
    return render_template('system_demo.html',
                         system=SYSTEMS['school_progression'],
                         system_id='school_progression')

@app.route('/progression_demo')
def progression_demo():
    return render_template('system_demo.html',
                         system=SYSTEMS['school_progression'],
                         system_id='school_progression')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5040))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🏛️  PMC School Management Systems Dashboard")
    print(f"============================================================")
    print(f"📊 Dashboard starting on port {port}...")
    print(f"🌐 Environment: {'Development' if debug else 'Production'}")
    print(f"============================================================")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
