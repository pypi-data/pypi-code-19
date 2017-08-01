import threading
import logging

class Sender(object):
    def __init__(self):
        self.socket = None
        self.lock = threading.Lock()

    def send(self, message):
        if not self.socket:
            return

        with self.lock:
            try:
                self.socket.sendall(message.encode())
            except OSError as err:
                logging.error(err)
