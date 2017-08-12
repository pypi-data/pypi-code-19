from celery import Celery
app = Celery('frontendcelery')
app.config_from_object('recastfrontend.celeryconfig')