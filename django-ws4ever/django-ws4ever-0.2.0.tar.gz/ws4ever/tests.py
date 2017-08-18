import ujson as json
import time
from functools import partial
from typing import Any, Optional
from unittest.mock import MagicMock, PropertyMock, patch

import gevent
import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.test import LiveServerTestCase, override_settings
from websocket import create_connection

from django_ws4ever.wsgi import application
from ws4ever.apps import WS4EverConfig
from ws4ever.management.commands.runserver import get_server
from ws4ever.redis import notify_clients
from ws4ever.views import BaseWebSocketApplication

User = get_user_model()
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8727


class WaitableMock:
    def __init__(self, func):
        self.func = func

    def __call__(self):
        def make_func(*args, **kwargs):
            ret = self.func(*args, **kwargs)
            make_func.called = True
            return ret

        make_func.wait_called = partial(self.wait_called, make_func)

        return make_func

    @classmethod
    def wait_called(cls, func, timeout=5):
        exception = Exception('{} timeout'.format(func))
        with gevent.Timeout(timeout, exception):
            while not getattr(func, 'called', False):
                gevent.sleep()
        return True


class MyLiveServerTestCase(LiveServerTestCase):
    @classmethod
    def _create_server_thread(cls, connections_override):
        class MyLiveServerThread(object):
            is_ready = MagicMock()
            is_ready.wait = MagicMock()
            join = MagicMock()
            error = None
            httpd = None

            def start(self):
                self.httpd = get_server(SERVER_HOST, SERVER_PORT,
                                        StaticFilesHandler(application))
                gevent.spawn(self.httpd.serve_forever)

            def terminate(self):
                self.httpd.stop(1)

        return MyLiveServerThread()


class TestWebsocketApplication(BaseWebSocketApplication):
    def handle_message(self, kind: str, payload: Optional[Any] = None):
        self.send_message(kind, payload)

    @classmethod
    def on_notify(cls, kind, payload, **extra):
        for client in cls.clients.values():
            client.send_message(kind, payload=payload)


@override_settings(WS4EVER={
    'ROUTES': {
        "/ws": "ws4ever.tests.TestWebsocketApplication"
    },
    'MAX_IDLE': 0.2,
    'BROADCAST_BACKEND': 'redis://127.0.0.1:6379'
})
class WebSocketClientApplicationTests(MyLiveServerTestCase):
    @classmethod
    def connect(cls):
        ws_url = 'ws://{}:{}{}'.format(SERVER_HOST, SERVER_PORT,
                                       list(settings.WS4EVER['ROUTES'].keys())[0])
        conn = create_connection(ws_url)
        gevent.sleep(0.1)
        return conn

    @classmethod
    def clients(cls):
        return list(TestWebsocketApplication.clients.values())

    def test_send_message_to(self):
        ws = self.connect()
        payload = {"kind": "hello", "payload": "world"}

        ws.send(json.dumps({"kind": "hello", "payload": "world"}))
        self.assertEqual(json.loads(ws.recv()), payload, "得到了message")
        ws.close()

    def test_publish_client_message(self):
        with patch('redis.client.PubSub.psubscribe',
                   new_callable=WaitableMock(redis.client.PubSub.psubscribe)) as mocked_method:
            gevent.spawn(WS4EverConfig.subscribe_redis)
            mocked_method.wait_called()

        ws = self.connect()
        data = {"kind": "hello", "payload": "world"}

        notify_clients("hello", "world", a='b')
        self.assertEqual(json.loads(ws.recv()), data, "得到了message")
        ws.close()

    def test_kill_zombies(self):
        class FakeClient:
            def __init__(self):
                self.last_ping = 0
                self.close = MagicMock()

        client_zombie = FakeClient()

        client_pinged = FakeClient()
        client_pinged.last_ping = time.time()

        fake_clients = {1: client_pinged, 2: client_zombie}

        with patch('ws4ever.tests.TestWebsocketApplication.clients',
                   new_callable=PropertyMock, return_value=fake_clients):
            TestWebsocketApplication.check_zombie_clients.delete_memoized()
            TestWebsocketApplication.check_zombie_clients()
            client_pinged.close.assert_not_called()
            client_zombie.close.assert_called_with()
