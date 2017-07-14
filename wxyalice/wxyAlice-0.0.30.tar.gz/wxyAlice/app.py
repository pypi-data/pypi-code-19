from sanic import Sanic


class App(object):
    def __init__(self, cfg):
        self.app = Sanic()
        self.cfg = cfg

    def Ini(self, views):
        def AddView(v):
            self.app.add_route(v[0].as_view(), v[1])

        [AddView(v) for v in views]
        return self

    def Run(self):
        self.app.run(self.cfg['host'], port=self.cfg['port'])
