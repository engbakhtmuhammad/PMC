"""
PMC School Management Systems - Unified Dashboard
A comprehensive dashboard for all Balochistan school management systems
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import subprocess
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pmc_dashboard_secret_key_2025'

# System configurations
SYSTEMS = {
    'bef_comparison': {
        'name': 'BEF vs Government Schools Comparison',
        'description': 'Compare BEF and Government schools with GIS mapping and distance analysis',
        'port': 5041,
        'path': 'BEFComparisonSystem',
        'icon': '🏫',
        'status': 'stopped',
        'features': ['GIS Mapping', 'Distance Analysis', 'Excel Upload', 'Statistical Comparison']
    },
    'school_upgrade': {
        'name': 'School Upgrade Configurator',
        'description': 'AI-powered school infrastructure upgrade recommendations',
        'port': 5042,
        'path': 'SchoolUpgradeSystem',
        'icon': '⬆️',
        'status': 'stopped',
        'features': ['AI Recommendations', 'Census Integration', 'Priority Scoring', 'Resource Planning']
    },
    'school_feasibility': {
        'name': 'School Feasibility Analyzer',
        'description': 'Analyze feasibility for new school locations',
        'port': 5043,
        'path': 'SchoolFeasibilitySystem',
        'icon': '📊',
        'status': 'stopped',
        'features': ['Location Analysis', 'Demographic Study', 'Cost Estimation', 'Risk Assessment']
    },
    'school_progression': {
        'name': 'School Progression Tracker',
        'description': 'Track and manage school development progression',
        'port': 5044,
        'path': 'SchoolProgressionSystem',
        'icon': '📈',
        'status': 'stopped',
        'features': ['Progress Tracking', 'Milestone Management', 'Performance Analytics', 'Report Generation']
    }
}

# Store running processes
running_processes = {}

@app.route('/')
def dashboard():
    """Main dashboard showing all systems"""
    # Update system statuses
    for system_id in SYSTEMS:
        SYSTEMS[system_id]['status'] = check_system_status(system_id)
    
    stats = {
        'total_systems': len(SYSTEMS),
        'running_systems': sum(1 for s in SYSTEMS.values() if s['status'] == 'running'),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return render_template('dashboard.html', systems=SYSTEMS, stats=stats)

@app.route('/system/<system_id>')
def system_details(system_id):
    """Show details of a specific system"""
    if system_id not in SYSTEMS:
        return "System not found", 404
    
    system = SYSTEMS[system_id]
    system['status'] = check_system_status(system_id)
    
    return render_template('system_details.html', system=system, system_id=system_id)

@app.route('/start_system/<system_id>')
def start_system(system_id):
    """Start a specific system"""
    if system_id not in SYSTEMS:
        return jsonify({'error': 'System not found'}), 404
    
    system = SYSTEMS[system_id]
    
    if system['status'] == 'running':
        return jsonify({'message': f'{system["name"]} is already running'})
    
    try:
        # Start the system
        system_path = os.path.join('/Users/macbookpro/Desktop/PMC', system['path'])
        cmd = f"cd {system_path} && python app.py"
        
        # Start process in background
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        running_processes[system_id] = process
        SYSTEMS[system_id]['status'] = 'running'
        
        return jsonify({
            'message': f'{system["name"]} started successfully',
            'url': f'http://localhost:{system["port"]}',
            'status': 'running'
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to start system: {str(e)}'}), 500

@app.route('/stop_system/<system_id>')
def stop_system(system_id):
    """Stop a specific system"""
    if system_id not in SYSTEMS:
        return jsonify({'error': 'System not found'}), 404
    
    try:
        if system_id in running_processes:
            process = running_processes[system_id]
            process.terminate()
            del running_processes[system_id]
        
        # Also kill by port
        system = SYSTEMS[system_id]
        os.system(f"lsof -ti:{system['port']} | xargs kill -9 2>/dev/null")
        
        SYSTEMS[system_id]['status'] = 'stopped'
        
        return jsonify({
            'message': f'{system["name"]} stopped successfully',
            'status': 'stopped'
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to stop system: {str(e)}'}), 500

@app.route('/system_status/<system_id>')
def get_system_status(system_id):
    """Get current status of a system"""
    if system_id not in SYSTEMS:
        return jsonify({'error': 'System not found'}), 404
    
    status = check_system_status(system_id)
    SYSTEMS[system_id]['status'] = status
    
    return jsonify({
        'system_id': system_id,
        'status': status,
        'url': f'http://localhost:{SYSTEMS[system_id]["port"]}' if status == 'running' else None
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    # Update all system statuses
    for system_id in SYSTEMS:
        SYSTEMS[system_id]['status'] = check_system_status(system_id)
    
    stats = {
        'total_systems': len(SYSTEMS),
        'running_systems': sum(1 for s in SYSTEMS.values() if s['status'] == 'running'),
        'stopped_systems': sum(1 for s in SYSTEMS.values() if s['status'] == 'stopped'),
        'systems': {k: v['status'] for k, v in SYSTEMS.items()},
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(stats)

def check_system_status(system_id):
    """Check if a system is running by checking its port"""
    if system_id not in SYSTEMS:
        return 'unknown'
    
    port = SYSTEMS[system_id]['port']
    
    # Check if port is in use
    result = os.system(f"lsof -i:{port} > /dev/null 2>&1")
    return 'running' if result == 0 else 'stopped'

@app.route('/logs/<system_id>')
def view_logs(system_id):
    """View logs for a specific system"""
    if system_id not in SYSTEMS:
        return "System not found", 404
    
    # This would show system logs
    return render_template('logs.html', system_id=system_id, system=SYSTEMS[system_id])

if __name__ == '__main__':
    print("🏛️  PMC School Management Systems Dashboard")
    print("=" * 60)
    print("📊 Dashboard starting...")
    print("🌐 Access the dashboard at: http://localhost:5040")
    print("🛑 Use Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    # Get port from environment variable for deployment
    port = int(os.environ.get('PORT', 5040))
    
    app.run(debug=False, host='0.0.0.0', port=port)
