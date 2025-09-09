#!/var/www/yourusername_pythonanywhere_com_wsgi.py
import sys
import os

# Add your project directory to sys.path
project_home = '/home/yourusername/PMC'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

# Import your Flask app
sys.path.append('/home/yourusername/PMC')
from wsgi import application
