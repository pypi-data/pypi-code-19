import argparse


def get_parser():
    parser = argparse.ArgumentParser(description='Easy email sending')

    parser.add_argument(
        '--config', '-c',
        default='~/.postino')

    parser.add_argument(
        '--no-config',
        action='store_true',
        help='do not use a config file')

    parser.add_argument(
        '--to',
        action='append',
        help='add recipient')

    parser.add_argument(
        '--cc',
        action='append',
        help='add CC recipient')

    parser.add_argument(
        '--bcc',
        action='append',
        help='add BCC recipient')

    parser.add_argument(
        '--subject',
        help='set subject')

    parser.add_argument(
        '--body',
        type=argparse.FileType('r'),
        default=sys.stdin)

    parser.add_argument(
        '--html',
        type=argparse.FileType('r'))

    parser.add_argument(
        '--host',
        default='localhost',
        help='SMTP host to connect to')

    parser.add_argument(
        '--port',
        type=int,
        default=25,
        help='SMTP port')

    parser.add_argument(
        '--mode',
        choices=['normal', 'ssl', 'tls'],
        default='normal',
        help='SMTP connection mode')

    parser.add_argument(
        '--from',
        default=None,
        help='SMTP connection mode')

    parser.add_argument(
        '--login',
        help='SMTP user name')

    parser.add_argument(
        '--password',
        help='SMTP password')

    return parser
