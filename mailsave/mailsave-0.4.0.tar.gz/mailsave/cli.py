#!/usr/bin/env python3

import argparse
import asyncore
import sys

from mailsave import save
from mailsave.smtp import MailSaveServer
from io import StringIO


def main():
    parser = argparse.ArgumentParser(
        description='Dump mails into files. Can be used as a '
                    'replacement for sendmail or an SMTP server'
    )
    parser.add_argument(
        '--dir',
        default='.',
        help='Directory in which to save the mails.',
    )
    parser.add_argument(
        '--filename',
        default=None,
        help='Directory in which to save the mails. If not given, it will use the date '
             'like 2017-07-07_14-78-00.mbox',
    )
    parser.add_argument(
        '--server',
        action='store_true',
        default=False,
        help='Listen on a TPC socket for mails.',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=2525,
        help='Port on which to listen. For server mode.',
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host on which to listen. For server mode. Can be a hostnane like localhost '
             'or an ip address',
    )
    args, _ = parser.parse_known_args()
    if args.server:
        read_server(args)
    else:
        read_stdin(args)


def read_server(args):
    server = MailSaveServer(args.host, args.port, args.dir, filename=args.filename)  # noqa
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print('Quitting')


def read_stdin(args):
    content = StringIO()
    for line in iter(sys.stdin.readline, ''):
        content.write(line)

    save(content.getvalue(), folder=args.dir, filename=args.filename)


if __name__ == '__main__':
    main()
