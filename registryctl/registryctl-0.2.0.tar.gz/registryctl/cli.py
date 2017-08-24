# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging

from cliff import app

from registryctl.common import baseclient,commandmanager

COMMAND_GROUPS = [
    'registryctl.catalog',
]

class RegistryCtlApp(app.App):

    def __init__(self):
        super(RegistryCtlApp, self).__init__(
            description='Docker Registry CLI',
            version='0.2',
            command_manager=commandmanager.CommandManager('registryctl.cli', COMMAND_GROUPS),
            deferred_help=True)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(RegistryCtlApp, self).build_option_parser(description,
                                                            version,
                                                            argparse_kwargs)
        # Common parameters
        parser.add_argument('-u', '--url',
            help='Registry URL',
            default=os.environ.get('REGISTRYCTL_URL', 'http://localhost:5000'))
        parser.add_argument('-l', '--login',
            help='Login for Basic auth',
            default=os.environ.get('REGISTRYCTL_LOGIN', None))
        parser.add_argument('-p', '--password',
            help='Password for Basic auth',
            default=os.environ.get('REGISTRYCTL_PASSWORD', None))
        return parser

    def initialize_app(self, argv):
        auth = None
        if self.options.login and self.options.password:
            auth = (self.options.login,self.options.password)
        url = self.options.url + '/v2'
        self.client = baseclient.BaseClient(url,auth)


def main(argv=sys.argv[1:]):
    app = RegistryCtlApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
