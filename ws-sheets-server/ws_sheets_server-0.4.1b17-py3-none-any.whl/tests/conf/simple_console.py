
from ws_sheets_server.tests.conf.simple import Conf as Conf1

class Conf(Conf1):
    @classmethod
    def prepare(cls, mode, **kwargs):
        Conf1.prepare(mode, **kwargs)

        cls.log_console()



