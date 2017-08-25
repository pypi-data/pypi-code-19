from SDLCSCore.ServiceManager import ServiceManager

from multiprocessing import Pipe
import signal

recv,send = Pipe(False)
def stop(sig,former):
    global send
    print('send terminat')
    print(sig,former)
    send.send('ok')


signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGHUP, stop)

def Main():
    ServiceManager.init()
    while True:
        value = recv.recv()
        if value == 'ok':
            ServiceManager.Stop()
            break

if __name__ == '__main__':
    Main()
