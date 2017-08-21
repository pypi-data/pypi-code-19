from configfactory.settings import *

LOGGING = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

BASE_ENVIRONMENT = 'default'

ENVIRONMENTS = [
    {
        'alias': 'development'
    },
    {
        'alias': 'testing',
        'fallback': 'development'
    }
]
