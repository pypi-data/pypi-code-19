import gzip

from multiprocessing import Pipe, Process
from .shared_file import SharedFile


class SharedFilePool(object):

    def __init__(self, lock, chunk_size=2 ** 16):
        with_master, with_slave = Pipe()
        self.files = SharedFilePoolStore(with_slave, lock)
        self.process = Process(target=shared_file_worker, args=(with_master, lock, chunk_size))
        self.process.start()

    def join(self):
        self.files.close()
        self.process.join()

    def terminate(self):
        self.process.terminate()

    def get_file_manager(self):
        return self.files

    def __getstate__(self):
        raise ValueError('use "get_file_manager" to get the picklable communication object')


class SharedFilePoolStore(object):

    __slots__ = ('files', 'conn', 'lock')

    def __init__(self, conn, lock):
        self.files = []
        self.conn = conn
        self.lock = lock

    def open(self, filename, mode='r'):
        res = SharedFile(filename, self.conn, self.lock, mode)
        self.files.append(res)
        return res

    def read(self, filename, bytes=2 ** 16):
        return self.files[filename].read(bytes)

    def write(self, filename, bytes):
        return self.files[filename].write(bytes)

    def close(self, filename=None):
        if filename is None:
            for file in self.files:
                file.close()
        else:
            self.files[filename].close()
        with self.lock:
            self.conn.send(('stop', None))

    def __getstate__(self):
        return self.files, self.conn, self.lock

    def __setstate__(self, state):
        self.files, self.conn, self.lock = state


def shared_file_worker(conn, lock, chunk_size=2 ** 16):
    try:
        files = {}
        while True:
            with lock:
                message, args = conn.recv()
            if message == 'stop':
                break

            filename = args['filename']
            if message == 'open':
                mode = args['mode']
                files[filename] = gzip.open(filename, mode) if filename.endswith('.gz') else open(filename, mode, encoding='utf-8')
                with lock:
                    conn.send('opened')
            elif message == 'read':
                bytes = args['bytes'] if 'bytes' in args else chunk_size
                with lock:
                    conn.send(files[filename].read(bytes))
            elif message == 'readline':
                bytes = args['bytes']
                with lock:
                    conn.send(files[filename].readline(bytes))
            elif message == 'write':
                bytes = args['bytes']
                files[filename].write(bytes)
                with lock:
                    conn.send('written')
            elif message == 'close':
                files[filename].close()
                with lock:
                    conn.send('closed')
            else:
                error = 'unknown command {}'.format(message)
                with lock:
                    conn.send(error)
                raise ValueError(error)
    except Exception as e:
        import sys
        sys.stderr.write(str(e))
        with lock:
            conn.send(str(e))
