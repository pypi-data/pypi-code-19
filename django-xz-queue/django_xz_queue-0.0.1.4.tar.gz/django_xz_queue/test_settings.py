# -*- coding: utf-8 -*-
import os


SECRET_KEY = 'a'


ENDPOINT = 'http://xxxxxxx.mns.cn-hangzhou-internal.aliyuncs.com/'
ACCID = 'xxxxxx'
ACCKEY = 'dddddddd'

XZ_QUEUES = {
    'sms-send': {
        'QUEUE_TYPE': 'mns', # queue type msn-> aliyun
        'QUEUE_CONSUMER_MODULE': 'web.queue_consumers_function.sms-send', # consumer module
        'QUEUE_CONNECTION': {  # queue save
            'ENDPOINT': ENDPOINT,
            'ACCID': ACCID,
            'ACCKEY': ACCKEY
        }
    }
}


try:
    from django.utils.log import NullHandler
    nullhandler = 'django.utils.log.NullHandler'
except:
    nullhandler = 'logging.NullHandler'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django_xz_queue',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "rq_console": {
            "level": "DEBUG",
            #"class": "logging.StreamHandler",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },
        'null': {
            'level': 'DEBUG',
            'class': nullhandler,
        },
    },
    'loggers': {
        "rq.worker": {
            "handlers": ['null'],
            "level": "ERROR"
        },
    }
}






BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


