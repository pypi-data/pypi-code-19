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
            self.authenticate()
            self.queue.task_done()

    def authenticate(self):
        payload = {
            'type':'auth',
            'serial': spy.get_serial(),
            'machine_id': spy.get_machine_id(),
        }
        self.manager.send(message.Message(payload))
