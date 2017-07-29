# coding: utf-8
import os
import sys
from multiprocessing import Process

from celery import Celery
from celery.bin.worker import worker
from django.conf import settings

from djotali.core.utils import is_celery_running

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djotali.settings')

app = Celery('djotali')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# The following code automatically launch a celery worker if in DEV mode
# It is for convenience reason and not needed otherwise as production and testing modes have other ways to start celery worker
if os.getenv('DEV') and not settings.TESTING and not is_celery_running() and 'runserver' in sys.argv:
    celery_worker_thread = Process(target=worker(app=app).run)
    celery_worker_thread.daemon = True
    celery_worker_thread.start()
