#!/usr/bin/env python3

import os
import sys


def main():
    if len(sys.argv) < 2:
        command = ""
    else:
        command = sys.argv[1]
        log_fit_client = LogFit("/tmp/logfit.pid")
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
    else:
        print("Unknown command")
        print("Allowed commands: start, run/foreground, stop, restart, status")


if __name__ == '__main__':
    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(current_path, '..'))
    from logfit.client import LogFit
    main()
