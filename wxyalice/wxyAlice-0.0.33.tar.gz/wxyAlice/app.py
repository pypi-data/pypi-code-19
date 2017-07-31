from sanic import Sanic
from sanic_cors import CORS


class App(object):
    def __init__(self, cfg):
        self.app = Sanic()
        CORS(self.app)
        self.cfg = cfg

        @self.app.middleware('response')
        async def print_on_response1(request, response):
            print("I print when a response 1 is returned by the server")

        @self.app.middleware('response')
        async def print_on_response2(request, response):
            print("I print when a response 2 is returned by the server")


    def Ini(self, views):
        def AddView(v):
            self.app.add_route(v[0].as_view(), v[1])

        [AddView(v) for v in views]
        return self

    def Run(self):
        self.app.run(self.cfg['host'], port=self.cfg['port'])
