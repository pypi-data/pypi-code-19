import threading
import queue

from .. import spy
from .. import message

class Routine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.manager = None

    def run(self):
        while True:
            self.queue.get()
            self.send_status()
            self.queue.task_done()

    def send_status(self):
        status = self.get_status()
        payload = {
            'type':'status',
            'status': status
        }
        self.manager.forward('dothat', {'text':status['temp']})
        self.manager.send(message.Message(payload))

    def get_status(self):
        status = {
            'hostname': spy.get_hostname(),
            'local_ip': spy.get_local_ip(),
            'addresses': spy.get_macs(),
            'ssid': spy.get_ssid(),
            'temp': spy.get_temp(),
            'signal_level': spy.get_signal_level(),
            'written_kbytes': spy.get_written_kbytes(),
            'uptime': spy.get_uptime()
        }
        return status
