import datetime
import functools
import json
import random
import string

from tornado import testing
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop


class Base(testing.AsyncHTTPTestCase):

    def get_new_ioloop(self):
        self._io_loop = AsyncIOMainLoop()
        return self._io_loop

    def get_app(self):
        app = self.get_flasky_app()
        app.build_app()

        for on_start_func in app.on_start_funcs:
            IOLoop.current().run_sync(functools.partial(on_start_func, app))

        return app.app

    def get_flasky_app(self):
        raise NotImplemented

    def load_body(self, response):
        return json.loads(response.body.decode("utf-8"))

    def generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def parse_datetime(self, value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")