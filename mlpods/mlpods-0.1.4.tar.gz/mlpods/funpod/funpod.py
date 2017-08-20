import socket
import json
#  import cPickle
import tempfile
import docker


class FunPod(object):
    """ Functional pod that is called on-demand """
    def __init__(self, name):
        self.name = name
        self.docker_client = docker.from_env()
        self.container = None
        self.fpc = FunPodConnector()

    def build(self, func):
        """TODO: build image given handle function """
        pass

    def spinup(self):
        self.container = self.docker_client.containers.run(
                        self.name,
                        detach=True,
                        ports={'9998': '9998'})

    def kill(self):
        if self.container:
            try:
                print self.container.status
                self.container.kill()
            except Exception as e:
                print e


class FunPodConnector(object):

    def __init__(self, ip='0.0.0.0', port=9998):
        self.ip = ip
        self.port = port

    def handle(self, func):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)

        conn, addr = self.sock.accept()
        print('handle request received')
        buf = self.recv(conn=conn)

        kwargs = json.loads(buf)
        gen = func(**kwargs)
        for i in gen:
            try:
                conn, addr = self.sock.accept()
                conn.send(str(i))
                conn.shutdown(socket.SHUT_WR)
            finally:
                conn.close()

        try:
            conn, addr = self.sock.accept()
            conn.send('EOF')
            conn.shutdown(socket.SHUT_WR)
        finally:
            conn.close()

    def handle_file(self, func):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)

        conn, addr = self.sock.accept()
        print('handle request received')
        f = self.recv_file(conn=conn)

        gen = func(f)
        for i in gen:
            try:
                conn, addr = self.sock.accept()
                conn.send(str(i))
                conn.shutdown(socket.SHUT_WR)
            finally:
                conn.close()

        try:
            conn, addr = self.sock.accept()
            conn.send('EOF')
            conn.shutdown(socket.SHUT_WR)
        finally:
            conn.close()

    def serve_recv_file(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)

        conn, addr = self.sock.accept()
        print('handle request received')
        f = self.recv_file(conn=conn)
        return f

    def send(self, data_send):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            #  self.sock.sendall(json.dumps(data_send).encode('utf-8'))
            self.sock.sendall(data_send)
            self.sock.shutdown(socket.SHUT_WR)
            buf = ''
            data = True
            while data:
                data = self.sock.recv(2048)
                buf += data
                #  return json.loads(unicode(buf, 'utf-8'))
        finally:
            self.sock.close()

    def recv(self, conn=None):
        try:
            if not conn:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.ip, self.port))
                #  self.sock.sendall(json.dumps(data_send).encode('utf-8'))
                conn = self.sock

            buf = ''
            data = True
            while data:
                data = conn.recv(2048)
                buf += data
            return buf
        finally:
            conn.close()

    def recv_file(self, conn=None):
        try:
            if not conn:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.ip, self.port))
                #  self.sock.sendall(json.dumps(data_send).encode('utf-8'))
                conn = self.sock

            f = tempfile.TemporaryFile()
            data = True
            while data:
                data = conn.recv(2048)
                f.write(data)
            f.seek(0)
            return f

        finally:
            conn.close()

    def serve_generator(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)

        while True:
            conn, addr = self.sock.accept()
            print('client connected')
            try:
                data = True
                buf = ''
                while data:
                    data = conn.recv(4096)
                    buf += data

                # echo back
                conn.sendall(buf)
                conn.shutdown(socket.SHUT_WR)

                #  return json.loads(unicode(buf, 'utf-8'))
                if buf == u'EOF':
                    return
                yield buf

            finally:
                conn.close()

    def client_generator(self, fileobj=False, **kwargs):
        if not fileobj:
            self.send(json.dumps(kwargs))
        else:
            self.send(fileobj.read())
        while True:
            recv = self.recv()
            if recv == 'EOF':
                break
            yield recv


def main_test():
    def makelist(n):
        for i in xrange(int(n)):
            yield i

    connect = FunPodConnector()
    connect.handle(makelist)


if __name__ == '__main__':
    main_test()
