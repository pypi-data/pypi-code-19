from pycube90 import Cube
import socket, os

class CubeSocket:
    def __init__(self, key):
        self.key = key
        self.session_key = ""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def wrap(self, sock):
        self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, buf):
        buf = Cube(self.key).encrypt(buf)
        self.sock.send(buf)

    def recv(self, buf_size):
        buf = self.sock.recv(buf_size)
        buf = Cube(self.key).decrypt(buf)
        return buf

    def close(self):
        self.sock.close()

    def listen(self, num_listeners):
        self.sock.listen(num_listeners)

    def bind(self, host, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))

    def cli_keyexchange(self, sock):
	session_key = self.gen_key(16)
	self.send(session_key)
	self.key = session_key

    def srv_keyexchange(self, client_sock):
	session_key = client_sock.recv(16)
	self.session_key = Cube(self.key).decrypt(session_key)
	self.key = self.session_key

    def accept(self):
        client, addr = self.sock.accept()
	self.srv_keyexchange(client)
        return client, addr

    def gen_key(self, length):
        key = ""
        for x in range(0,length):
            char = chr((os.urandom(1) % (90 - 32 + 1)) + 32)
            key += char
        return key

    def cubeconnect(self, host, port):
        self.connect(host, port)
	self.cli_keyexchange(self.sock)

class CubeWrap:
    def __init__(self, sock, key):
        self.sock = CubeSocket(key)
        self.sock.wrap(sock)
        self.raw_sock = sock
