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

import re
import json

from carbontube.clients import PipelineClient
from carbontube.console.base import get_sub_parser_argv
from carbontube.console.base import bootstrap_conf_with_gevent


def execute_command_enqueue():
    """executes an instance of the pipeline manager server.

    ::

      $ carbontube enqueue tcp://0.0.0.0:5050 <pipeline-name> [json instructions]

    """

    from carbontube.console.parsers.enqueue import parser
    args = parser.parse_args(get_sub_parser_argv())
    bootstrap_conf_with_gevent(args)

    client = PipelineClient(args.address)
    client.connect()

    job = {
        'pipeline': re.sub(r'[^a-zA-Z0-1]+', '_', args.name),
        'instructions': json.loads(args.instructions)
    }
    ok, payload = client.enqueue_job(job)
    if ok:
        print "enqueued", json.dumps(payload, indent=2)
    else:
        print "FAILED TO SEND"
