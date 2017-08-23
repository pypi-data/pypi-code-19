"""
dj12: 12factor config support for Django.

* https://12factor.net/
* https://12factor.net/config
* https://gitlab.com/aiakos/dj12
"""

try:
    from urllib.parse import urlsplit, urlunsplit
except ImportError:
    from urlparse import urlsplit, urlunsplit

import django_cache_url
import dj_database_url
import dj_email_url
import os
import logging
import six
import sys

from ._bool import to_bool

logger = logging.getLogger(__name__)


def _get_many(key, default, transform):
    config = {}

    for (k, v) in six.iteritems(os.environ):
        _SUFFIX = '_' + key
        _OFFSET = len(_SUFFIX)

        if k.endswith(_SUFFIX):
            prefix = k[:-_OFFSET]

            if not prefix.isupper():
                # i.e. it was not already all upper-cased
                logger.warning("Ignoring %s because the prefix (%s) is not all upper-case - dj12 will automatically convert prefixes to lower-case", key, prefix)
                continue

            config[prefix.lower()] = transform(v)

    if not 'default' in config:
        config['default'] = transform(os.getenv(key, default))

    return config


class Config(object):
    pass


def get_config():
    c = Config()

    c.USE_I18N = True
    c.USE_L10N = True
    c.USE_TZ = True

    c.DEBUG = to_bool(os.getenv('DEBUG'), False)

    if c.DEBUG:
        logger.warning("INSECURE - DEBUG is enabled.")

    c.SECRET_KEY = os.getenv('SECRET_KEY')

    if not c.SECRET_KEY:
        if c.DEBUG:
            c.SECRET_KEY = 'debugkey'
        else:
            sys.exit("""DEBUG is False but no SECRET_KEY is set in the environment - either it has been hardcoded (bad) or not set at all (bad) - exit()ing for safety reasons""")

    c.BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000/')
    if not c.BASE_URL.endswith('/'):
        c.BASE_URL += '/'
    base_url = urlsplit(c.BASE_URL)
    c.BASE_HOST = urlunsplit(base_url._replace(path=''))

    https = base_url.scheme == 'https'
    if not https:
        logger.warning("INSECURE - running without https enabled.")

    c.SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if to_bool(os.getenv('TRUST_X_FORWARDED_PROTO'), False) else None
    if https and not c.SECURE_PROXY_SSL_HEADER:
        logger.error("Django won't be able to detect if the request was sent using https; this will probably result in redirection loop.")

    c.SECURE_SSL_REDIRECT = https
    c.SESSION_COOKIE_SECURE = https

    c.SECURE_HSTS_PRELOAD = to_bool(os.getenv('HSTS_PRELOAD'), False)
    
    if c.SECURE_HSTS_PRELOAD and not https:
        logger.warning("Set BASE_URL to a https:// URL before enabling HSTS_PRELOAD.")

    c.SECURE_HSTS_INCLUDE_SUBDOMAINS = to_bool(os.getenv('HSTS_INCLUDE_SUBDOMAINS'), False)
    c.SECURE_HSTS_SECONDS = int(os.getenv('HSTS_SECONDS') or 10886400 if c.SECURE_HSTS_PRELOAD else 3600 if https else 0)

    c.ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', base_url.hostname).split(',')

    if not base_url.hostname in c.ALLOWED_HOSTS:
        logger.warning("BASE_URL's hostname is not a member of ALLOWED_HOSTS list.")

    c.FORCE_SCRIPT_NAME = base_url.path

    c.DATABASES = _get_many('DATABASE_URL', 'sqlite:///db.sqlite3', dj_database_url.parse)
    c.CACHES = _get_many('CACHE_URL', 'locmem://', django_cache_url.parse)
    c.__dict__.update(dj_email_url.parse(os.getenv('EMAIL_URL', 'console://')))

    c.DEFAULT_FROM_EMAIL = os.getenv('EMAIL_FROM', "webmaster@localhost")

    c.LANGUAGE_CODE = os.getenv('LANG', 'en-us').replace('_', '-').split('.', 1)[0].lower()

    if c.LANGUAGE_CODE == 'c':
        c.LANGUAGE_CODE = 'en-us'

    c.TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')

    c.RAVEN_CONFIG = dict(
        dsn = os.getenv('RAVEN_URL'),
    )

    c.LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'stderr': {
                'level': 'INFO' if not c.DEBUG else 'DEBUG',
                'class': 'logging.StreamHandler',
            }
        },
        'root': {
            'handlers': ['stderr'],
        },
    }

    return c.__dict__
