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
import os
import requests
import socket
from urllib.parse import urlparse
import xmlrpc.client
import yaml

from .__about__ import *

from .commands import (
    aliases,
    devices,
    device_types,
    events,
    jobs,
    results,
    system,
    tags,
    workers
)


class RequestsTransport(xmlrpc.client.Transport):

    def __init__(self, scheme, proxy=None, timeout=20.0, verify_ssl_cert=True):
        super().__init__()
        self.scheme = scheme
        # Set the user agent
        self.user_agent = "lavacli v%s" % __version__
        if proxy is None:
            self.proxies = {}
        else:
            self.proxies = {scheme: proxy}
        self.timeout = timeout
        self.verify_ssl_cert = verify_ssl_cert
        if not verify_ssl_cert:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def request(self, host, handler, data, verbose=False):
        headers = {"User-Agent": self.user_agent,
                   "Content-Type": "text/xml",
                   "Accept-Encoding": "gzip"}
        url = "%s://%s%s" % (self.scheme, host, handler)
        try:
            response = None
            response = requests.post(url, data=data, headers=headers,
                                     timeout=self.timeout,
                                     verify=self.verify_ssl_cert,
                                     proxies=self.proxies)
            response.raise_for_status()
            return self.parse_response(response)
        except requests.RequestException as e:
            if response is None:
                raise xmlrpc.client.ProtocolError(url, 500, str(e), "")
            else:
                raise xmlrpc.client.ProtocolError(url, response.status_code,
                                                  str(e), response.headers)

    def parse_response(self, resp):
        """
        Parse the xmlrpc response.
        """
        p, u = self.getparser()
        p.feed(resp.text)
        p.close()
        return u.close()


def load_config(identity):
    # Build the path to the configuration file
    config_dir = os.environ.get("XDG_CONFIG_HOME") or "~/.config"
    config_filename = os.path.expanduser(os.path.join(config_dir,
                                                      "lavacli.yaml"))

    # load configuration from file
    with open(config_filename, "r", encoding="utf-8") as f_conf:
        config = yaml.load(f_conf.read())

    return config.get(identity)


def parser(commands):
    parser_obj = argparse.ArgumentParser()
    url = parser_obj.add_mutually_exclusive_group(required=True)
    url.add_argument("--uri", type=str, default=None,
                     help="URI of the lava-server RPC endpoint")
    url.add_argument("--identity", "-i", type=str, default=None,
                     help="Server identity")

    root = parser_obj.add_subparsers(dest="sub_command", help="Sub commands")

    keys = list(commands.keys())
    keys.sort()
    for name in keys:
        cls = commands[name]
        cls.configure_parser(root.add_parser(name, help=cls.help_string()))

    return parser_obj


def main():
    commands = {"aliases": aliases,
                "devices": devices,
                "device-types": device_types,
                "events": events,
                "jobs": jobs,
                "results": results,
                "system": system,
                "tags": tags,
                "workers": workers}

    # Parse the command line
    parser_obj = parser(commands)
    options = parser_obj.parse_args()

    if options.uri is None:
        config = load_config(options.identity)
        if config is None:
            print("Unknown identity '%s'" % options.identity)
            return 1
        options.uri = config["uri"]
    else:
        config = None

    # Check that a sub_command was given
    if options.sub_command is None:
        parser_obj.print_help()
        return 1

    # Create the Transport object
    parsed_uri = urlparse(options.uri)
    if options.identity:
        transport = RequestsTransport(parsed_uri.scheme,
                                      config.get("proxy"),
                                      config.get("timeout", 20.0),
                                      config.get("verify_ssl_cert", True))
    else:
        transport = RequestsTransport(parsed_uri.scheme)

    # Connect to the RPC endpoint
    try:
        # allow_none is True because the server does support it
        proxy = xmlrpc.client.ServerProxy(options.uri, allow_none=True,
                                          transport=transport)
        return commands[options.sub_command].handle(proxy, options, config)
    except xmlrpc.client.Error as exc:
        if "sub_sub_command" in options:
            print("Unable to call '%s.%s': %s" % (options.sub_command,
                                                  options.sub_sub_command,
                                                  str(exc)))
        else:
            print("Unable to call '%s': %s" % (options.sub_command,
                                               str(exc)))
    except (ConnectionError, socket.gaierror) as exc:
        print("Unable to connect to '%s': %s" % (options.uri, str(exc)))

    return 1
