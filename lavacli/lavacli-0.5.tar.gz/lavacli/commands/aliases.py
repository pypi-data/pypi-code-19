# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import yaml


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    aliases_add = sub.add_parser("add", help="add an alias")
    aliases_add.add_argument("alias", help="alias name")

    # "delete"
    aliases_del = sub.add_parser("delete", help="delete an alias")
    aliases_del.add_argument("alias", help="alias name")

    # "list"
    aliases_list = sub.add_parser("list", help="list available aliases")
    aliases_list.add_argument("--yaml", dest="output_format", default=None,
                              action="store_const", const="yaml",
                              help="print as yaml")

    # "show"
    aliases_show = sub.add_parser("show", help="show alias details")
    aliases_show.add_argument("alias", help="alias")
    aliases_show.add_argument("--yaml", dest="output_format",
                              action="store_const", const="yaml",
                              default=None, help="print as yaml")


def help_string():
    return "manage device-type aliases"


def handle_add(proxy, options):
    proxy.scheduler.aliases.add(options.alias)


def handle_delete(proxy, options):
    proxy.scheduler.aliases.delete(options.alias)


def handle_list(proxy, options):
    aliases = proxy.scheduler.aliases.list()
    if options.output_format == "yaml":
        print(yaml.dump(aliases).rstrip("\n"))
    else:
        print("Aliases:")
        for alias in aliases:
            print("* %s" % alias)


def handle_show(proxy, options):
    alias = proxy.scheduler.aliases.show(options.alias)
    if options.output_format == "yaml":
        print(yaml.dump(alias).rstrip("\n"))
    else:
        print("name        : %s" % alias["name"])
        print("device-types:")
        for dt in alias["device_types"]:
            print("* %s" % dt)


def handle(proxy, options, _):
    handlers = {
        "add": handle_add,
        "delete": handle_delete,
        "list": handle_list,
        "show": handle_show
    }
    return handlers[options.sub_sub_command](proxy, options)
