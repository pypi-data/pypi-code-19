from sanic import Sanic
from sanic.response import json


class App(object):
    def __init__(self, cfg):
        self.app = Sanic()
        self.cfg = cfg

        @self.app.middleware('response')
        async def cors_on_response(request, response):
            response.headers['access-control-allow-origin'] = '*'
            response.headers['access-control-allow-methods'] = '*'
            response.headers['access-control-allow-headers'] = 'content-type'
            response.headers['access-control-allow-credentials'] = 'true'

        @self.app.middleware('request')
        async def cors_on_request(request):
            if request.method == 'OPTIONS':
                return json({})

    def Ini(self, views):
        def AddView(v):
            self.app.add_route(v[0].as_view(), v[1])

        [AddView(v) for v in views]
        return self

    def Run(self):
        self.app.run(self.cfg['host'], port=self.cfg['port'])
