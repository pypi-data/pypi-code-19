import json
import logging
import time
import uuid
from typing import Dict, Optional
from urllib.parse import parse_qsl

from django.conf import settings
from geventwebsocket import WebSocketApplication
from ipware.ip import get_ip
from memoize import memoize
from voluptuous import Any

log = logging.getLogger('BaseWebSocketApplication')


class BaseWebSocketApplication(WebSocketApplication):
    clients = {}  # type:Dict[str: BaseWebSocketApplication]

    def __init__(self, ws):
        super(BaseWebSocketApplication, self).__init__(ws)

        self.META = self.ws.environ
        self.query = dict(parse_qsl(self.META.get('QUERY_STRING', '')))
        self.remote_ip = get_ip(self)
        self.guid = "{}|{}".format(self.remote_ip, uuid.uuid4())
        self.last_ping = None

    def on_open(self):
        self.last_ping = time.time()
        self.clients[self.guid] = self

        self.on_connect()
        self.check_zombie_channels()

    def handle_message(self, kind: str, payload: Optional[Any] = None):
        pass

    def on_ping(self):
        pass

    # called by on_open
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def send_message(self, kind: str, payload: Optional[Any] = None):
        obj = {'kind': kind}
        if payload is not None:
            obj['payload'] = payload
        self.write_message(json.dumps(obj))

    # internal =================
    def __repr__(self):
        return '[{}:{}]'.format(self.__class__.__name__, self.guid)

    def write_message(self, message):
        self.ws.send(message)

    def on_message(self, message, *args, **kwargs):
        if self.guid not in self.clients:
            self.close(500, 'connection died')

        self.last_ping = time.time()

        if message is None:
            # 可能来自客户端关闭, client会自动关闭,这里不处理
            return

        elif len(message) == 1:
            self.ws.send('.')  # pong back
            self.on_ping()

        else:
            try:
                obj = json.loads(message)
                kind, payload = map(obj.get, ['kind', 'payload'])
                self.handle_message(kind, payload)
            except Exception as e:
                log.warning('%s <-!(%s) %s', self, e, message)

    def on_close(self, *args, **kwargs):
        if self.guid:
            del self.clients[self.guid]
        self.on_disconnect()

    def close(self, *args, **kwargs):
        self.ws.close(*args, **kwargs)

    @classmethod
    @memoize(settings.CHECK_ZOMBIE_INTERVAL)
    def check_zombie_channels(cls):
        now = time.time()

        kills = 0
        clients = cls.clients.copy()
        for client in clients.values():
            dt = now - client.last_ping
            if dt > settings.CHECK_ZOMBIE_INTERVAL * 2:
                kills += 1
                client.close()
        log.debug('[%s] check ping time: [%s/-%s] @%.2f ms',
                  cls.__name__,
                  len(cls.clients),
                  kills,
                  (time.time() - now) * 1000)
