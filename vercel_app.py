import os
import sys

from django.core.wsgi import get_wsgi_application

# Ensure the project base directory is in the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "user_authentication"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_authentication.settings")

# Get the WSGI application for the Django project
application = get_wsgi_application()

# Vercel requires the WSGI callable to be named 'app'
app = application
