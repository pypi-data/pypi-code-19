import logging
import logging.config
import os

FORMAT = '[%(asctime)s] %(levelname)s pid:%(process)d %(name)s:%(lineno)d %(message)s'
def level_for_environment():
    return logging.INFO if os.environ.get('ENVIRONMENT') == 'prod' else logging.DEBUG

def setup_logging(level=None):
    level = level if level else level_for_environment()
    configuration = {
        'version'   : 1,
        'disable_existing_loggers'  : False,
        'formatters'                : {
            'standard'              : {
                'format'            : FORMAT,
                'dateformat'        : '%d/%b/%Y:%H:%M:%S %z',
            },
        },
        'handlers'                  : {
            'console'               : {
                'level'             : level,
                'class'             : 'logging.StreamHandler',
                'formatter'         : 'standard',
            },
        },
        'loggers'                   : {
            ''                      : {
                'handlers'          : ['console'],
                'level'             : level,
                'propogate'         : True,
            },
        },
    }
    logging.config.dictConfig(configuration)
