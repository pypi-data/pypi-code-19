from django.db import transaction

from configfactory.configurations import config
from configfactory.environments.models import Environment
from configfactory.exceptions import ComponentDeleteError, InjectKeyError
from configfactory.models import Component
from configfactory.utils import inject_dict_params


def delete_component(component: Component):
    """
    Delete component.
    """

    with transaction.atomic():

        component.delete()

        for environment in Environment.objects.all():
            try:
                inject_dict_params(
                    data=config.get_settings(
                        component=component,
                        environment=environment
                    ),
                    params=config.get_all_settings(environment, flatten=True),
                    flatten=True,
                    raise_exception=True
                )
            except InjectKeyError as e:
                raise ComponentDeleteError(
                    'One of other components is referring '
                    'to `%(key)s` key.' % {
                        'key': e.key
                    }
                )
