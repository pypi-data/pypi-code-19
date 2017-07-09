
from ws_web_aiohttp.tests.conf.simple_secure import Conf as Conf_simple_secure

class Conf(Conf_simple_secure):
    @classmethod
    def prepare(cls, mode, port=None, conf_dir=None, **kwargs):
        Conf_simple_secure.prepare(mode, port=port, conf_dir=conf_dir, **kwargs)

        cls.log_console()

