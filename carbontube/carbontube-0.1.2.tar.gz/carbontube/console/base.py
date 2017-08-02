#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import json
import coloredlogs
import logging
import argparse
import gevent.monkey

from carbontube.version import version

logger = logging.getLogger('carbontube')


def bootstrap_conf_with_gevent(args, loglevel=logging.INFO):
    gevent.monkey.patch_all(thread=True, select=True, subprocess=True)
    coloredlogs.install(loglevel)
    try:
        conf_path = args.conf
    except AttributeError:
        conf_path = None

    if conf_path:
        os.environ['CARBONTUBE_CONFIG_PATH'] = conf_path


def get_sub_parser_argv():
    argv = sys.argv[2:]
    return argv


def get_main_parser_argv():
    argv = sys.argv[1:2]
    return argv


def execute_command_version():
    parser = argparse.ArgumentParser(
        prog='carbontube version --json',
        description='prints the software version')

    parser.add_argument('--json', action='store_true', default=False, help='shows the version as a json')

    args = parser.parse_args(get_sub_parser_argv())

    if args.json:
        print json.dumps({'version': version, 'name': 'CarbonTube'}, indent=2)
    else:
        print "CarbonTube", 'v{0}'.format(version)
