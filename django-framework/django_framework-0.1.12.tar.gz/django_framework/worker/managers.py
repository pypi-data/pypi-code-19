
from django_framework.django_helpers.manager_helpers.base_manager import BaseManager

from django_framework.django_helpers.manager_helpers.manager_registry import register_manager

from django_framework.django_helpers.model_helpers.model_registry import get_model

class JobManager(BaseManager):
    Model = get_model(model_name = 'Job')
    pass

register_manager(JobManager)
