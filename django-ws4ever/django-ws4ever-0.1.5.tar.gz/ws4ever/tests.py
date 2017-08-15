import json
import time
from functools import partial
from typing import Any, Optional
from unittest.mock import MagicMock, patch, PropertyMock

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
from ws4ever.redis import publish_client_message
from ws4ever.views import BaseWebSocketApplication

User = get_user_model()

# 可用port 万一冲突, 需要修改
LIVE_SERVER_PORT = 8727


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
                gevent.sleep(0)
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
                self.httpd = get_server(settings.SERVER_HOST, settings.SERVER_PORT,
                                        StaticFilesHandler(application))  # todo create application
                gevent.spawn(self.httpd.serve_forever)

            def terminate(self):
                self.httpd.stop(1)

        return MyLiveServerThread()


class TestWebsocketApplication(BaseWebSocketApplication):
    last_message = {}

    def handle_message(self, kind: str, payload: Optional[Any] = None):
        self.last_message = {'kind': kind, 'payload': payload}

    @classmethod
    def on_redis_message(cls, data):
        for client in cls.clients:
            client.send_message(data['kind'], payload=data.get('payload'))


@override_settings(SERVER_HOST="127.0.0.1", SERVER_PORT=8727, WS4EVER={
    'ROUTES': {
        "/ws": "ws4ever.tests.TestWebsocketApplication"
    },
    'MAX_IDLE': 0.2})
class WebSocketClientApplicationTests(MyLiveServerTestCase):
    ws_url = 'ws://{}:{}{}'.format(settings.SERVER_HOST, settings.SERVER_PORT, settings.WEBSOCKET_URL)

    @classmethod
    def connect(cls, url):
        conn = create_connection(url)
        gevent.sleep(0.1)
        return conn

    @classmethod
    def clients(cls):
        return list(TestWebsocketApplication.clients.values())

    def test_send_message_to(self):
        ws = self.connect(self.ws_url)
        payload = {"kind": "hello", "payload": "world"}

        publish_client_message(kind="hello", payload="world")
        self.assertEqual(json.loads(ws.recv()), payload, "得到了message")
        ws.close()

    def test_publish_client_message(self):
        user, token = self.create_user('a@a.com')

        with patch('redis.client.PubSub.psubscribe',
                   new_callable=WaitableMock(redis.client.PubSub.psubscribe)) as mocked_method:
            gevent.spawn(WS4EverConfig.subscribe_redis)
            mocked_method.wait_called()

        with patch('main.websocket.TestWebsocketApplication.send_message_to') as send_message_to:
            publish_client_message(msg='a', user_ids=[user.pk])
            WaitableMock.wait_called(send_message_to)
            self.assertEqual(send_message_to.call_args, (('a', None), {'user_id': user.pk}),
                             'redis publish_client_message 根据user_id发送')

        with patch('main.websocket.TestWebsocketApplication.send_message_to') as send_message_to:
            publish_client_message(msg='b')
            WaitableMock.wait_called(send_message_to)
            self.assertEqual(send_message_to.call_args, (('b', None), {}),
                             'redis publish_client_message 广播')

    def test_kill_zombies(self):
        class FakeClient:
            def __init__(self):
                self.last_ping = 0
                self.close = MagicMock()

        client_zombie = FakeClient()

        client_pinged = FakeClient()
        client_pinged.last_ping = time.time()

        fake_clients = {1: client_pinged, 2: client_zombie}

        with patch('main.websocket.TestWebsocketApplication.clients',
                   new_callable=PropertyMock, return_value=fake_clients):
            TestWebsocketApplication.kill_zombies.delete_memoized()
            TestWebsocketApplication.kill_zombies()
            client_pinged.close.assert_not_called()
            client_zombie.close.assert_called_with()
