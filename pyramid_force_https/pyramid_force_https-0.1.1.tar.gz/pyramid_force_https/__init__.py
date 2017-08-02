# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from pyramid.httpexceptions import HTTPFound

import logging


def includeme(config):
    config.add_tween('pyramid_force_https.EnforceHTTPS')


class EnforceHTTPS(object):
    """Enforce HTTPS for every request."""

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        if request.url.startswith('http://'):
            secure_url = request.url.replace('http://', 'https://')

            if request.registry.settings.get('pyramid_force_https.structlog'):
                import structlog
                logger = structlog.getLogger(__name__)
                logger.info('Forcing SSL', orig=request.url, dest=secure_url)
            else:
                logger = logging.getLogger(__name__)
                logger.info(
                    'Forcing SSL: {} -> {}'.format(request.url, secure_url))

            return HTTPFound(secure_url)
        return self.handler(request)
