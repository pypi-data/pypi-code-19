# -*- coding: utf-8
import six

from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.apps import AppConfig

from . import connections, logger, flexconfig


class ElasticsearchFlexConfig(AppConfig):
    name = 'elasticsearch_flex'

    def ready(self):
        self.__init_connection()
        self.__import_modules()

    def __init_connection(self):
        host = flexconfig.get('host')
        if host is None:
            connections.create_connection(hosts=['localhost'])
            logger.info('No Elasticsearch host specified, assuming "localhost"')
            return

        if isinstance(host, dict):
            connections.configure(**host)
        elif isinstance(host, six.string_types):
            connections.create_connection(hosts=[host])
        else:
            raise ImproperlyConfigured('<host = {0}> for ElasticsearchFlex is incorrect'.format(host))

        logger.info('Elasticsearch connection configured using <%s>', host)

    def __import_modules(self):
        # Discover the modules
        import elasticsearch_flex.signals
        _loaded = []
        for app_name in settings.INSTALLED_APPS:
            module = '{}.search_indexes'.format(app_name)
            try:
                import_module(module)
                _loaded.append(app_name)
            except ImportError:
                pass
        if len(_loaded):
            logger.info('Loaded search indices for %s apps: %s', len(_loaded), _loaded)
