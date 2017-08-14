import configparser


class Cfg(object):
    def __init__(self,file):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(file)

    def get(self, key):
        sec = self.cfg[key]
        return dict(zip(sec.keys(), sec.values()))
