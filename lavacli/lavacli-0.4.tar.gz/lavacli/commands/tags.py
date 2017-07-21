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
    tags_add = sub.add_parser("add", help="add a tag")
    tags_add.add_argument("tag", help="tag name")
    tags_add.add_argument("--description", default=None,
                          help="tag description")

    # "delete"
    tags_delete = sub.add_parser("delete", help="delete a tag")
    tags_delete.add_argument("tag", help="tag name")

    # "list"
    tags_list = sub.add_parser("list", help="list tags")
    tags_list.add_argument("--yaml", dest="output_format",
                           action="store_const", const="yaml",
                           help="print as yaml")

    # "show"
    tags_show = sub.add_parser("show", help="show tag details")
    tags_show.add_argument("tag", help="tag name")
    tags_show.add_argument("--yaml", dest="output_format",
                           action="store_const", const="yaml",
                           help="print as yaml")


def help_string():
    return "manage device tags"


def handle_add(proxy, options):
    proxy.scheduler.tags.add(options.tag, options.description)


def handle_delete(proxy, options):
    proxy.scheduler.tags.delete(options.tag)


def handle_list(proxy, options):
    tags = proxy.scheduler.tags.list()
    if options.output_format == "yaml":
        print(yaml.dump(tags).rstrip("\n"))
    else:
        print("Tags:")
        for tag in tags:
            if tag["description"]:
                print("* %s (%s)" % (tag["name"], tag["description"]))
            else:
                print("* %s" % tag["name"])


def handle_show(proxy, options):
    tag = proxy.scheduler.tags.show(options.tag)
    if options.output_format == "yaml":
        print(yaml.dump(tag).rstrip("\n"))
    else:
        print("name       : %s" % tag["name"])
        print("description: %s" % tag["description"])
        print("devices    :")
        for device in tag["devices"]:
            print("* %s" % device)


def handle(proxy, options, _):
    handlers = {
        "add":  handle_add,
        "delete": handle_delete,
        "list": handle_list,
        "show": handle_show
    }
    return handlers[options.sub_sub_command](proxy, options)
