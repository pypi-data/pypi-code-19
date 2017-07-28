import socket
import json
import attr
import uuid
import threading

tls = threading.local()
tls.trace_id = None
tls.current_trace = None


def set_current_trace(trace):
    tls.current_trace = trace


def get_current_trace():
    return getattr(tls, 'current_trace', None)


class Connection:

    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def serialize(self, msg):
        data = '\n'.join([
            json.dumps({'format': 'json', 'version': 1}),
            json.dumps(msg.serialize())
        ])
        return data.encode('utf-8')

    def send(self, record):
        if not record.trace_id:
            return

        data = self.serialize(record)
        self._socket.sendto(data, ('127.0.0.1', 2000))


connection = Connection()
