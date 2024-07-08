import os
import sys

from django.core.wsgi import get_wsgi_application


sys.path.append(os.path.join(os.path.dirname(__file__), "user_authentication"))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_authentication.settings")


application = get_wsgi_application()


app = application
