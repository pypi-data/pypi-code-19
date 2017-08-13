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

from fcoclient.commands.base import Command


class JobCmd(Command):

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser("job",
                                       help="Inspect jobs")
        subs = parser.add_subparsers()

        Command.create_get_parser(subs, "job")
        Command.create_list_parser(subs, "jobs")

        return parser

    @property
    def resource_client(self):
        return self.client.job

    def list(self, args):
        self.logger.info("Listing jobs")
        conditions = self.parse_filter(args.filter)
        for job in self.client.job.list(args.no_items, **conditions):
            print("{} ({})".format(job["itemDescription"], job.uuid))
        self.logger.info("Jobs listed")
