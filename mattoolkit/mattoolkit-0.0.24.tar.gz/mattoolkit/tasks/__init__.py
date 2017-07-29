from celery import Celery

from .config import CeleryConfig

def init_app():
    app = Celery('tasks')
    app.config_from_object(CeleryConfig)
    return app

app = init_app()
