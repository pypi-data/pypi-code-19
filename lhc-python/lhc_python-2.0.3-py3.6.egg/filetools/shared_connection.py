class SharedConnection(object):
    def __init__(self, connection, lock):
        self.connection = connection
        self.lock = lock

    def send(self, data):
        self.lock.acquire()
        self.connection.send(data)
        self.lock.release()

    def recv(self):
        self.lock.acquire()
        data = self.connection.recv()
        self.lock.release()
        return data

    def __getstate__(self):
        return self.connection, self.lock

    def __setstate__(self, state):
        self.connection, self.lock = state
