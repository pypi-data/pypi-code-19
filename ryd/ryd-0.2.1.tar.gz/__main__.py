# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import sys
import os                 # NOQA

from ruamel.std.argparse import ProgramBase, option, CountAction, \
    SmartFormatter, sub_parser, version
from ruamel.appconfig import AppConfig
from . import __version__, _package_data
from .ryd import RYD


def to_stdout(*args):
    sys.stdout.write(' '.join(args))


class RYDCmd(ProgramBase):
    def __init__(self):
        super(RYDCmd, self).__init__(
            formatter_class=SmartFormatter,
            # aliases=True,
            # usage="""""",
            full_package_name=_package_data['full_package_name'],
        )

    # you can put these on __init__, but subclassing RYDCmd
    # will cause that to break
    @option('--verbose', '-v',
            help='increase verbosity level', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @option('--force',
            help='force action, even on normally skipped files', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        self.ryd = RYD(self._args, self._config)
        if hasattr(self._args, 'func'):  # not there if subparser selected
            return self._args.func()
        self._parse_args(['--help'])     # replace if you use not subparsers

    def parse_args(self, args=None):
        self._config = AppConfig(
            'ryd',
            filename=AppConfig.check,
            parser=self._parser,  # sets --config option
            warning=to_stdout,
            add_save=False,  # add a --save-defaults (to config) option
        )
        # self._config._file_name can be handed to objects that need
        # to get other information from the configuration directory
        self._config.set_defaults()
        self._parse_args(
            args=args,
            default_sub_parser="convert",
        )

    @sub_parser(help='generate output as per first YAML document')
    # @option('--session-name', default='abc')
    @option('file', nargs='+', help='files to process')
    def convert(self):
        self.ryd.convert()

    @sub_parser('from-rst', aliases=['fromrst'], help='convert .rst to .ryd')
    # @option('--session-name', default='abc')
    @option('file', nargs='+', help='files to process')
    def from_rst(self):
        self.ryd.from_rst()


def main():
    n = RYDCmd()
    n.parse_args()
    sys.exit(n.run())


if __name__ == '__main__':
    main()
