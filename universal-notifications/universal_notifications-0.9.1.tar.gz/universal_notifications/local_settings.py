# -*- coding: utf-8 -*-
DEBUG = True
SASS_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG
# COMPRESS_ENABLED = True
ADMINS = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'XXX',
        'USER': 'XXX',
        'PASSWORD': 'XXX',
        'HOST': 'localhost',
        'PORT': '3306',
        'ATOMIC_REQUESTS': True
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'universal_notifications',
)


SECRET_KEY = 'foo'

# INTERNAL_IPS = (
#     "127.0.0.1",
# )
# CELERY_ALWAYS_EAGER = True
# DIET_COMPRESS_STATIC_IMAGES = False
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     }
# }

# if SASS_DEBUG:
#     COMPRESS_PRECOMPILERS = (
#         # ('text/x-scss', 'sass --scss  --debug-info {infile} {outfile}'),
#         ('text/x-scss', 'sass --scss --compass  --debug-info {infile} {outfile}'),
#     )
# else:
#     COMPRESS_PRECOMPILERS = (
#         ('text/x-scss', 'sass --scss --compass {infile} {outfile}'),
#     )
# # disable on local
# RAVEN_CONFIG = {
#     'dsn': '',
# }

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# # uncomment the settings below to see all db queries on console
# #
# # LOGGING = {
# #     'disable_existing_loggers': False,
# #     'version': 1,
# #     'handlers': {
# #         'console': {
# #             # logging handler that outputs log messages to terminal
# #             'class': 'logging.StreamHandler',
# #             'level': 'DEBUG',  # message level to be written to console
# #         },
# #     },
# #     'loggers': {
# #         '': {
# #             # this sets root level logger to log debug and higher level
# #             # logs to console. All other loggers inherit settings from
# #             # root level logger.
# #             'handlers': ['console'],
# #             'level': 'DEBUG',
# #             'propagate': False,  # this tells logger to send logging message
# #                                  # to its parent (will send if set to True)
# #         },
# #         'django.db': {
# #             # django also has database level logging
# #         },
# #     },
# # }

# # if you need django debug toolbar only for local (watch out for tests):
# # if you need django debug toolbar only for local (watch out for tests):
# USE_DEBUG_TOOLBAR = False
# # USE_DEBUG_TOOLBAR = True

# if USE_DEBUG_TOOLBAR:
#     from django.conf import settings

#     MIDDLEWARE_CLASSES = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + list(settings.MIDDLEWARE_CLASSES)

#     INSTALLED_APPS = list(settings.INSTALLED_APPS) + ['debug_toolbar']
#     DEBUG_TOOLBAR_PATCH_SETTINGS = True

#     REST_FRAMEWORK = settings.REST_FRAMEWORK

#     REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = list(
#         REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']) + ['rest_framework.authentication.SessionAuthentication']


# # update test server with counting number of queries
# USE_QUERIES_NUMBER_IN_TEST_SERVER = True
# if USE_QUERIES_NUMBER_IN_TEST_SERVER:
#     from django.conf import settings

#     QUERIES_NUMBER_WARN = 7
#     QUERIES_ERR_NUMBER = 15

#     INSTALLED_APPS = list(settings.INSTALLED_APPS) + ['getreferd.utils.hacks']


# AWS_ACCESS_KEY_ID = 'AKIAJQCI5DWOR3SITIVQ'
# AWS_SECRET_ACCESS_KEY = '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'
# AWS_STORAGE_BUCKET_NAME = 'getreferd-api-dev'
