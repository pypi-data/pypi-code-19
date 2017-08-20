# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging

from cliff import app
from cliff import commandmanager

from registryctl import client

class RegistryCtl(app.App):

    def __init__(self):
        super(RegistryCtl, self).__init__(
            description='Docker Registry CLI',
            version='0.1',
            command_manager=commandmanager.CommandManager('registryctl.api'),
            deferred_help=True)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(RegistryCtl, self).build_option_parser(description,
                                                            version,
                                                            argparse_kwargs)
        parser.add_argument('-u', '--url',
                            help='Registry URL',
                            default=os.environ.get('REGISTRYCTL_URL', None))
        parser.add_argument('-l', '--login',
                            help='Login for Basic auth',
                            default=os.environ.get('REGISTRYCTL_LOGIN', None))
        parser.add_argument('-p', '--password',
                            help='Password for Basic auth',
                            default=os.environ.get('REGISTRYCTL_PASSWORD', None))
        return parser

    def initialize_app(self, argv):
        if not self.options.url:
            raise Exception("Missing --url argument or REGISTRYCTL_URL env var")
        basic_auth = None
        if self.options.login and self.options.password:
            basic_auth = (self.options.login,self.options.password)
        self.client = client.RegistryCtlClient(url=self.options.url + '/v2', auth=basic_auth)


def main():
    cli = RegistryCtl()
    return cli.run(sys.argv[1:])


if __name__ == '__main__':
    main()
