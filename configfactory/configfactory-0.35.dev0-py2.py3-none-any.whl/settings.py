import os

import appdirs
import dj_database_url

from configfactory.support import config, dirs

ALLOWED_HOSTS = ['*']

SECRET_KEY = '28$0ld^(u&7o%f_e4sqh@rl&lere4kzsca#@&6@f+#5k7r963b'

DEBUG = True

ROOT_URLCONF = 'configfactory.urls'

DATABASES = {
    'default': dj_database_url.config(
        env='CONFIGFACTORY_DATABASE_URL',
        default=config['database.url']
    )
}

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': '.html',
            'auto_reload': True,
            'context_processors': [
                'configfactory.configurations.context_processors.components',
                'configfactory.users.context_processors.auth',
                'configfactory.support.context_processors.version',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'configfactory.support.middleware.logging_middleware',
]

INSTALLED_APPS = [

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django_jinja',
    'guardian',

    'configfactory',
    'configfactory.environments',
    'configfactory.configurations',
    'configfactory.users',
]

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATICFILES_DIRS = (
    dirs.package_dir('static'),
)

LOGGING_DIR = config.get(
    'logging.dir',
    appdirs.user_data_dir('logs'),
)

LOGGING_FILENAME = config.get(
    'logging.filename',
    'configfactory.log'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)-15s] (%(name)s) %(levelname)s - %(message)s",
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(
                LOGGING_DIR,
                LOGGING_FILENAME
            ),
            'maxBytes': 5000000,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'level': 'WARNING',
            'handlers': ['console', 'file'],
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        # 'django.db': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        'configfactory': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    }
}

TIME_ZONE = 'UTC'

ENVIRONMENTS = config.get('environments', [])

CLEANSED_HIDDEN = config.get(
    'cleansed.hidden',
    default='api token key secret pass password signature'
)

CLEANSED_SUBSTITUTE = config.get(
    'cleansed.substitute',
    default='***************'
)

######################################
# Auth / users settings
######################################
DEFAULT_USERS = config.get('users', [])

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)

ANONYMOUS_USER_NAME = None

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'index'
