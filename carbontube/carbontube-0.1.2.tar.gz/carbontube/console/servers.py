# -*- coding: utf-8 -*-
# <carbontube - distributed pipeline framework>
#
# Copyright (C) <2016>  Gabriel Falcão <gabriel@nacaolivre.org>
# (C) Author: Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import unicode_literals

import zmq
import imp
import logging
import inspect

from datetime import datetime
from zmq.devices import Device
from carbontube.util import sanitize_name
from carbontube.servers import Phase
from carbontube.servers import Pipeline
from carbontube.console.base import get_sub_parser_argv
from carbontube.console.base import bootstrap_conf_with_gevent


DEFAULT_CONCURRENCY = 32


def execute_command_run_pipeline():
    from carbontube.console.parsers.pipeline import parser
    args = parser.parse_args(get_sub_parser_argv())
    bootstrap_conf_with_gevent(args, loglevel=logging.INFO)

    module_name = ".".join([
        "carbontube",
        "pipelines",
        sanitize_name(args.name).replace('-', '_'),
    ])

    module = imp.load_source(module_name, args.path)
    all_members = dict(
        map(lambda (name, member): (member.name, member),
            filter(lambda (name, member): (
                hasattr(member, 'name') and isinstance(member, type) and issubclass(member, Pipeline)
            ), inspect.getmembers(module)))
    )

    PipelineClass = all_members.get(args.name)

    if not PipelineClass:
        print "invalid job type \033[1;32m'{0}'\033[0m at \033[1;34m{1}\033[0m, but I found these \033[1;33m{2}\033[0m".format(args.name, args.path, ", ".join([x.name for x in all_members.values()]))
        raise SystemExit(1)

    server = PipelineClass(args.name, concurrency=args.concurrency)

    pull_connect_addresses = list(args.pull_connect or [])
    sub_connect_addresses = list(args.sub_connect or [])
    server.run(
        sub_connect_addresses=sub_connect_addresses,
        sub_bind_address=args.sub_bind,
        pull_bind_address=args.pull_bind,
        pull_connect_addresses=pull_connect_addresses,
    )


def execute_command_run_phase():
    from carbontube.console.parsers.phase import parser
    args = parser.parse_args(get_sub_parser_argv())
    bootstrap_conf_with_gevent(args)

    pull_connect_addresses = list(args.pull_connect or [])
    push_connect_addresses = list(args.push_connect or [])

    module_name = ".".join([
        "carbontube",
        "phases",
        sanitize_name(args.job_type).replace('-', '_'),
    ])
    module = imp.load_source(module_name, args.path)
    all_members = dict(
        map(lambda (name, member): (member.job_type, member),
            filter(lambda (name, member): (
                hasattr(member, 'job_type') and isinstance(member, type) and issubclass(member, Phase)
            ), inspect.getmembers(module)))
    )

    PhaseClass = all_members.get(args.job_type)

    if not PhaseClass:
        print "invalid job type \033[1;32m'{0}'\033[0m at \033[1;34m{1}\033[0m, but I found these \033[1;33m{2}\033[0m".format(args.job_type, args.path, ", ".join([x.job_type for x in all_members.values()]))
        raise SystemExit(1)

    server = PhaseClass(
        pull_bind_address=args.pull_bind,
        pub_connect_address=args.pub_connect,
        concurrency=args.concurrency,
        push_connect_addresses=push_connect_addresses,
        pull_connect_addresses=pull_connect_addresses,
    )

    try:
        server.run()
    except KeyboardInterrupt:
        logging.info('exiting')


def execute_command_forwarder():
    from carbontube.console.parsers.streamer import parser

    args = parser.parse_args(get_sub_parser_argv())
    bootstrap_conf_with_gevent(args)

    device = Device(zmq.FORWARDER, zmq.SUB, zmq.PUB)

    device.bind_in(args.subscriber)
    device.bind_out(args.publisher)
    device.setsockopt_in(zmq.SUBSCRIBE, b'')
    if args.subscriber_hwm:
        device.setsockopt_in(zmq.RCVHWM, args.subscriber_hwm)

    if args.publisher_hwm:
        device.setsockopt_out(zmq.SNDHWM, args.publisher_hwm)

    print "carbontube forwarder started"
    print "date", datetime.utcnow().isoformat()
    print "subscriber", (getattr(args, 'subscriber'))
    print "publisher", (getattr(args, 'publisher'))
    device.start()


def execute_command_streamer():
    from carbontube.console.parsers.streamer import parser

    args = parser.parse_args(get_sub_parser_argv())
    bootstrap_conf_with_gevent(args)

    device = Device(zmq.STREAMER, zmq.PULL, zmq.PUSH)

    device.bind_in(args.pull)
    device.bind_out(args.push)
    if args.pull_hwm:
        device.setsockopt_in(zmq.RCVHWM, args.pull_hwm)

    if args.push_hwm:
        device.setsockopt_out(zmq.SNDHWM, args.push_hwm)

    print "carbontube streamer started"
    print "date", datetime.utcnow().isoformat()
    print "pull", (getattr(args, 'pull'))
    print "push", (getattr(args, 'push'))
    device.start()


def execute_command_run_bundle():
    from carbontube.console.parsers.bundle import parser

    args = parser.parse_args(get_sub_parser_argv())
    bootstrap_conf_with_gevent(args, loglevel=logging.INFO)

    module_name = ".".join([
        "carbontube",
        "pipelines",
        sanitize_name(args.name).replace('-', '_'),
    ])

    module = imp.load_source(module_name, args.path)
    all_members = dict(
        map(lambda (name, member): (member.name, member),
            filter(lambda (name, member): (
                hasattr(member, 'name') and isinstance(member, type) and issubclass(member, Pipeline)
            ), inspect.getmembers(module)))
    )

    PipelineClass = all_members.get(args.name)

    if not PipelineClass:
        print "invalid job type \033[1;32m'{0}'\033[0m at \033[1;34m{1}\033[0m, but I found these \033[1;33m{2}\033[0m".format(args.name, args.path, ", ".join([x.name for x in all_members.values()]))
        raise SystemExit(1)

    server = PipelineClass(args.name, concurrency=args.concurrency)
    server.run_bundle(args.sub_bind, args.pull_bind)
