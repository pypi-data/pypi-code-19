import socket


class Rprint:
    me = None

    @staticmethod
    def start():
        Rprint.me = Rprint()

    def __init__(self, host='localhost', port=10000):
        if not Rprint.me:
            self.name = 'user'
            self.host = host
            self.port = port
            self.version = '0.0.7'

    @staticmethod
    def config(name='user', host='localhost', port=10000):
        Rprint.me.name = name
        Rprint.me.host = host
        Rprint.me.port = port

    @staticmethod
    def send(message):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = (Rprint.me.host, Rprint.me.port)
            sock.sendto(message.encode('utf-8'), server_address)
        finally:
            sock.close()

    @staticmethod
    def send_from(message):
        Rprint.send("{}:{}".format(Rprint.me.name,message))

    @staticmethod
    def version():
        return Rprint.me.version

    @staticmethod
    def server(host='localhost', port=10000):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = (host, port)
        sock.bind(server_address)

        print('Server udp listen')

        while True:
            data, address = sock.recvfrom(4096)
            print(address[0], ':', data.decode('utf-8'))

    @staticmethod
    def help():
    
        info = """
server example:
    (case 1)
        from rprint.rprint import Rprint
        Rprint.server()

    (case 2)
        from rprint import Rprint
        Rprint.server(host='xxx.xxx.xxx.xxx', port=nnnn)
    
client example:
    (case 1)
        from rprint.rprint import Rprint
        Rprint.send('ops')
    (case 2)
        from rprint import Rprint
        Rprint.config(name, host='xxx.xxx.xxx.xxx', port=nnnn):
        Rprint.send('ops')
            """

        print(info)

Rprint.start()

if __name__ == "__main__":

    print(Rprint.version())
    Rprint.send('ops')



