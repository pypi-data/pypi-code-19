from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

QUEUES = getattr(settings, 'XZ_QUEUES', None)
if QUEUES is None:
    raise ImproperlyConfigured("You have to define XZ_QUEUES in settings.py")

