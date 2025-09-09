"""
PMC School Management Systems - Unified Dashboard (Production Version)
A comprehensive dashboard for all Balochistan school management systems - Cloud Deployment
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pmc_dashboard_secret_key_2025'

# System configurations for display only in production
SYSTEMS = {
    'bef_comparison': {
        'name': 'BEF vs Government Schools Comparison',
        'description': 'Compare BEF and Government schools with GIS mapping and distance analysis',
        'icon': '🏫',
        'features': ['GIS Mapping', 'Distance Analysis', 'Excel Upload', 'Statistical Comparison'],
        'demo_url': '/bef_demo',
        'status': 'available'
    },
    'school_upgrade': {
        'name': 'School Upgrade Configurator', 
        'description': 'AI-powered school infrastructure upgrade recommendations',
        'icon': '⬆️',
        'features': ['AI Recommendations', 'Census Integration', 'Priority Scoring', 'Resource Planning'],
        'demo_url': '/upgrade_demo',
        'status': 'available'
    },
    'school_feasibility': {
        'name': 'School Feasibility Analyzer',
        'description': 'Analyze feasibility for new school locations',
        'icon': '📊', 
        'features': ['Location Analysis', 'Demographic Study', 'Cost Estimation', 'Risk Assessment'],
        'demo_url': '/feasibility_demo',
        'status': 'available'
    },
    'school_progression': {
        'name': 'School Progression Tracker',
        'description': 'Track and monitor school development progress',
        'icon': '📈',
        'features': ['Progress Monitoring', 'Timeline Tracking', 'Milestone Management', 'Reporting'],
        'demo_url': '/progression_demo',
        'status': 'available'
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

# Demo routes for each system (placeholder for actual functionality)
@app.route('/bef_demo')
def bef_demo():
    return render_template('system_demo.html', 
                         system=SYSTEMS['bef_comparison'],
                         system_id='bef_comparison')

@app.route('/upgrade_demo')
def upgrade_demo():
    return render_template('system_demo.html',
                         system=SYSTEMS['school_upgrade'], 
                         system_id='school_upgrade')

@app.route('/feasibility_demo')
def feasibility_demo():
    return render_template('system_demo.html',
                         system=SYSTEMS['school_feasibility'],
                         system_id='school_feasibility')

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
