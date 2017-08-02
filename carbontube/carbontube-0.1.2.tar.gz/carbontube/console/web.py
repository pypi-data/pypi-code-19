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

from carbontube.web import run_server
from carbontube.util import sanitize_name
from carbontube.console.base import get_sub_parser_argv


def execute_command_webserver():
    from carbontube.console.parsers.web import parser
    args = parser.parse_args(get_sub_parser_argv())
    print "browse at: http://{0}:{1}".format(args.host, args.port)
    run_server(args.host, args.port, pipeline_name=sanitize_name(args.pipeline), redis_uri=args.redis_uri, level=logging.INFO)
