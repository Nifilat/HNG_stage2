import os
import sys

from django.core.wsgi import get_wsgi_application

# Add your project to the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "user_authentication"))

# Set the settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_authentication.settings")

# Get the WSGI application
application = get_wsgi_application()
