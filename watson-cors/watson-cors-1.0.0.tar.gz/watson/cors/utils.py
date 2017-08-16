# -*- coding: utf-8 -*-
from watson.common import datastructures
from watson.cors import config


def generate_cors_config(container, route, **kwargs):
    config_ = datastructures.merge_dicts(
        config.defaults,
        container.get('application.config').get('cors', {}),
        route.options.get('cors', {}))
    if route.accepts:
        config_['allow_methods'] = route.accepts
    return datastructures.merge_dicts(config_, kwargs)


def process_cors(
        request,
        response,
        allow_origin,
        allow_credentials,
        allow_methods,
        allow_headers,
        expose_headers,
        max_age):
    if hasattr(response, '_cors_processed'):
        return True
    if request.is_method('OPTIONS'):
        if max_age:
            response.headers.set('Access-Control-Max-Age', max_age)
        if allow_methods:
            response.headers.set(
                'Access-Control-Allow-Methods',
                ', '.join(allow_methods))
        if allow_headers:
            response.headers.set(
                'Access-Control-Allow-Headers',
                ', '.join(allow_headers))
    if expose_headers:
        response.headers.set(
            'Access-Control-Expose-Headers',
            ', '.join(expose_headers))
    if allow_origin:
        origin = request.headers['Origin']
        if isinstance(allow_origin, (list, tuple)) and origin in allow_origin:
            allow_origin = origin
        response.headers.set(
            'Access-Control-Allow-Origin',
            allow_origin)
    if allow_credentials:
        response.headers.set('Access-Control-Allow-Credentials', 'true')
    response._cors_processed = True
