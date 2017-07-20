#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import asyncio
from concurrent import futures
from ..bcommon import default
from .server import BubbleProtocol


def main():
    port = default.DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    loop = asyncio.get_event_loop()
    coro = loop.create_server(BubbleProtocol, '0.0.0.0', port)
    server = loop.run_until_complete(coro)
    print('Bubble server integrator, (c) Vadim Dyadkin, ESRF, inspired by Giuseppe Portale')
    print('!*!*!*! IT IS IMPORTANT !*!*!*!*!')
    print('If the client does not run on windows, please install this:')
    print('https://www.microsoft.com/en-us/download/details.aspx?id=48145')
    print('!*!*!*! IT IS IMPORTANT !*!*!*!*!')
    print('If you use this program, please cite this paper: http://dx.doi.org/10.1107/S1600577516002411')
    print('Mercurial repository: http://hg.3lp.cx/bubble')
    print('Mercurial hash: {}'.format(default.get_hg_hash()))
    print('Serving on {}:{:d}'.format(*server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Ctrl-C has been pressed. Exit and clean up...')
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
