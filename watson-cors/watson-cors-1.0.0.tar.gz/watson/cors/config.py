# -*- coding: utf-8 -*-

defaults = {
    'allow_origin': None,
    'allow_credentials': False,
    'allow_methods': (
        'DELETE',
        'GET',
        'OPTIONS',
        'PATCH',
        'POST',
        'PUT',
    ),
    'allow_headers': (
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ),
    'expose_headers': None,
    'max_age': 86400,
}
