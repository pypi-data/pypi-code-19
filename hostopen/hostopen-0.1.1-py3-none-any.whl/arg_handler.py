import argparse
import logging

# Arbitrary number
default_port = 12355

def convert2level(arg):
    """ Convert the 'level' obtained from the command line
    into a useful logging.<LEVEL> value

    Args:
        arg<str>: the string to convert

    Returns:
        logging.LEVEL (which is essentially an int)
            or None
    """
    arg = arg.lower()
    level_dict = {
        'critial': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }

    if arg in level_dict:
        level = level_dict[arg]
    else:
        level = None

    return level

def parse_client(args):
    parser = argparse.ArgumentParser(description='Host Open: Client.')
    parser.add_argument('-p', '--port',
                        help='The port to connect through.',
                        type=int,
                        default=default_port)
    parser.add_argument('-l', '--log', 
                        help='The verbosity of log messages.',
                        type=str,
                        default='warning')
    parser.add_argument('files',
                        help='The files to send.',
                        nargs='*')

    results = parser.parse_args(args)

    level = convert2level(results.log)
    port = results.port
    files = results.files
    
    return level, port, files

def parse_server(args):
    parser = argparse.ArgumentParser(description='Host Open: Server.')
    parser.add_argument('app',
                        help='The program to open files with.',
                        type=str)
    parser.add_argument('-p', '--port',
                        help='The port to connect through.',
                        type=int,
                        default=default_port)
    parser.add_argument('-l', '--log', 
                        help='The verbosity of log messages.',
                        type=str,
                        default='error')

    results = parser.parse_args(args)

    app = results.app
    level = convert2level(results.log)
    port = results.port
    return app, level, port