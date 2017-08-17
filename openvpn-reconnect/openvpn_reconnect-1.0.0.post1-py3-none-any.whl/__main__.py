#!/usr/bin/env python3
# encoding:UTF-8

import os
import sys

from openvpn_reconnect.daemon.daemon_reconnect import DaemonReconnect
from openvpn_reconnect.program.parser import Parser
from openvpn_reconnect.program.reconnect import es_sudo
from openvpn_reconnect.program.statics import Statics


def main():
    if not es_sudo():
        print('Error: El programa debe ser ejecutado como root para funcionar.', file=sys.stderr)
        sys.exit(1)
    parser = Parser()
    os.makedirs(Statics.PID_FOLDER, exist_ok=True)
    daemon = DaemonReconnect(Statics.PID_FILE)
    if parser.args['start']:
        daemon.start()
    elif parser.args['stop']:
        daemon.stop()
    elif parser.args['restart']:
        daemon.restart()


if __name__ == '__main__':
    main()
