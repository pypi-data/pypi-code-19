import logging

from django.conf import settings
from elasticsearch_dsl.connections import connections

__version__ = '0.3.2'

logger = logging.getLogger('elasticsearch_flex')

default_app_config = 'elasticsearch_flex.apps.ElasticsearchFlexConfig'

flexconfig = dict()

if hasattr(settings, 'ELASTICSEARCH_FLEX'):
    flexconfig.update(settings.ELASTICSEARCH_FLEX)

__all__ = ('connections',)
