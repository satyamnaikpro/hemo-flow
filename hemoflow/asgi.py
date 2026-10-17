"""ASGI config for hemoflow project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hemoflow.settings')

application = get_asgi_application()
