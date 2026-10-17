"""WSGI config for hemoflow project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hemoflow.settings')

application = get_wsgi_application()
