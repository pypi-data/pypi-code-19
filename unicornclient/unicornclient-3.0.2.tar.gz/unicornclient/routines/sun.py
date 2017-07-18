import threading
import queue

class Routine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()

    def run(self):
        while True:
            self.queue.get()
            self.queue.task_done()
