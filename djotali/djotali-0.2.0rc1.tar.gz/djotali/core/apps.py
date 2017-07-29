import logging

from django.apps import AppConfig

_logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    name = 'djotali.core'
    verbose_name = 'core'
