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
    parser = argparse.ArgumentParser(
        description='Read and upload log files to log.fit'
    )
    parser.add_argument(
        'command',
        choices=['start', 'run', 'foreground', 'stop', 'restart', 'status'],
    )
    args = parser.parse_args()
    log_fit_client = LogFit("/tmp/logfit.pid", Config(CONFIG_LOCATION))
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
    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(current_path, '..'))
    from logfit.client import LogFit
    from logfit.config import Config
    rollbar.init(ROLLBAR_TOKEN, ROLLBAR_ENV)
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        rollbar.report_exc_info()
        raise
