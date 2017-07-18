import os
import logging

ENV = os.getenv('PYTHONENV', 'prod')

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

HOST = 'localhost'
PORT = 8080

SSL_VERIFY = False

DEFAULT_ROUTINES = ['auth', 'ping', 'status', 'system']

if ENV == 'prod':
    LOG_LEVEL = logging.INFO
    HOST = 'unicorn.ahst.fr'
    #SSL_VERIFY = True
