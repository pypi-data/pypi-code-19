# Copyright (c) 2017 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.replication as replication

class ReplicationReplicate(qumulo.lib.opts.Subcommand):
    NAME = "replication_replicate"
    DESCRIPTION = "Replicate from the source to the target of the " \
        "specified relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.replicate(conninfo, credentials, args.id)

class ReplicationCreateRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_create_relationship"
    DESCRIPTION = "Create a new replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument(
            "--source", required=True,
            help="Path to the source directory that we replicate from")
        parser.add_argument(
            "--target", required=True,
            help="Path to the target directory that we replicate to")
        parser.add_argument(
            "--target-address", required=True,
            help="The target IP address")
        parser.add_argument(
            "--target-port", type=int, required=False,
            help="Network port to replicate to on the target "
                "(overriding default)")

    @staticmethod
    def main(conninfo, credentials, args):

        if args.target_port:
            print replication.create_relationship(
                conninfo,
                credentials,
                args.source,
                args.target,
                args.target_address,
                target_port=args.target_port)
        else:
            print replication.create_relationship(
                conninfo,
                credentials,
                args.source,
                args.target,
                args.target_address)

class ReplicationListRelationships(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_relationships"
    DESCRIPTION = "List existing replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_relationships(conninfo, credentials)

class ReplicationListSourceRelationships(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_source_relationships"
    DESCRIPTION = "List existing source replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_source_relationships(conninfo, credentials)

class ReplicationGetRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_relationship"
    DESCRIPTION = "Get information about the specified " \
        "replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_relationship(conninfo, credentials, args.id)

class ReplicationGetSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_source_relationship"
    DESCRIPTION = "Get information about the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_source_relationship(
            conninfo, credentials, args.id)

class ReplicationDeleteRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_relationship"
    DESCRIPTION = "Delete the specified replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.delete_relationship(conninfo, credentials, args.id)

class ReplicationDeleteSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_source_relationship"
    DESCRIPTION = "Delete the specified source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.delete_source_relationship(conninfo, credentials, args.id)

class ReplicationDeleteTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_target_relationship"
    DESCRIPTION = "Delete the specified target replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.delete_target_relationship(conninfo, credentials, args.id)

class ReplicationListRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_relationship_statuses"
    DESCRIPTION = "List statuses for all existing replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_relationship_statuses(conninfo, credentials)

class ReplicationListSourceRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_source_relationship_statuses"
    DESCRIPTION = "List statuses for all existing source replication " \
        "relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_source_relationship_statuses(
            conninfo, credentials)

class ReplicationListTargetRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_target_relationship_statuses"
    DESCRIPTION = "List statuses for all existing target " \
        "replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_target_relationship_statuses(
            conninfo, credentials)

class ReplicationGetRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_relationship_status"
    DESCRIPTION = "Get current status of the specified " \
        "replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_relationship_status(
            conninfo,
            credentials,
            args.id)

class ReplicationGetSourceRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_source_relationship_status"
    DESCRIPTION = "Get current status of the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_source_relationship_status(
            conninfo,
            credentials,
            args.id)

class ReplicationGetTargetRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_target_relationship_status"
    DESCRIPTION = "Get current target of the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_target_relationship_status(
            conninfo,
            credentials,
            args.id)

class ReplicationAuthorize(qumulo.lib.opts.Subcommand):
    NAME = "replication_authorize"
    DESCRIPTION = "Authorize the specified replication relationship, "+ \
        "establishing this cluster as the target of replication."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.authorize(conninfo, credentials, args.id)


class ReplicationEnableReplication(qumulo.lib.opts.Subcommand):
    NAME = "replication_enable_replication"
    DESCRIPTION = "Enable automatic replication for the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.enable_replication(conninfo, credentials, args.id)

class ReplicationDisableReplication(qumulo.lib.opts.Subcommand):
    NAME = "replication_disable_replication"
    DESCRIPTION = "Disable automatic replication for the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.disable_replication(conninfo, credentials, args.id)
