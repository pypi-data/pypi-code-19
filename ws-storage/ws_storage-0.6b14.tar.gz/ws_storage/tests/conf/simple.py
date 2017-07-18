import os
import enum

import modconf

class Conf(object):
    class Mode(enum.Enum):
        DEVELOP=1
        DEPLOY=2
        
        @classmethod
        def from_string(cls, s):
            if s == 'DEVELOP':
                return cls.DEVELOP
            elif s == 'DEPLOY':
                return cls.DEPLOY
            else:
                raise Exception()

    @classmethod
    def log_console(cls):
        for l in cls.LOGGING['loggers'].values():
            l['handlers'] = ['console']

    @classmethod
    def prepare(cls, conf_dir=None, impl=None, port=None, **kwargs):

        cls.CONF_DIR = conf_dir

        cls.IMPL = impl if impl is not None else 'AS3'

        cls.DEV = kwargs.get('dev', False)

        if cls.DEV:
            cls.PORT = 10001 if port is None else port
            cls.STORAGE_DIR = '.dev/etc/ws_storage/storage'
            cls.LOG_FILE = '.dev/var/log/ws_storage/debug.log'
        else:
            cls.PORT = 10002 if port is None else port
            cls.STORAGE_DIR = '/etc/ws_storage/storage'
            cls.LOG_FILE = '/var/log/ws_storage/debug.log'

        try:
            os.makedirs(os.path.dirname(cls.LOG_FILE))
        except os.error: pass

        cls.LOGGING = {
                'version': 1,
                'disable_existing_loggers': False,
                'handlers': {
                    'file': {
                        'level': 'DEBUG',
                        'class': 'logging.FileHandler',
                        'filename': cls.LOG_FILE,
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
                    'async_patterns': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_storage': {
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

        if kwargs.get('console', False):
            cls.log_console()

        try:
            cls.AWS = modconf.import_class('aws', 'Conf', tuple(), folder=cls.CONF_DIR)
        except:
            cls.AWS = type('AWS', tuple(), {})
            cls.AWS.ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
            cls.AWS.SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
            cls.AWS.REGION = os.environ['AWS_REGION']
            cls.AWS.BUCKET = os.environ['AWS_BUCKET']
        


