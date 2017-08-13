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

import json

from fcoclient.commands.base import Command


class ServerCmd(Command):

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser("server", help="Manage servers")
        subs = parser.add_subparsers()

        Command.create_get_parser(subs, "server")
        Command.create_list_parser(subs, "servers")
        Command.create_skeleton_parser(subs, "server")
        sub = Command.create_new_parser(subs, "server")
        sub.add_argument("-k", "--key-uuid", action="append",
                         help="UUID of the ssh key to install on server")
        Command.create_delete_parser(subs, "server")

        sub = subs.add_parser("start", help="Start server")
        sub.add_argument("uuid", help="UUID of the server")
        Command.add_wait_argument(sub, "Wait for server to start")

        sub = subs.add_parser("stop", help="Stop server")
        sub.add_argument("uuid", help="UUID of the server")
        Command.add_wait_argument(sub, "Wait for server to stop")

        return parser

    @property
    def resource_client(self):
        return self.client.server

    def create(self, args):
        self.logger.info("Creating new server")
        skeleton = json.load(args.skeleton)
        keys = [] if args.key_uuid is None else args.key_uuid
        job = self.client.server.create(skeleton, keys)
        self.wait_for_termination(job, args.wait)

    def delete(self, args):
        self.logger.info("Deleting server")
        job = self.client.server.delete(args.uuid, cascade=args.cascade)
        self.wait_for_termination(job, args.wait)

    def start(self, args):
        self.logger.info("Starting server")
        job = self.client.server.start(args.uuid)
        self.wait_for_termination(job, args.wait)

    def stop(self, args):
        self.logger.info("Stopping server")
        job = self.client.server.stop(args.uuid)
        self.wait_for_termination(job, args.wait)
