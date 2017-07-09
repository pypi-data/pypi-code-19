import enum
import os
import modconf
import ssl

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
                raise Exception('invalid mode: {}'.format(s))
    
    @classmethod
    def prepare(cls, mode):
        cls.MODE = cls.Mode.from_string(mode)

        if cls.MODE == cls.Mode.DEVELOP:
            LOG_FILE = '.dev/var/log/ws_web_aiohttp/debug.log'
        elif cls.MODE == cls.Mode.DEPLOY:
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
                        "format":"%(asctime)s %(module)12s %(levelname)s %(message)s"
                        }
                    }
                }
 
    @classmethod
    def log_console(cls):
        for l in cls.LOGGING['loggers'].values():
            l['handlers'] = ['console']
       
