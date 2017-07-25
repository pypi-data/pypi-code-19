import threading
import queue

from .. import message

class Routine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.last_ping_id = None
        self.manager = None

    def run(self):
        while True:
            data = self.queue.get()

            ping_id = data['id'] if 'id' in data else None
            if ping_id:
                self.last_ping_id = ping_id
                payload = {'type': 'pong', 'id': ping_id}
                self.manager.send(message.Message(payload))

            self.queue.task_done()
