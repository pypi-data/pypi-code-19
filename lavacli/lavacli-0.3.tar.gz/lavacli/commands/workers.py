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
    workers_add = sub.add_parser("add", help="Add a worker")
    workers_add.add_argument("hostname", type=str,
                             help="Hostname of the worker")
    workers_add.add_argument("--description", type=str, default=None,
                             help="Worker description")
    workers_add.add_argument("--disabled", action="store_true",
                             default=False, help="Create a disabled worker")

    # "config"
    workers_config = sub.add_parser("config", help="Worker configuration")
    config_sub = workers_config.add_subparsers(dest="sub_sub_sub_command",
                                               help="Sub commands")
    config_sub.required = True
    config_get = config_sub.add_parser("get",
                                       help="Get the worker configuration")
    config_get.add_argument("hostname", type=str,
                            help="Hostname of the worker")

    config_set = config_sub.add_parser("set",
                                       help="Set the worker configuration")
    config_set.add_argument("hostname", type=str,
                            help="Hostname of the worker")
    config_set.add_argument("config", type=argparse.FileType('r'),
                            help="Configuration file")

    # "list"
    workers_list = sub.add_parser("list", help="List workers")
    workers_list.add_argument("--yaml", dest="output_format",
                              action="store_const", const="yaml",
                              default=None, help="Print as yaml")

    # "update"
    update_parser = sub.add_parser("update", help="Update worker properties")
    update_parser.add_argument("hostname", type=str,
                               help="Hostname of the worker")
    update_parser.add_argument("--description", type=str, default=None,
                               help="Worker description")
    display = update_parser.add_mutually_exclusive_group()
    display.add_argument("--disable", action="store_false",
                         default=None, dest="display",
                         help="Disable the worker")
    display.add_argument("--enable", action="store_true",
                         default=None, dest="display",
                         help="Enable the worker")

    # "show"
    workers_show = sub.add_parser("show", help="Details of a worker")
    workers_show.add_argument("hostname", help="Hostname of the worker")
    workers_show.add_argument("--yaml", dest="output_format",
                              action="store_const", const="yaml",
                              default=None, help="Print as yaml")


def help_string():
    return "Manage workers"


def handle_add(proxy, options):
    proxy.scheduler.workers.add(options.hostname,
                                options.description,
                                options.disabled)


def handle_config(proxy, options):
    if options.sub_sub_sub_command == "get":
        config = proxy.scheduler.workers.get_config(options.hostname)
        print(str(config).rstrip("\n"))
    else:
        config = options.config.read()
        ret = proxy.scheduler.workers.set_config(options.hostname,
                                                 config)
        if not ret:
            print("Unable to store worker configuration")
            return 1


def handle_list(proxy, options):
    workers = proxy.scheduler.workers.list()
    if options.output_format == "yaml":
        print(yaml.dump(workers).rstrip("\n"))
    else:
        print("Workers:")
        for worker in workers:
            print("* %s" % worker)


def handle_show(proxy, options):
    worker = proxy.scheduler.workers.show(options.hostname)
    if options.output_format == "yaml":
        print(yaml.dump(worker).rstrip("\n"))
    else:
        print("hostname    : %s" % worker["hostname"])
        print("description : %s" % worker["description"])
        print("master      : %s" % worker["master"])
        print("hidden      : %s" % worker["hidden"])
        print("devices     : %s" % worker["devices"])


def handle_update(proxy, options):
    proxy.scheduler.workers.update(options.hostname,
                                   options.description,
                                   not options.display)


def handle(proxy, options, _):
    handlers = {
        "add": handle_add,
        "config": handle_config,
        "list": handle_list,
        "show": handle_show,
        "update": handle_update
    }
    return handlers[options.sub_sub_command](proxy, options)
