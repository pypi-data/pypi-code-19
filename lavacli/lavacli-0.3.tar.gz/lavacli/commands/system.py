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

from contextlib import suppress
import os
import shutil
import xmlrpc.client
import yaml


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "export"
    sys_export = sub.add_parser("export", help="Export server configuration")
    sys_export.add_argument("name", help="Name of the export")

    # "import"
    sub.add_parser("import", help="Import server configuration")

    # "methods"
    sys_methods = sub.add_parser("methods", help="List methods")
    sys_sub = sys_methods.add_subparsers(dest="sub_sub_sub_command",
                                         help="Sub commands")
    sys_sub.required = True
    sys_sub.add_parser("list", help="List available methods")

    sys_help = sys_sub.add_parser("help", help="Method help")
    sys_help.add_argument("method", help="Method name")

    sys_signature = sys_sub.add_parser("signature", help="Method signature")
    sys_signature.add_argument("method", help="Method name")

    # "version"
    sub.add_parser("version", help="Return the server version")

    # "whoami"
    sub.add_parser("whoami", help="Return the current username")


def help_string():
    return "System information"


def handle_export(proxy, options):
    print("Export to %s" % options.name)
    with suppress(FileNotFoundError):
        shutil.rmtree(options.name)
    os.mkdir(options.name)
    os.chdir(options.name)

    print("Listing aliases")
    aliases = []
    for alias in proxy.scheduler.aliases.list():
        print("* %s" % alias)
        aliases.append(proxy.scheduler.aliases.show(alias))

    print("Listing tags")
    tags = []
    for tag in proxy.scheduler.tags.list():
        print("* %s" % tag["name"])
        tags.append(tag)

    print("Listing workers")
    workers = []
    for worker in proxy.scheduler.workers.list():
        print("* %s" % worker)
        w = proxy.scheduler.workers.show(worker)
        workers.append({"hostname": w["hostname"],
                        "description": w["description"],
                        "master": w["master"],
                        "hidden": w["hidden"]})

    print("Listing device-types")
    os.mkdir("device-types")
    device_types = []
    for device_type in proxy.scheduler.device_types.list():
        print("* %s" % device_type["name"])
        dt = proxy.scheduler.device_types.show(device_type["name"])
        device_types.append({"name": dt["name"],
                             "description": dt["description"],
                             "display": dt["display"],
                             "health_disabled": dt["health_disabled"],
                             "owners_only": dt["owners_only"],
                             "aliases": dt["aliases"]})

        try:
            dt_template = proxy.scheduler.device_types.get_template(dt["name"])
        except xmlrpc.client.Fault as exc:
            if exc.faultCode == 404:
                print("  => No template found")
                continue
            raise
        with open(os.path.join("device-types", dt["name"] + ".jinja2"),
                  "w", encoding="utf-8") as f_out:
            f_out.write(str(dt_template))

    print("Listing devices")
    os.mkdir("devices")
    devices = []
    for device in proxy.scheduler.devices.list():
        print("* %s" % device["hostname"])
        d = proxy.scheduler.devices.show(device["hostname"])
        devices.append({"hostname": d["hostname"],
                        "description": d["description"],
                        "device_type": d["device_type"],
                        "pipeline": d["pipeline"],
                        "worker": d["worker"],
                        "status": d["status"],
                        "public": d["public"],
                        "user": d["user"],
                        "group": d["group"],
                        "health": d["health"],
                        "tags": d["tags"]})

        try:
            device_dict = proxy.scheduler.devices.get_dictionary(device["hostname"])
        except xmlrpc.client.Fault as exc:
            if exc.faultCode == 404:
                print("  => No device dict found")
                continue
            raise
        with open(os.path.join("devices", device["hostname"] + ".jinja2"),
                  "w", encoding="utf-8") as f_out:
            f_out.write(str(device_dict))

    export = {"aliases": aliases,
              "devices": devices,
              "device-types": device_types,
              "tags": tags,
              "workers": workers}

    # Dump the configuration
    with open("instance.yaml", "w", encoding="utf-8") as f_out:
        f_out.write(yaml.dump(export).rstrip("\n"))


def handle_methods(proxy, options):
    if options.sub_sub_sub_command == "help":
        print(proxy.system.methodHelp(options.method))
    elif options.sub_sub_sub_command == "signature":
        print(proxy.system.methodSignature(options.method))
    else:
        # Fallback to "list"
        methods = proxy.system.listMethods()
        for method in methods:
            print(method)


def handle_version(proxy, _):
    print(proxy.system.version())


def handle_whoami(proxy, _):
    username = proxy.system.whoami()
    if username is None:
        print("<AnonymousUser>")
    else:
        print(username)


def handle(proxy, options, _):
    handlers = {
        "export": handle_export,
        "methods": handle_methods,
        "version": handle_version,
        "whoami": handle_whoami
    }
    return handlers[options.sub_sub_command](proxy, options)
