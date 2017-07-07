
from django_framework.django_helpers.manager_helpers.base_manager import BaseManager

from django_framework.django_helpers.manager_helpers.manager_registry import register_manager

from django_framework.django_helpers.model_helpers.model_registry import get_model

class BasicTestRunManager(BaseManager):
    Model = get_model(model_name = 'BasicTestRun')

    @classmethod
    def _relationship_name_format(cls, relationship_name=None, relationship_list=None):
        if relationship_name == 'profile':
            query_key = 'id__in'
            query_key = 'pass' # skip over it
        return query_key, relationship_list

register_manager(BasicTestRunManager)
