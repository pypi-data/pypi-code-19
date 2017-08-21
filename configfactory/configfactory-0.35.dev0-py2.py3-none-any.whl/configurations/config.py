from collections import OrderedDict

from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string

from configfactory.configurations import settings
from configfactory.configurations.backends.base import ConfigBackend
from configfactory.environments.helpers import get_environment_alias
from configfactory.environments.models import Environment
from configfactory.environments.settings import BASE_ENVIRONMENT
from configfactory.models import Component
from configfactory.utils import flatten_dict, json_dumps, json_loads, merge_dicts

backend = SimpleLazyObject(func=lambda: _get_backend())  # type: ConfigBackend


def get_settings(component, environment=None, flatten=False):
    """
    Get component settings.
    """

    settings_dict = json_loads(component.settings_json)
    base_settings_dict = settings_dict.get(
        BASE_ENVIRONMENT,
        {}
    )

    if isinstance(environment, str):
        environment = Environment.objects.get(environment)

    if environment.is_base:
        ret = base_settings_dict
    else:
        env_settings_dict = settings_dict.get(environment.alias)
        if env_settings_dict is None:
            if environment.fallback:
                env_settings_dict = settings_dict.get(
                    environment.fallback,
                    {}
                )
            else:
                env_settings_dict = {}
        ret = merge_dicts(
            base_settings_dict,
            env_settings_dict,
        )

    if flatten:
        ret = flatten_dict(ret)

    return ret


def get_all_settings(environment, flatten=False):
    """
    Get all settings.
    """
    data = OrderedDict([
        (
            component.alias,
            get_settings(
                component=component,
                environment=environment
            )
        )
        for component in Component.objects.all()
    ])
    if flatten:
        return flatten_dict(data)
    return data


def update_settings(component, environment, settings):
    """
    Update component settings.
    """

    environment = get_environment_alias(environment)
    settings_dict = json_loads(component.settings_json)

    if isinstance(settings, str):
        settings = json_loads(settings)

    settings_dict[environment] = settings

    component.settings_json = json_dumps(settings_dict)
    component.save()

    return component


def _get_backend():
    klass = import_string(settings.CONFIG_BACKEND['class'])
    options = settings.CONFIG_BACKEND.get('options', {})
    return klass(**options)
