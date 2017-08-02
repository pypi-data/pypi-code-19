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

import logging
import argparse
import warnings
import coloredlogs

from carbontube.console.base import get_main_parser_argv
from carbontube.console.base import execute_command_version
from carbontube.console.web import execute_command_webserver
from carbontube.console.servers import execute_command_run_pipeline
from carbontube.console.servers import execute_command_run_bundle
from carbontube.console.servers import execute_command_run_phase
from carbontube.console.servers import execute_command_forwarder
from carbontube.console.servers import execute_command_streamer
from carbontube.console.clients import execute_command_enqueue


warnings.catch_warnings()
warnings.simplefilter("ignore")


def entrypoint():
    handlers = {
        'web': execute_command_webserver,
        'phase': execute_command_run_phase,
        'bundle': execute_command_run_bundle,
        'version': execute_command_version,
        'enqueue': execute_command_enqueue,
        'streamer': execute_command_streamer,
        'pipeline': execute_command_run_pipeline,
        'forwarder': execute_command_forwarder,
    }
    parser = argparse.ArgumentParser(prog='carbontube')
    options = ", ".join(handlers.keys())
    help_msg = 'Available commands:\n\n{0}\n'.format(options)

    parser.add_argument('command', help=help_msg, choices=handlers.keys())

    argv = get_main_parser_argv()

    args = parser.parse_args(argv)

    # enabling colored logs by default ;)
    coloredlogs.install(level=logging.INFO, show_hostname=False)

    if args.command not in handlers:
        parser.print_help()
        raise SystemExit(1)

    try:
        handlers[args.command]()
    except KeyboardInterrupt:
        print "\033[A\r                        "
        print "\033[A\r\rYou hit Control-C. Bye"
        raise SystemExit(1)

    except Exception:
        logging.exception("Failed to execute %s", args.command)
        raise SystemExit(1)


def __main__():
    entrypoint()

if __name__ == '__main__':
    entrypoint()
