class SharedFile(object):

    __slots__ = ('pos', 'buffer', 'filename', 'conn', 'lock')

    def __init__(self, filename, conn, lock, mode='r'):
        self.pos = 0
        self.buffer = b''

        self.filename = filename
        self.conn = conn
        self.lock = lock

        with lock:
            self.conn.send(('open', {
                'filename': filename,
                'mode': mode
            }))
            self.conn.recv()

    def __iter__(self):
        return self

    def __next__(self):
        index = self.buffer.find(b'\n', self.pos)
        if index == -1:
            buffers = [self.buffer[self.pos:]]
            self.pos = 0
            pos = 0
            while index == -1:
                pos += len(buffers[-1])
                with self.lock:
                    self.conn.send(('read', {
                        'filename': self.filename
                    }))
                    buffer = self.conn.recv()
                if buffer == b'':
                    if buffers[-1] == b'':
                        return
                    buffer = self.buffer
                    self.buffer = b''
                    return buffer
                index = buffer.find(b'\n')
                buffers.append(buffer)
            index += pos
            self.buffer = b''.join(buffers)
        pos = self.pos
        self.pos = index + 1
        return self.buffer[pos:index + 1]

    def read(self, bytes=2 ** 16):
        with self.lock:
            self.conn.send(('read', {
                'filename': self.filename,
                'bytes': bytes
            }))
            buffer = self.conn.recv()
        return buffer

    def readline(self, bytes=0):
        with self.lock:
            self.conn.send(('readline', {
                'filename': self.filename,
                'bytes': bytes
            }))
            buffer = self.conn.recv()
        return buffer

    def write(self, bytes):
        with self.lock:
            self.conn.send(('write', {
                'filename': self.filename,
                'bytes': bytes
            }))
            buffer = self.conn.recv()
        return buffer

    def close(self):
        with self.lock:
            self.conn.send(('close', {
                'filename': self.filename
            }))
            buffer = self.conn.recv()
        return buffer

    def __getstate__(self):
        return self.pos, self.buffer, self.filename, self.conn, self.lock

    def __setstate__(self, state):
        self.pos, self.buffer, self.filename, self.conn, self.lock = state
