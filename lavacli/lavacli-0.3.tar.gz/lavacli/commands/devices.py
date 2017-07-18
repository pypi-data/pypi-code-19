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

from . import jobs


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    devices_add = sub.add_parser("add", help="Add a device")
    devices_add.add_argument("hostname", help="Hostname of the device")
    devices_add.add_argument("--type", required=True, help="Device-type")
    devices_add.add_argument("--worker", required=True, help="Worker hostname")
    devices_add.add_argument("--description", default=None,
                             help="Device description")

    owner = devices_add.add_mutually_exclusive_group()
    owner.add_argument("--user", default=None, help="Device owner")
    owner.add_argument("--group", default=None, help="Device owner")

    devices_add.add_argument("--status", default=None,
                             choices=["OFFLINE", "IDLE", "RUNNING",
                                      "OFFLINING", "RETIRED", "RESERVED"],
                             help="Device status")
    devices_add.add_argument("--health", default=None,
                             choices=["UNKNOWN", "PASS", "FAIL", "LOOPING"],
                             help="Device health status")

    devices_add.add_argument("--private", action="store_true", default=False,
                             help="Private device, public by default")

    # "dict"
    devices_dict = sub.add_parser("dict", help="Device dictionary")
    dict_sub = devices_dict.add_subparsers(dest="sub_sub_sub_command",
                                           help="Sub commands")
    dict_sub.required = True
    dict_get = dict_sub.add_parser("get",
                                   help="Get the device dictionary")
    dict_get.add_argument("hostname", help="Hostname of the device")
    dict_get.add_argument("--render", action="store_true", default=False,
                          help="Render the dictionary to the configuration.")

    dict_set = dict_sub.add_parser("set",
                                   help="Set the device dictionary")
    dict_set.add_argument("hostname", help="Hostname of the device")
    dict_set.add_argument("config", type=argparse.FileType('r'),
                          help="Configuration file")

    # "force-health"
    devices_fh = sub.add_parser("force-health", help="Force a health check for the device")
    devices_fh.add_argument("hostname", help="Device hostname")
    devices_fh.add_argument("--follow", action="store_true", default=False,
                            help="Wait for the job and print the logs")

    # "list"
    devices_list = sub.add_parser("list", help="List available devices")
    devices_list.add_argument("--all", action="store_true", default=False,
                              help="List every devices, inluding retired")
    devices_list.add_argument("--yaml", dest="output_format", default=None,
                              action="store_const", const="yaml",
                              help="Print as yaml")

    # "show"
    devices_show = sub.add_parser("show", help="Show device details")
    devices_show.add_argument("hostname", help="Device hostname")
    devices_show.add_argument("--yaml", dest="output_format",
                              action="store_const", const="yaml",
                              default=None, help="Print as yaml")

    # "tags"
    devices_tags = sub.add_parser("tags", help="Manage tags")
    tags_sub = devices_tags.add_subparsers(dest="sub_sub_sub_command",
                                           help="Sub commands")
    tags_sub.required = True
    tags_add = tags_sub.add_parser("add", help="Add a tag")
    tags_add.add_argument("hostname", help="Hostname of the device")
    tags_add.add_argument("tag", help="Name of the tag")

    tags_list = tags_sub.add_parser("list", help="List tags for the device")
    tags_list.add_argument("hostname", help="Hostname of the device")
    tags_list.add_argument("--yaml", dest="output_format",
                           action="store_const", const="yaml",
                           help="Print as yaml")

    tags_del = tags_sub.add_parser("delete", help="Remove a tag")
    tags_del.add_argument("hostname", help="Hostname of the device")
    tags_del.add_argument("tag", help="Name of the tag")

    # "update"
    devices_update = sub.add_parser("update", help="Update device properties")
    devices_update.add_argument("hostname",
                                help="Hostname of the device")
    devices_update.add_argument("--worker", default=None,
                                help="Update the worker")
    devices_update.add_argument("--description", default=None,
                                help="Update the description")

    owner = devices_update.add_mutually_exclusive_group()
    owner.add_argument("--user", default=None, help="Device owner")
    owner.add_argument("--group", default=None, help="Device owner")

    devices_update.add_argument("--status", default=None,
                                choices=["OFFLINE", "IDLE", "RUNNING",
                                         "OFFLINING", "RETIRED", "RESERVED"],
                                help="Update the device status")
    devices_update.add_argument("--health", default=None,
                                choices=["UNKNOWN", "PASS", "FAIL", "LOOPING"],
                                help="Update the device health status")

    display = devices_update.add_mutually_exclusive_group()
    display.add_argument("--public", default=None, action="store_true",
                         help="Make the device public")
    display.add_argument("--private", dest="public", action="store_false",
                         help="Make the device private")


def help_string():
    return "Manage devices"


def handle_add(proxy, options):
    proxy.scheduler.devices.add(options.hostname, options.type,
                                options.worker, options.user,
                                options.group, not options.private,
                                options.status, options.health,
                                options.description)


def handle_dict(proxy, options):
    if options.sub_sub_sub_command == "get":
        config = proxy.scheduler.devices.get_dictionary(options.hostname,
                                                        options.render)
        print(str(config).rstrip("\n"))
    else:
        config = options.config.read()
        ret = proxy.scheduler.devices.set_dictionary(options.hostname,
                                                     config)
        if not ret:
            print("Unable to set the configuration")
        return 0 if ret else 1


def handle_fh(proxy, options):
    job_id = proxy.scheduler.devices.force_health_check(options.hostname)
    if options.follow:
        # Adapt to "jobs logs" options
        options.job_id = job_id
        options.no_follow = False
        options.polling = 5
        options.raw = False
        jobs.handle_logs(proxy, options)


def handle_list(proxy, options):
    devices = proxy.scheduler.devices.list(options.all)

    if options.output_format == "yaml":
        print(yaml.dump(devices).rstrip("\n"))
    else:
        print("Devices:")
        for device in devices:
            print("* %s (%s): %s" % (device["hostname"], device["type"], device["status"]))


def handle_show(proxy, options):
    device = proxy.scheduler.devices.show(options.hostname)

    if options.output_format == "yaml":
        print(yaml.dump(device).rstrip("\n"))
    else:
        print("name        : %s" % device["hostname"])
        print("device-type : %s" % device["device_type"])
        print("status      : %s" % device["status"])
        print("user        : %s" % device["user"])
        print("group       : %s" % device["group"])
        print("health      : %s" % device["health"])
        print("health job  : %s" % device["health_job"])
        print("description : %s" % device["description"])
        print("public      : %s" % device["public"])
        print("pipeline    : %s" % device["pipeline"])
        print("device-dict : %s" % device["has_device_dict"])
        print("worker      : %s" % device["worker"])
        print("current job : %s" % device["current_job"])
        print("tags        : %s" % device["tags"])


def handle_tags(proxy, options):
    if options.sub_sub_sub_command == "add":
        proxy.scheduler.devices.tags.add(options.hostname, options.tag)
    elif options.sub_sub_sub_command == "delete":
        proxy.scheduler.devices.tags.delete(options.hostname, options.tag)
    else:
        tags = proxy.scheduler.devices.tags.list(options.hostname)
        if options.output_format == "yaml":
            print(yaml.dump(tags).rstrip("\n"))
        else:
            print("Tags:")
            for tag in tags:
                print("* %s" % tag)


def handle_update(proxy, options):
    proxy.scheduler.devices.update(options.hostname, options.worker,
                                   options.user, options.group,
                                   options.public, options.status,
                                   options.health, options.description)


def handle(proxy, options, _):
    handlers = {
        "add": handle_add,
        "dict": handle_dict,
        "force-health": handle_fh,
        "list": handle_list,
        "show": handle_show,
        "tags": handle_tags,
        "update": handle_update
    }
    return handlers[options.sub_sub_command](proxy, options)
