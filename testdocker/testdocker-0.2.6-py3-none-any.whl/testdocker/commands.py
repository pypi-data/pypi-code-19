"""
testdocker.commands
~~~~~~~~~~~~~~~~~~~

Commands classes for docker testing.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import json

from . import util


class CommandBase:
    cmd = ''
    def __repr__(self):
        return self.cmd


class CurlCommand(CommandBase):
    defaults = dict(
        options=dict(
            silent=True,
            fail=True,
            location=True
        )
    )
    def __init__(self, url, method='GET', headers=None, data=None, file=None,
                 options=None):
        headers = headers or {}
        data = data or {}
        options = util.set_defaults(options or {}, self.defaults['options'])

        cmd = ['curl']
        cmd.append(self._build_args(options))
        if method != 'GET':
            cmd.append('-X %s' % method.upper())
        if data:
            if isinstance(data, dict):
                data = json.dumps(data)
            cmd.append("--data '%s'" % data)
        if file:
            if not os.path.isfile(file):
                raise FileNotFoundError(file)
            cmd.append("--data-binary @%s" % file)
            headers['Content-type'] = util.get_content_type(file)
        if headers:
            for key, val in headers.items():
                cmd.append("-H '%s: %s'" % (key, val))
        cmd.append(url)
        self.cmd = ' '.join(cmd)

    @staticmethod
    def _build_args(options):
        args = []
        if options.get('silent'):
            args.append('-s')
        if options.get('fail'):
            args.append('-f')
        if options.get('location'):
            args.append('-L')
        return ' '.join(args)


class NetCatCommand(CommandBase):
    def __init__(self, host, port, udp=False):
        cmd = ['nc', '-z', host, str(port)]
        if udp:
            cmd.append('-u')
        self.cmd = ' '.join(cmd)


class CatCommand(CommandBase):
    def __init__(self, path):
        cmd = ['cat', path]
        self.cmd = ' '.join(cmd)
