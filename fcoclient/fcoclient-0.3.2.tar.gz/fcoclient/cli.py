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

from __future__ import print_function

import argparse
import inspect
import logging
import sys

from requests.exceptions import RequestException

from fcoclient import commands
from fcoclient.client import Client
from fcoclient.config import Config
from fcoclient.exceptions import InvalidConfigError, FCOError


def _configure_logging():
    fmt_stream = logging.Formatter("[%(levelname)s] - %(message)s")
    handler_stream = logging.StreamHandler()
    handler_stream.setFormatter(fmt_stream)
    handler_stream.setLevel(logging.INFO)

    fmt_file = logging.Formatter(
        "%(asctime)s %(name)s:%(lineno)s [%(levelname)s] - %(message)s"
    )
    handler_file = logging.FileHandler(".fco.log")
    handler_file.setFormatter(fmt_file)
    handler_file.setLevel(logging.DEBUG)

    log = logging.getLogger("fcoclient")
    log.addHandler(handler_stream)
    log.addHandler(handler_file)
    log.setLevel(logging.DEBUG)

    return log


class ArgParser(argparse.ArgumentParser):
    """
    Argument parser that displays help on error
    """

    def error(self, message):
        sys.stderr.write("error: {}\n".format(message))
        self.print_help()
        sys.exit(2)

    def add_subparsers(self):
        # Workaround for http://bugs.python.org/issue9253
        subparsers = super(ArgParser, self).add_subparsers()
        subparsers.required = True
        subparsers.dest = "command"
        return subparsers


def create_parser():
    parser = ArgParser(description="DICE Deployment Service CLI",
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", help="Configuration file to use",
                        default=".fco.conf")
    subparsers = parser.add_subparsers()

    cmds = inspect.getmembers(commands, inspect.isclass)
    for _, cls in sorted(cmds, key=lambda x: x[0]):
        sub = cls.add_subparser(subparsers)
        sub.set_defaults(cls=cls)

    return parser


def main():
    logger = _configure_logging()

    parser = create_parser()
    args = parser.parse_args()

    client = None
    if args.cls.require_client:
        try:
            client = Client(**Config.load_from_file(args.config))
        except InvalidConfigError as e:
            print("ERROR: {}".format(e), file=sys.stderr)
            return 1

    try:
        getattr(args.cls(client, logger), args.command)(args)
    except (FCOError, RequestException) as e:
        logger.error(e)
        return 1

    return 0
