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
import uuid
import json
import logging
import coloredlogs
import gevent.pool
from gevent import pywsgi
from plant import Node
from flask import Flask, render_template, Response
from carbontube.storage import RedisStorageBackend


node = Node(__file__)
server = Flask(
    __name__,
    static_folder=node.dir.join('dist'),
    template_folder=node.dir.join('templates'),
)


def json_response(data, code=200, headers={}):
    serialized = json.dumps(data, indent=2)
    headers[b'Content-Type'] = 'application/json'
    return Response(serialized, status=code, headers=headers)


@server.route("/")
def index():
    return render_template('index.html')


@server.route("/api/pipelines")
def api_pipelines():
    data = server.backend.list_pipelines()
    print "pipelines", data
    return json_response(data)


@server.route("/api/queues")
def api_queues():
    data = server.backend.list_job_types()
    print "queues", data
    return json_response(data)


@server.route("/api/workers/available")
def api_workers_available():
    data = sorted(map(dict, server.backend.list_all_available_workers()), key=lambda w: w['checkin'])
    return json_response(data)


@server.route("/api/jobs")
def api_jobs_by_type():
    payload = server.backend.retrieve_jobs()
    return json_response(payload)


def run_server(host, port, pipeline_name, redis_uri, level=logging.INFO, debug=True, secret_key=None, concurrency=10):
    coloredlogs.install(level=level)
    server.debug = debug
    server.backend = RedisStorageBackend(pipeline_name, redis_uri=redis_uri)
    server.backend.connect()
    server.config['SECRET_KEY'] = secret_key or bytes(uuid.uuid4())
    pool = gevent.pool.Pool(concurrency)
    green_server = pywsgi.WSGIServer(
        (host, port),
        server,
        spawn=pool
    )
    green_server.serve_forever()
