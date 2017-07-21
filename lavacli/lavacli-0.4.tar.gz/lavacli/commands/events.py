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

import json


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "listen"
    sub.add_parser("listen", help="listen to events")

    # "wait"
    sub.add_parser("wait", help="wait for a specific event")
    # TODO: add the right arguments


def help_string():
    return "listen to events"


def handle_listen(proxy, options, config):
    import zmq
    from zmq.utils.strtypes import b, u
    # Try to find the socket url
    if config is None or config.get("events", {}).get("uri") is None:
        url = proxy.scheduler.get_publisher_event_socket()
    else:
        url = config["events"]["uri"]

    if url is None:
        print("Unable to find the socket url")
        return 1

    context = zmq.Context()
    sock = context.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, b"")
    # Set the sock proxy (if needed)
    socks = config.get("events", {}).get("socks_proxy")
    if socks is not None:
        print("Listening to %s (socks %s)" % (url, socks))
        sock.setsockopt(zmq.SOCKS_PROXY, b(socks))
    else:
        print("Listening to %s" % url)

    try:
        sock.connect(url)
    except zmq.error.ZMQError as exc:
        print("Unable to connect: %s" % exc)
        return 1

    while True:
        msg = sock.recv_multipart()
        try:
            (topic, _, dt, username, data) = (u(m) for m in msg)
        except ValueError:
            print("Invalid message: %s" % msg)
            continue

        # If unknown, print the full data
        msg = data
        data = json.loads(data)
        # Print according to the topic
        topic_end = topic.split(".")[-1]
        if topic_end == "device":
            msg = "[%s] <%s> %s" % (data["device"], data["device_type"], data["status"])
            if "job" in data:
                msg += " for %s" % data["job"]
        elif topic_end == "testjob":
            msg = "[%s] <%s> %s (%s)" % (data["job"], data.get("device", "??"),
                                         data["status"], data["description"])
        print("\033[1;30m%s\033[0m \033[1;37m%s\033[0m \033[32m%s\033[0m - %s" % (dt, topic, username, msg))


def handle_wait(proxy, options, config):
    return 1


def handle(proxy, options, config):
    handlers = {
        "listen": handle_listen,
        "wait": handle_wait
    }
    return handlers[options.sub_sub_command](proxy, options, config)
