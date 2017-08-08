import warnings

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from .mail_template import Variable


# Available templates and variables for the mail editor.
TEMPLATES = getattr(django_settings, 'MAIL_EDITOR_CONF', {})
if TEMPLATES:
    warnings.warn('Setting MAIL_EDITOR_CONF is deprecated, please use MAIL_EDITOR_TEMPLATES.', DeprecationWarning)
else:
    TEMPLATES = getattr(django_settings, 'MAIL_EDITOR_TEMPLATES', {})


# The base URL when relative links are found.
BASE_URL = getattr(django_settings, 'MAIL_EDITOR_BASE_URL', None)
if not BASE_URL:
    raise ImproperlyConfigured("The setting MAIL_EDITOR_BASE_URL must be configured. For a fallback when you don't pass a base_url via the context.")


def get_choices():
    choices = []
    for key, values in TEMPLATES.items():
        choices += [(key, values.get('name'))]
    return choices


def get_config():
    config = {}
    for key, values in TEMPLATES.items():
        subject_variables = []
        for var in values.get('subject', []):
            subject_variables.append(Variable(**var))

        body_variables = []
        for var in values.get('body', []):
            body_variables.append(Variable(**var))

        config[key] = {
            'subject': subject_variables,
            'body': body_variables
        }
    return config
