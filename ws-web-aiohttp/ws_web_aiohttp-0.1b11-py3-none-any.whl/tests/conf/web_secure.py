import os
import modconf
import ssl

from ws_web_aiohttp.tests.conf.log import Conf as Conf_log

class Conf(Conf_log):
    SCHEME = 'https'
    SCHEME_WS = 'wss'
    PORT_PUB = 443

    certfile = '/etc/letsencrypt/live/www.charlesrymal.com/fullchain.pem'
    keyfile = '/etc/letsencrypt/live/www.charlesrymal.com/privkey.pem'
    

    STATIC_DIR = '/var/www/ws_web_aiohttp/static'

    @classmethod
    def prepare(cls, mode_s, port=None, addr_compute=None):
        print('config')
        print('addr compute', addr_compute)

        Conf_log.prepare(mode_s)
       
        if cls.MODE == Conf.Mode.DEVELOP:
            cls.PORT = port or 10005
            cls.PREFIX = '/dev/'

            cls.ADDR_COMPUTE = ('localhost', 10003) if addr_compute is None else addr_compute

        elif cls.MODE == Conf.Mode.DEPLOY:
            cls.PORT = port or 10006
            cls.PREFIX = '/'

            cls.ADDR_COMPUTE = ('localhost', 10004) if addr_compute is None else addr_compute

        if False:
            try:
                cls.SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                cls.SSL_CONTEXT.load_cert_chain(cls.certfile, cls.keyfile)
            except Exception as e:
                print(e)
                cls.SSL_CONTEXT = None
        else:
            cls.SSL_CONTEXT = None

        cls.HOST = 'www.charlesrymal.com'

    @classmethod
    def url_root(cls):
        return '{}://{}:{}{}'.format(cls.SCHEME, cls.HOST, cls.PORT_PUB, cls.PREFIX)

    @classmethod
    def ws_root(cls):
        return '{}://{}:{}{}'.format(cls.SCHEME_WS, cls.HOST, cls.PORT_PUB, cls.PREFIX)


