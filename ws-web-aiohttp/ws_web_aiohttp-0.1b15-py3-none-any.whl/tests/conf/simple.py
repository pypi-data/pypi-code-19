import enum
import os
import ssl

import modconf

class Conf(object):
 
    certfile = '/etc/letsencrypt/live/www.charlesrymal.com/fullchain.pem'
    keyfile = '/etc/letsencrypt/live/www.charlesrymal.com/privkey.pem'

    STATIC_DIR = '/var/www/ws_web_aiohttp/static'
    
    @classmethod
    def url_root(cls):
        """
        root url for accessing site for testing
        """
        return '{}://{}{}'.format(cls.SCHEME, cls.HOST, cls.PREFIX)

    @classmethod
    def ws_root(cls):
        """
        root websockets url for accessing site for testing
        """
        return '{}://{}{}'.format(cls.SCHEME_WS, cls.HOST, cls.PREFIX)

    @classmethod
    def prepare(cls, **kwargs):
        """
        defaults are overridden by ``kwargs``
        """
        print('{}.{}'.format(cls.__module__, cls.__name__))
        print('kwargs')
        print('\n- '.join('{} = {}'.format(k, v) for k, v in kwargs.items()))

        cls.kwargs = kwargs
        
        cls.DEV = cls.kwargs.get('dev', False)

        cls.SCHEME, cls.SCHEME_WS = cls._scheme()
        
        cls.PORT = cls._port()
        
        cls.PREFIX = cls._prefix()

        cls.ADDR_COMPUTE = cls._addr_compute()

        cls.SSL_CONTEXT = cls._ssl_context()

        cls.HOST = 'www.charlesrymal.com'

        if cls.DEV:
            LOG_FILE = '.dev/var/log/ws_web_aiohttp/debug.log'
        else:
            LOG_FILE = '/var/log/ws_web_aiohttp/debug.log'
        
        try:
            os.makedirs(os.path.dirname(LOG_FILE))
        except: pass
        
        cls.LOGGING = {
                'version': 1,
                'disable_existing_loggers': False,
                'handlers': {
                    'file': {
                        'level': 'DEBUG',
                        'class': 'logging.FileHandler',
                        'filename':LOG_FILE,
                        'formatter':'basic'
                        },
                    'console':{
                        'level':'DEBUG',
                        'class':'logging.StreamHandler',
                        'formatter': 'basic'
                        },
                    },
                'loggers':{
                    '__main__': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_storage': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_sheets_server': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_web_aiohttp': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    },
                'formatters': {
                    "basic":{
                        "format":"%(asctime)s %(process)s %(module)10s %(funcName)20s %(levelname)7s %(message)s"
                        }
                    }
                }

        if cls.kwargs.get('console', False):
            cls.log_console()

        cls.CONF_DIR = cls.kwargs.get('conf_dir', None) or '/etc/ws_web_aiohttp/conf/'

        cls.test_key = cls.kwargs.get('test_key', None)

        try:
            cls.google_oauth2 = modconf.import_conf('google_oauth2', cls.CONF_DIR)
        except:
            cls.google_oauth2 = type('GoogleOauth2', tuple(), {
                'client_id': os.environ['GOOGLE_CLIENT_ID'],
                'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
                })

        try:
            cls.PG = modconf.import_conf('postgresql', cls.CONF_DIR)
        except:
            cls.PG = type('PG', tuple(), {
                'host': os.environ['PG_HOST'],
                'db': os.environ['PG_DB'],
                'user': os.environ['PG_USER'],
                'password': os.environ['PG_PASSWORD'],
                })

        cls.ws_sheets_server = modconf.import_class(
                'ws_sheets_server.tests.conf.simple', 'Conf', tuple(), {'dev': cls.DEV})

    @classmethod
    def _prefix(cls):
        if cls.kwargs.get('prefix', None):
            return cls.kwargs['prefix']

        if cls.DEV:
            return '/dev/'

        return '/'

    @classmethod
    def _port(cls):
        if cls.kwargs.get('port', None):
            return cls.kwargs['port']

        if cls.DEV:
            return 10005

        return 10006

    @classmethod
    def _ssl_context(cls):
        if cls.kwargs.get('ssl', False):
            ssl = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            ssl.load_cert_chain(cls.certfile, cls.keyfile)
            return ssl

        return None

    @classmethod
    def _addr_compute(cls):
        if cls.kwargs.get('addr_compute', None):
            return cls.kwargs['addr_compute']
        
        if cls.DEV:
            return ('localhost', 10003)
        
        return ('localhost', 10004)
   
    @classmethod
    def _scheme(cls):
        if cls._scheme_secure():
            return 'https', 'wss'
        else:
            return 'http', 'ws'

    @classmethod
    def _scheme_secure(cls):
        if 'scheme_secure' in cls.kwargs:
            return cls.kwargs['scheme_secure']
        
        return True

    @classmethod
    def log_console(cls):
        for l in cls.LOGGING['loggers'].values():
            l['handlers'] = ['console']
       

