import enum
import os
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
    def prepare(cls, mode, port=None, addr_storage=None, console=False):
        mode = Conf.Mode.from_string(mode)
        
        cls.conf_sheets = modconf.import_conf('ws_sheets.tests.conf.simple')
        
        cls.STORAGE_HOST = 'localhost'

        if mode == cls.Mode.DEVELOP:
            cls.STORAGE_ADDR = ('localhost',10001) if addr_storage is None else addr_storage

            cls.LOG_DIR = '.dev/var/log/ws_sheets_server'
            cls.PORT = 10003 if port is None else port
        elif mode == cls.Mode.DEPLOY:
            cls.STORAGE_ADDR = ('localhost',10002) if addr_storage is None else addr_storage

            cls.LOG_DIR = '/var/log/ws_sheets_server'
            cls.PORT = 10004 if port is None else port

        LOG_FILE = os.path.join(cls.LOG_DIR, 'debug.log')
        LOG_FILE_CELL = os.path.join(cls.LOG_DIR, 'cell/debug.log')

        try:
            os.makedirs(os.path.dirname(LOG_FILE))
        except OSError as e: pass
        
        try:
            os.makedirs(os.path.dirname(LOG_FILE_CELL))
        except OSError as e: pass
       
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
                    'file_cell': {
                        'level': 'DEBUG',
                        'class': 'logging.FileHandler',
                        'filename':LOG_FILE_CELL,
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
                    'ws_sheets': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_sheets_server': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_sheets.cell/cell': {
                        'handlers': ['file_cell'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    },
                'formatters': {
                    "basic":{
                        "format":"%(asctime)s %(process)s %(module)10s %(funcName)10s %(levelname)7s %(message)s"
                        }
                    }
                }
        
        if console:
            cls.log_console()

    @classmethod
    def log_console(cls):
        for l in cls.LOGGING['loggers'].values():
            l['handlers'] = ['console']
  
  

  
  
