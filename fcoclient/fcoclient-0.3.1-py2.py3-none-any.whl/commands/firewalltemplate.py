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


class FirewallTemplateCmd(Command):

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser("firewalltemplate",
                                       help="Inspect firewall templates")
        subs = parser.add_subparsers()

        Command.create_get_parser(subs, "firewall template")
        Command.create_list_parser(subs, "firewall templates")
        Command.create_skeleton_parser(subs, "firewall template")
        Command.create_new_parser(subs, "firewall template")
        Command.create_delete_parser(subs, "firewall template")

        sub = subs.add_parser("apply",
                              help="Apply firewall template to address")
        sub.add_argument("uuid", help="UUID of the server")
        sub.add_argument("address", help="IP address to apply to")
        Command.add_wait_argument(sub, "Wait for firewall template to apply")

        return parser

    @property
    def resource_client(self):
        return self.client.firewalltemplate

    def create(self, args):
        self.logger.info("Creating new firewall template")
        skeleton = json.load(args.skeleton)
        job = self.client.firewalltemplate.create(skeleton)
        self.wait_for_termination(job, args.wait)

    def delete(self, args):
        self.logger.info("Deleting firewall template")
        job = self.client.firewalltemplate.delete(args.uuid,
                                                  cascade=args.cascade)
        self.wait_for_termination(job, args.wait)

    def apply(self, args):
        msg = "Applying firewall template {} to ip {}"
        self.logger.info(msg.format(args.uuid, args.address))
        job = self.client.firewalltemplate.apply(args.uuid, args.address)
        self.wait_for_termination(job, args.wait)
