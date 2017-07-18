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

import argparse
import yaml


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    dt_add = sub.add_parser("add", help="Add a device type")
    dt_add.add_argument("name", help="Name of the device-type")
    dt_add.add_argument("--description", default=None,
                        help="Device-type description")
    dt_add.add_argument("--hide", dest="display", action="store_false",
                        default=True, help="Device is hidden in the UI")
    dt_add.add_argument("--owners-only", action="store_true", default=False,
                        help="Devices are only visible to owners")
    dt_health = dt_add.add_argument_group("health check")
    dt_health.add_argument("--health-frequency", default=24,
                           help="How often to run health checks.")
    dt_health.add_argument("--health-denominator", default="hours",
                           choices=["hours", "jobs"],
                           help="Initiate health checks by hours or by jobs.")

    # "aliases"
    dt_aliases = sub.add_parser("aliases", help="Manage aliases")
    aliases_sub = dt_aliases.add_subparsers(dest="sub_sub_sub_command",
                                            help="Sub commands")
    aliases_sub.required = True

    aliases_add = aliases_sub.add_parser("add", help="Add aliases")
    aliases_add.add_argument("name", help="Name of the device-type")
    aliases_add.add_argument("alias", help="Name of alias")

    aliases_delete = aliases_sub.add_parser("delete", help="Delete aliases")
    aliases_delete.add_argument("name", help="Name of the device-type")
    aliases_delete.add_argument("alias", help="Name of alias")

    aliases_list = aliases_sub.add_parser("list", help="List aliases for the device-type")
    aliases_list.add_argument("name", help="device-type")
    aliases_list.add_argument("--yaml", dest="output_format", default=None,
                              action="store_const", const="yaml",
                              help="Print as yaml")

    # "list"
    dt_list = sub.add_parser("list", help="List available device-types")
    dt_list.add_argument("--all", "-a", dest="show_all",
                         default=False, action="store_true",
                         help="Show all device types in the database, "
                              "including non-installed ones")
    dt_list.add_argument("--yaml", dest="output_format", default=None,
                         action="store_const", const="yaml",
                         help="Print as yaml")

    # "show"
    dt_show = sub.add_parser("show", help="Show device-type details")
    dt_show.add_argument("name", help="Name of the device-type")
    dt_show.add_argument("--yaml", dest="output_format",
                         action="store_const", const="yaml",
                         default=None, help="Print as yaml")

    # "template"
    devices_template = sub.add_parser("template", help="Device-type template")
    dt_sub = devices_template.add_subparsers(dest="sub_sub_sub_command",
                                             help="Sub commands")
    dt_sub.required = True
    dt_get = dt_sub.add_parser("get",
                               help="Get the device-type template")
    dt_get.add_argument("name", help="Name of the device-type")

    dt_set = dt_sub.add_parser("set",
                               help="Set the device-type template")
    dt_set.add_argument("name", help="Name of the device-type")
    dt_set.add_argument("template", type=argparse.FileType('r'),
                        help="Device-type template")

    # "update"
    dt_update = sub.add_parser("update", help="Update device-type")
    dt_update.add_argument("name", help="Name of the device-type")
    dt_update.add_argument("--description", default=None,
                           help="Device-type description")

    visibility = dt_update.add_mutually_exclusive_group()
    visibility.add_argument("--hide", dest="display", action="store_false",
                            default=None, help="Device-type is hidden in the UI")
    visibility.add_argument("--show", dest="display", action="store_true",
                            help="Device-type is visible in the UI")

    owner = dt_update.add_mutually_exclusive_group()
    owner.add_argument("--owners-only", action="store_true", dest="owners_only",
                       default=None,
                       help="Devices are only visible to owners")
    owner.add_argument("--public", action="store_false", dest="owners_only",
                       help="Devices are visible to all users")

    dt_health = dt_update.add_argument_group("health check")
    dt_health.add_argument("--health-frequency", default=None,
                           help="How often to run health checks.")
    dt_health.add_argument("--health-denominator", default=None,
                           choices=["hours", "jobs"],
                           help="Initiate health checks by hours or by jobs.")

    health = dt_health.add_mutually_exclusive_group()
    health.add_argument("--health-disabled", default=None,
                        action="store_true",
                        help="Disable health checks")
    health.add_argument("--health-active", dest="health_disabled",
                        action="store_false",
                        help="Activate health checks")


def help_string():
    return "Manage device-types"


def handle_add(proxy, options):
    proxy.scheduler.device_types.add(options.name, options.description,
                                     options.display, options.owners_only,
                                     options.health_frequency,
                                     options.health_denominator)


def handle_aliases(proxy, options):
    if options.sub_sub_sub_command == "add":
        proxy.scheduler.device_types.aliases.add(options.name, options.alias)
    elif options.sub_sub_sub_command == "list":
        aliases = proxy.scheduler.device_types.aliases.list(options.name)
        if options.output_format == "yaml":
            print(yaml.dump(aliases).rstrip("\n"))
        else:
            print("Aliases:")
            for alias in aliases:
                print("* %s" % alias)
    elif options.sub_sub_sub_command == "delete":
        proxy.scheduler.device_types.aliases.delete(options.name,
                                                    options.alias)


def handle_list(proxy, options):
    device_types = proxy.scheduler.device_types.list(options.show_all)

    if options.output_format == "yaml":
        print(yaml.dump(device_types).rstrip("\n"))
    else:
        print("Device-Types:")
        for dt in device_types:
            print("* %s (%s)" % (dt["name"], dt["devices"]))


def handle_show(proxy, options):
    dt = proxy.scheduler.device_types.show(options.name)

    if options.output_format == "yaml":
        print(yaml.dump(dt).rstrip("\n"))
    else:
        print("name            : %s" % dt["name"])
        print("description     : %s" % dt["description"])
        print("display         : %s" % dt["display"])
        print("owners only     : %s" % dt["owners_only"])
        print("health disabled : %s" % dt["health_disabled"])
        print("aliases         : %s" % dt["aliases"])
        print("devices         : %s" % dt["devices"])


def handle_template(proxy, options):
    if options.sub_sub_sub_command == "get":
        template = proxy.scheduler.device_types.get_template(options.name)
        print(str(template).rstrip("\n"))
    else:
        template = options.template.read()
        proxy.scheduler.device_types.set_template(options.name, template)


def handle_update(proxy, options):
    proxy.scheduler.device_types.update(options.name, options.description,
                                        options.display, options.owners_only,
                                        options.health_frequency,
                                        options.health_denominator,
                                        options.health_disabled)


def handle(proxy, options, _):
    handlers = {
        "add": handle_add,
        "aliases": handle_aliases,
        "list": handle_list,
        "show": handle_show,
        "template": handle_template,
        "update": handle_update
    }
    return handlers[options.sub_sub_command](proxy, options)
