#!/usr/bin/env python3

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Read and upload log files to log.fit'
    )
    parser.add_argument(
        'command',
        choices=['start', 'run', 'foreground', 'stop', 'restart', 'status'],
    )
    args = parser.parse_args()
    log_fit_client = LogFit("/tmp/logfit.pid")
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
    main()
