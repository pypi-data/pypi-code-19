# Copyright (c) 2017 XLAB d.o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fcoclient import utils
from fcoclient.client import Client
from fcoclient.commands.base import Command
from fcoclient.config import Config


class ConfigureCmd(Command):

    require_client = False

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser("configure", help="Configure client")
        parser.add_argument("-a", "--url", help="FCO URL")
        parser.add_argument("-u", "--username", help="FCO username")
        parser.add_argument("-c", "--customer", help="FCO customer")
        return parser

    def configure(self, args):
        self.logger.info("Configuring client")

        url = args.url if args.url else utils.prompt("FCO URL")
        username = (
            args.username if args.username else utils.prompt("FCO username")
        )
        customer = (
            args.customer if args.customer else utils.prompt("FCO customer")
        )
        password = utils.prompt("FCO password", is_password=True)
        config = Config(url=url, username=username, customer=customer,
                        password=password)

        self.logger.info("Testing client configuration")
        Client(**config).vdc.list()

        config.save(args.config)
        self.logger.info("Client configured")
