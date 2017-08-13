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

"""
Basic command line helpers.
"""

from __future__ import print_function

import argparse
import sys

from fcoclient import utils


class Command(object):

    require_client = True

    @staticmethod
    def add_subparser(subparsers):
        raise NotImplementedError("Command is an abstract class")

    @staticmethod
    def create_list_parser(subparsers, item_names):
        parser = subparsers.add_parser("list",
                                       help="List {}".format(item_names))
        parser.add_argument("-n", "--no-items", type=int, default=100,
                            help="Number of {} to display".format(item_names))
        parser.add_argument(
            "-f", "--filter", action="append",
            help="Only display {} matching filter".format(item_names)
        )
        return parser

    @staticmethod
    def create_get_parser(subparsers, item_name):
        msg = "Get details about selected {}".format(item_name)
        parser = subparsers.add_parser("get", help=msg)
        parser.add_argument("uuid", help="UUID of the {}".format(item_name))
        return parser

    @staticmethod
    def create_skeleton_parser(subparsers, item_name):
        msg = "Create {} skeleton".format(item_name)
        parser = subparsers.add_parser("skeleton", help=msg)
        parser.add_argument("-o", "--output", type=argparse.FileType("w"),
                            default=sys.stdout, help="Output file")
        return parser

    @staticmethod
    def add_wait_argument(parser, help):
        parser.add_argument("-w", "--wait", action="store_true", help=help)

    @staticmethod
    def create_new_parser(subparsers, item_name):
        msg = "Create new {}".format(item_name)
        parser = subparsers.add_parser("create", help=msg)
        parser.add_argument("skeleton", type=argparse.FileType("r"),
                            help="Skeleton file")
        Command.add_wait_argument(parser, "Wait for creation to terminate")
        return parser

    @staticmethod
    def create_delete_parser(subparsers, item_name):
        msg = "Delete {}".format(item_name)
        parser = subparsers.add_parser("delete", help=msg)
        parser.add_argument("uuid", help="UUID of the {}".format(item_name))
        Command.add_wait_argument(parser, "Wait for deletion to terminate")
        parser.add_argument("-c", "--cascade", action="store_true",
                            help="Delete dependent resources")
        return parser

    def __init__(self, client, logger):
        self.client = client
        self.logger = logger

    def parse_filter(self, filter_conditions):
        if filter_conditions is None:
            return {}
        try:
            return dict(f.split("=", 1) for f in filter_conditions)
        except ValueError:
            self.logger.error("Malformed filter. Must be in key=value form.")
            sys.exit(1)

    def list(self, args):
        self.logger.info("Listing items")
        conditions = self.parse_filter(args.filter)
        for item in self.resource_client.list(args.no_items, **conditions):
            print("{} ({})".format(item.name, item.uuid))
        self.logger.info("Items listed")

    def get(self, args):
        self.logger.info("Getting item details")
        utils.output_json(self.resource_client.get(uuid=args.uuid))
        self.logger.info("Item details retrieved")

    def skeleton(self, _):
        self.logger.info("Generating item skeleton")
        utils.output_json(self.resource_client.skeleton())
        self.logger.info("Done generating item skeleton")

    def wait_for_termination(self, job, wait):
        if wait:
            self.logger.info("Waiting for job to finish")
            job = self.client.job.wait(job.uuid)
        utils.output_json(job)
        msg = "Job {}".format("terminated" if wait else "scheduled")
        self.logger.info(msg)
