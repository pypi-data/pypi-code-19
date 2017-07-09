import os
import modconf
import ssl

from ws_web_aiohttp.tests.conf.log import *

url = 'www.charlesrymal.com'

certfile = '/etc/letsencrypt/live/www.charlesrymal.com/fullchain.pem'
keyfile = '/etc/letsencrypt/live/www.charlesrymal.com/privkey.pem'

SSL_CONTEXT = None

class Conf(object):
    SCHEME = 'http'
    SCHEME_WS = 'ws'
    PORT = 8080
    
    STATIC_DIR = '/var/www/ws_web_aiohttp/static'
    
    @classmethod
    def url_root(cls):
        return '{}://localhost:{}'.format(cls.SCHEME, cls.PORT)

    @classmethod
    def ws_root(cls):
        return '{}://localhost:{}'.format(cls.SCHEME_WS, cls.PORT)


