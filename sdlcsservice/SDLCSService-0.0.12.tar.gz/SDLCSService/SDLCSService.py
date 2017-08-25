from . import ServiceManager

from multiprocessing import Pipe
import signal

recv,send = Pipe(False)
def stop(sig,former):
    global send
    send.send('ok')


signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGHUP, stop)

def Main():
    ServiceManager.init()
    print('service is start ...')
    while True:
        value = recv.recv()
        if value == 'ok':
            print('service terminat...')
            ServiceManager.Stop()
            break

if __name__ == '__main__':
    Main()
