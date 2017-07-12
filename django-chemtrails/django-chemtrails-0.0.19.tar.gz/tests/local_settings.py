# -*- coding: utf-8 -*-

from .settings import INSTALLED_APPS

INSTALLED_APPS += [
    'django_extensions'
]

CHEMTRAILS = {
    'ENABLED': True,
    'IGNORE_MODELS': [
        'admin.logentry',
        'migrations.migration',
    ]
}
