import logging
from datetime import datetime

from ws4ever.views import BaseWebSocketApplication

log = logging.getLogger('WebSocketClientApplication')


class WebSocketClientApplication(BaseWebSocketApplication):
    def __init__(self, ws):
        meta = ws.environ
        log.info('%s - - [%s] "%s %s %s"',
                 meta.get("REMOTE_ADDR") or meta.get("HTTP_X_FORWARDED_FOR") or meta.get("HTTP_X_REAL_IP"),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 meta.get('REQUEST_METHOD'),
                 meta.get('PATH_INFO'),
                 meta.get('SERVER_PROTOCOL'))

        super(WebSocketClientApplication, self).__init__(ws)

    def on_ping(self):
        log.debug('on ping')

    def handle_message(self, kind, payload=None):
        log.debug('got message kind:%s, payload:%s', kind, payload)
        self.send_message(kind, payload)

    def on_connect(self):
        log.debug('%s ... on connect', self)
        # import time
        # while True:
        #     time.sleep(1)

    def on_disconnect(self):
        log.debug('%s ... on disconnect', self)

    @classmethod
    def on_redis_message(cls, kind, payload, **extra):
        log.debug('[sub] <-- %s', payload)
