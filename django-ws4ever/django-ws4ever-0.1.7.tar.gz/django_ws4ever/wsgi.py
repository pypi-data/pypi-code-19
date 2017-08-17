"""
WSGI config for django_ws4ever project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_ws4ever.settings")
application = get_wsgi_application()

# gunicorn 用的 websocket wsgi
from geventwebsocket import Resource
from ws4ever.helpers import get_websocket_resources
ws_application = Resource(get_websocket_resources())
