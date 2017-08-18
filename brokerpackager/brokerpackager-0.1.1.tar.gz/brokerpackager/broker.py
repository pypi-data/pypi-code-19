import time
import sys
import json
import stomp
from .installer import Installer


class Message(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)
        self.fields = []
        for field in self.__dict__:
            field_type = type(self.__dict__[field])
            self.fields.append((field, field_type))
            if field_type == dict:
                self.__dict__[field] = Message(json.dumps(self.__dict__[field]))
        self.original_json = j

    def __repr__(self):
        return str(self.get_fields())

    def get_fields(self):
        return dict(self.fields[:-1])

    def get_field_names(self):
        return self.get_fields().keys()

    def get_path(self, *path):
        root = self
        for level in path:
            fields = root.get_field_names()
            if level in fields:
                root = getattr(root, level)
            else:
                print('No level {} in {}'.format(level, ', '.join(path)))
                break
        if type(root) == list:
            return root
        else:
            print("Path need to be a list. Is a {}".format(str(type(root))))
            return []


    def to_json(self):
        return self.original_json

def connect_and_subscribe(conn, destination, selector):
    conn.start()
    conn.connect(wait=True)
    conn.subscribe(
        destination=destination,
        ack="auto",
        id=destination,
        headers = {'selector' : selector})

class BrokerListener(stomp.ConnectionListener):
    def __init__(self, conn, destination, selector, installer_configs):
        self.conn = conn
        self.destination = destination
        self.selector = selector
        self.installer_configs = installer_configs
        self.installer = Installer(installer_configs)

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        message = Message(message)
        print('received a message "%s"' % message.to_json())
        for path in self.installer_configs:
            self.installer_configs[path]['paths'] = message.get_path(*self.installer_configs[path]['json'].split('.'))
        print('paths parsed "%s"' % str(self.installer_configs[path]['paths']))
        self.installer.install(self.installer_configs)
        print('processed message and installed packages')

    def on_disconnected(self):
        print('disconnected')
        connect_and_subscribe(self.conn, self.destination, self.selector)

class BrokerConnector(object):
    def __init__(self, host, port, destination, selector, installer_configs):
        conn = stomp.Connection(
            host_and_ports=[(host, port)],
            reconnect_sleep_initial=10,
            reconnect_sleep_increase=1.618,
            reconnect_sleep_jitter=0.1,
            reconnect_sleep_max=300.0,
            reconnect_attempts_max=((24 * 60 * 60) / 300) * 2,  # Almost two days
            heartbeats=(0, 0)
        )
        conn.set_listener('broker-packager', BrokerListener(conn, destination, selector, installer_configs))
        connect_and_subscribe(conn, destination, selector)
        self.delay()
    
    def delay(self):
        while True:
            time.sleep(100000)