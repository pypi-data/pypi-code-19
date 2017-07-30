import socket


class Rprint:
    name = 'user'
    host = '127.0.0.1'
    port = 10000
    ver = '0.0.8'
    dbg = False


def config(name='user', host='localhost', port=10000):
    Rprint.name = name
    Rprint.host = host
    Rprint.port = port
    print(Rprint.name, Rprint.host, Rprint.port)


def send(message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (Rprint.host, Rprint.port)
        sock.sendto(message.encode('utf-8'), server_address)
    finally:
        sock.close()
        if Rprint.dbg:
            print(message)


def send_from(message):
    send("{}:{}".format(Rprint.name, message))


def version():
    return Rprint.ver


def debug(change=None):
    if change:
        Rprint.dbg = change
    return Rprint.dbg


def server(host='localhost', port=10000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (Rprint.host, Rprint.port)
    sock.bind(server_address)

    print('Server udp listen')

    while True:
        data, address = sock.recvfrom(4096)
        print(address[0], ':', data.decode('utf-8'))


def help():
    info = """
server example:
    (case 1)
        import rprint
        rprint.server()

    (case 2)
        import rprint
        rprint.server(host='xxx.xxx.xxx.xxx', port=nnnn)

client example:
    (case 1)
        import rprint
        rprint.send('ops')
    (case 2)
        import rprint
        rprint.config(name, host='xxx.xxx.xxx.xxx', port=nnnn):
        rprint.send('ops')
"""

    print(info)
