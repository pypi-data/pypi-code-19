import os
import modconf
import ssl

from ws_web_aiohttp.tests.conf.web_secure import Conf as Conf_web

class Conf(Conf_web):
    @classmethod
    def prepare(cls, mode_s, port=None, conf_dir=None, console=False, **kwargs):
        Conf_web.prepare(mode_s, port, **kwargs)
        
        mode = Conf.Mode.from_string(mode_s)
        
        cls.CONF_DIR = conf_dir or '/etc/ws_web_aiohttp/conf/'

        cls.test_key = os.environ.get('WS_WEB_AIOHTTP_TEST_KEY', None)

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

        cls.ws_sheets_server = modconf.import_class('ws_sheets_server.tests.conf.simple', 'Conf', (mode_s,))

        if console:
            cls.log_console()

    @classmethod
    def log_console(cls):
        for l in cls.LOGGING['loggers'].values():
            l['handlers'] = ['console']

