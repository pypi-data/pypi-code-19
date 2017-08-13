#!/usr/bin/env python3

import argparse
import os
import rollbar
import sys


SCRIPT_LOCATION = os.path.dirname(os.path.realpath(__file__))
CONFIG_LOCATION = os.path.join(SCRIPT_LOCATION, 'logfit_config.json')
ROLLBAR_TOKEN = 'ac917447c181447cbd50e4c6f108e1d2'
ROLLBAR_ENV = 'production'


def main():
    current_path = os.path.dirname(os.path.realpath(__file__))
    root_path = os.path.normpath(os.path.join(current_path, '..'))
    sys.path.append(root_path)
    rollbar.init(ROLLBAR_TOKEN, ROLLBAR_ENV)
    try:
        parse_args(sys.argv[1:])
    except KeyboardInterrupt:
        pass
    except Exception as e:
        rollbar.report_exc_info()
        raise


def parse_args(sys_args):
    from logfit import __version__
    from logfit.client import LogFit
    from logfit.config import Config
    parser = argparse.ArgumentParser(
        description='Read and upload log files to log.fit'
    )
    parser.add_argument(
        'command',
        choices=['start', 'run', 'foreground', 'stop', 'restart', 'status'],
    )
    parser.add_argument(
        '-v', '--version', action='version', version=__version__,
    )
    args = parser.parse_args(sys_args)
    config = Config()
    config.read_config_file(CONFIG_LOCATION)
    log_fit_client = LogFit(
        pidfile="/tmp/logfit.pid",
        config=config,
    )
    command = args.command
    if command == 'start':
        log_fit_client.start()
    elif command in ['run', 'foreground']:
        log_fit_client.run()
    elif command == 'stop':
        log_fit_client.stop()
    elif command == 'restart':
        log_fit_client.restart()
    elif command == 'status':
        log_fit_client.is_running()


if __name__ == '__main__':
    main()
