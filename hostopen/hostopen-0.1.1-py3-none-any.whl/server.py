import logging
import socket
import subprocess
import sys

from hostopen import utils
from hostopen.arg_handler import parse_server

def open_all(filepaths, app):
    """ Open all files with the specified application
    """
    logger.debug('Opening files with \'%s\''% app)
    for file in filepaths:
        logger.debug('  %s' % file)
        subprocess.Popen([app, file])

def listen(port, app):
    """ Listen to the specified port and open files that are sent through
    
    A try-block is placed around everything to catch KeybordInterrupt,
        which will allow to program to exit gracefully upon Ctrl+C

    Args:
        port <int>: the port to listen to
        app <str>: the application to open the files with
    """
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('localhost', port))
        # 5 simultaenous connections. Arbitrary number.
        serversocket.listen(5)
        logger.debug('Listening.')

        while True:
            connection, address = serversocket.accept()
            data = connection.recv(4096)
            if len(data) > 0:
                filepaths = utils.unpack_data(data)
                logger.debug('Filepaths: %s', filepaths)
                open_all(filepaths, app)
    except OSError as e:
        logger.error(e)
    except KeyboardInterrupt:
        print() # So ^C is on a different line
        logger.info('Keyboard Interrupt, exiting.')
        serversocket.close()

def main():
    global logger
    app, level, port = parse_server(sys.argv[1:])

    utils.init_logger(level)
    logger = logging.getLogger(__name__)

    listen(port, app)

if __name__ == '__main__':
    main()
