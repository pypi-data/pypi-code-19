from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import os.path as op

from diraas.application import app


def main():
    parser = argparse.ArgumentParser(
        description='Make directory as a service.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--debug', action='store_true', dest='debug')
    parser.add_argument('--with-threads', action='store_true', dest='with_threads')
    parser.add_argument('--host', dest='host', default='127.0.0.1', help='The interface to bind to.')
    parser.add_argument('--port', dest='port', type=int, default=5100, help='The port to bind to.')
    parser.add_argument('--token', dest='token', help='API access token.', required=True)
    parser.add_argument('root_dir', nargs='?', default='.', help='the directory to serve.')
    args = parser.parse_args()

    app.config.update(dict(
        DEBUG=args.debug,
        ROOT_DIR=op.abspath(args.root_dir),
        ACCESS_TOKEN=args.token,
    ))

    print('Serving {0}'.format(app.config['ROOT_DIR']))
    app.run(host=args.host, port=args.port, threaded=args.with_threads)


if __name__ == '__main__':
    main()
