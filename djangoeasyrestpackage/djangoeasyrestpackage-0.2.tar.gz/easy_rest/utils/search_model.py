from django.apps import apps
from django.db import models


class GetModelByString(object):
    def __init__(self, registered_models=None):
        if registered_models is None:
            registered_models = ['__all__']
        self.registered_models = registered_models

    def get_model(self, model_name, app):
        if app not in self.registered_models and '__all__' not in self.registered_models:
            return self.empty()
        return apps.get_model(app_label=app, model_name=model_name)

    def empty(self):
        return models.Manager().none()  # empty query set
