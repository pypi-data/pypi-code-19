# NFQ Conductor. A tool for centralizing and visualizing logs.
# Copyright (C) 2017 Guillem Borrell Nogueras
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import zmq
import subprocess
import datetime
import sys
import os
import socket as unix_socket
from uuid import uuid4


def launch(collector, command, host=None, uid=None, echo=False):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(collector)

    if uid is None:
        uid = str(uuid4())

    # Make linters happy
    p = None
    try:
        with subprocess.Popen(command.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True) as p:

            if host:
                host_id = host
            else:
                hostname = unix_socket.gethostname()

                try:
                    host = unix_socket.gethostbyname(hostname)
                except unix_socket.gaierror:
                    host = 'unknown'

                host_id = ' '.join([hostname, host])

            socket.send_json({
                'source': uid,
                'when': datetime.datetime.now().isoformat(),
                'message': '~~~~{{"process": {}, "wrapped": {}, "host": "{}", '
                           '"label": "{}", "command": "{}" }}'.format(
                    p.pid, os.getpid(), host_id, uid, command)
            })
            for line in p.stdout:
                if echo:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                socket.send_json({'source': uid,
                                  'when': datetime.datetime.now().isoformat(),
                                  'message': line})
    except KeyboardInterrupt:
        print('KILLING SUBPROCESS....')
        p.kill()


def run():
    """
    Source of log messages
    """
    epilog = """
Example:\n

$> nfq-runner --command "python echoer.py" --collector tcp://127.0.0.1:5555
"""

    parser = argparse.ArgumentParser(
        description="Run a command and redirect the output to the registry",
        epilog=epilog,
        prog='nfq-runner')
    parser.add_argument('--command',
                        help='Command to be run',
                        type=str,
                        required=True)
    parser.add_argument('--collector',
                        help='Socket address for the collector',
                        type=str,
                        default='tcp://127.0.0.1:5555')
    parser.add_argument('--uid',
                        help='UID for the logged process',
                        type=str,
                        default=str(uuid4()))
    parser.add_argument('--echo',
                        help="Echo logs while running",
                        action='store_true')
    
    parser.add_argument('--host',
                        help="Set the host id",
                        type=str,
                        default=None)

    args = parser.parse_args()

    launch(args.collector, args.command, args.host, args.uid, args.echo)

if __name__ == '__main__':
    run()

