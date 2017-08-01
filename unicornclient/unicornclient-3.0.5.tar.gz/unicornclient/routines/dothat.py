import threading
import queue

from .. import hat

class Routine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.hat = hat.Microdot()
        self.queue = queue.Queue()

    def run(self):
        while True:
            data = self.queue.get()
            text = data['text'] if 'text' in data else None

            if text:
                self.hat.clear()
                self.hat.write_string(str(text))
                self.hat.show()

            self.queue.task_done()
