"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brew.base import Brew
from tornado import gen, ioloop
from pubkeeper.utils.logging import get_logger
from pubkeeper.brew.websocket import WebsocketSettings
from pubkeeper.communication.websocket import WebsocketClientCommunication
from threading import Thread
import ujson as json


class WebsocketPatron():
    def __init__(self, brewer_id, brewer_brew, callback):
        self._brewer_id = brewer_id
        self._brewer_brew = brewer_brew
        self._callback = callback

        self._th = Thread(target=self.run)
        self._th.start()

    def run(self):
        self._ioloop = ioloop.IOLoop()
        self._ioloop.make_current()

        self._running = True

        self._socket = WebsocketClientCommunication({
            'host': self._brewer_brew['hostname'],
            'port': self._brewer_brew['port'],
            'resource': '',
            'secure': self._brewer_brew['secure'],
            'headers': False,
        })
        self._socket.start(on_connected=self.on_connected,
                           on_message=self.on_message)

        self._ioloop.start()
        self._ioloop.close()

    def on_message(self, data):
        self._callback(brewer_id=self._brewer_id,
                       data=data)

    def on_connected(self):
        self._socket.write_message(json.dumps([0, self._brewer_id, None]))

    def stop(self):
        # This is called from outside our thread, and we need this
        # thread to shut it self down on the next iteration
        self._ioloop.add_callback(self._stop)
        self._th.join(5)

    def _stop(self):
        self._socket.write_message(json.dumps([1, self._brewer_id, None]))
        self._connection = None
        self._running = False
        self._socket.close()
        self._ioloop.stop()


class WebsocketBrew(Brew):
    def __init__(self, *args, **kwargs):
        self.logger = get_logger(self.__class__.__name__)
        self.name = 'websocket'
        self._patrons = {}
        self._socket = None

        super().__init__(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        return WebsocketSettings

    def configure(self, context):
        non_casting_types = [type(None), str]
        for setting in WebsocketSettings.keys():
            if context and setting in context:
                _type = type(WebsocketSettings[setting])
                if _type in non_casting_types:
                    WebsocketSettings[setting] = context[setting]
                else:
                    # cast incoming value to known type
                    WebsocketSettings[setting] = _type(context[setting])

    def start(self):
        self.logger.info("Starting websocket brew")

    def stop(self):
        self.logger.info("Stopping websocket brew")
        if self._socket:
            self._socket.close()

        for brewer_id, patron in self._patrons.items():
            patron.stop()

    def create_brewer(self, brewer):
        if self._socket is None:
            self.logger.info("Websocket Brewer Socket Created")
            self._socket = WebsocketClientCommunication({
                'host': WebsocketSettings['ws_host'],
                'port': WebsocketSettings['ws_port'],
                'resource': '',
                'secure': WebsocketSettings['ws_secure'],
                'headers': False,
            })
            self._socket.start(on_message=None)

        details = super().create_brewer(brewer)

        if details is None:
            details = {}

        details.update({
            'hostname': WebsocketSettings['ws_host'],
            'port': WebsocketSettings['ws_port'],
            'secure': WebsocketSettings['ws_secure']
        })

        return details

    @gen.coroutine
    def _send_message(self, packet, topic, data=None):
        yield self._socket.get_connection()
        self._socket.write_message(json.dumps([
            packet,
            topic,
            data
        ]), binary=True)

    def start_brewer(self, brewer_id, topic, patron_id, patron):
        self._send_message(0, brewer_id)

    def stop_brewer(self, brewer_id, topic, patron_id):
        self._send_message(1, brewer_id)

    def start_patron(self, patron_id, topic, brewer_id, brewer_config,
                     brewer_brew, callback):
        if brewer_id in self._patrons:
            if isinstance(self._patrons[brewer_id]._th, Thread) and \
                    self._patrons[brewer_id]._th.is_alive():
                self.logger.warn(
                    "Already an existing thread for {} on {}".format(
                        brewer_id, topic
                    )
                )
                return
            else:
                del(self._patrons[brewer_id])

        self._patrons[brewer_id] = WebsocketPatron(
            brewer_id,
            brewer_brew,
            callback
        )

    def stop_patron(self, patron_id, topic, brewer_id):
        if brewer_id in self._patrons:
            self._patrons[brewer_id].stop()
            del(self._patrons[brewer_id])

    def brew(self, brewer_id, topic, data, patrons):
        self._send_message(2, brewer_id, data)
