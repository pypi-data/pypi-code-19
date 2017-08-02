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

import os
import time
import uuid
import logging
import gevent
import gevent.pool
import gevent.monkey
import zmq.green as zmq
import GreenletProfiler
from greenlet import GreenletExit
from gevent.event import Event
from agentzero.util import serialized_exception
from agentzero import SocketManager
from carbontube.util import parse_port


def extract_instructions(job):
    job = dict(job.items())
    while 'instructions' in job:
        job = job['instructions']

    return job


class Phase(object):
    def __init__(
            self,
            pull_bind_address='tcp://127.0.0.1',
            pub_connect_address='tcp://127.0.0.1:6000',
            concurrency=10,
            timeout=1,
            pull_connect_addresses=[],
            push_connect_addresses=[],
            publish_logs=False,
    ):
        self.context = zmq.Context()
        self.sockets = SocketManager(zmq, self.context, polling_timeout=1, timeout=0.0001)
        self.sockets.create('pull', zmq.PULL)
        self.sockets.create('push', zmq.PUSH)
        self.sockets.create('events', zmq.PUB)
        self.sockets.set_socket_option('pull', zmq.RCVHWM, 1)
        self.sockets.set_socket_option('push', zmq.SNDHWM, 1)
        self.sockets.set_socket_option('events', zmq.SNDHWM, 1)

        self.pool = gevent.pool.Pool(concurrency)
        self.name = self.__class__.__name__
        self.pub_connect_address = pub_connect_address
        self.pull_connect_addresses = pull_connect_addresses
        self.push_connect_addresses = push_connect_addresses
        self._allowed_to_run = Event()
        self._allowed_to_run.set()
        self.timeout = timeout
        self.pull_bind_address = pull_bind_address
        self.id = str(uuid.uuid4())
        if publish_logs:
            self.logger = self.get_zmq_logger()
        else:
            self.logger = logging.getLogger('carbontube')

        self.port = parse_port(pull_bind_address)
        self.pull_bind_address = pull_bind_address
        self.publish_logs = publish_logs
        self.address = None
        self.success_count = 0
        self.failed_count = 0

    def get_zmq_logger(self):
        self.sockets.create('logger', zmq.PUB)
        self.sockets.set_socket_option('logger', zmq.SNDHWM, 1)
        return self.sockets.get_logger('logger', ':'.join([self.job_type, 'logs']))

    def listen(self):
        if self.port:
            self.address = self.pull_bind_address
            self.sockets.bind('pull', self.address, zmq.POLLIN)

        else:
            _, self.address = self.sockets.bind_to_random_port('pull', zmq.POLLIN, local_address=self.pull_bind_address)

        self.logger.info('[%s] listening for jobs on %s', self.job_type, self.address)

    def connect(self):
        if self.publish_logs:
            self.sockets.connect('logger', self.pub_connect_address, zmq.POLLOUT)

        self.sockets.connect('events', self.pub_connect_address, zmq.POLLOUT)
        for address in self.pull_connect_addresses:
            self.sockets.connect('pull', address, zmq.POLLIN)

        for address in self.push_connect_addresses:
            self.sockets.connect('push', address, zmq.POLLOUT)

        self.notify_available()
        self.logger.info('[%s] publishing events at %s', self.job_type, self.pub_connect_address)

    def notify_available(self):
        self.send_event('available', self.to_dict())

    def should_run(self):
        return self._allowed_to_run.is_set()

    def stop(self, *args, **kw):
        self._allowed_to_run.clear()

    def send_event(self, name, data):
        self.sockets.publish_safe('events', name, data)

    def dispatch(self, job):
        try:
            start = time.time()
            job['job_started_at'] = start
            instructions = extract_instructions(job)
            if 'instructions' in job['instructions']:
                instructions = job['instructions']['instructions']
            else:
                instructions = job['instructions']

            result = self.execute(instructions)
            if result:
                job['instructions'].update(result)

        except Exception as e:
            job['error'] = serialized_exception(e)
            self.logger.exception('failed to execute job {id}'.format(**dict(job)))

        finally:
            job['job_finished_at'] = time.time()

        if 'error' not in job:
            job['success'] = True
            self.success_count += 1
        else:
            job['success'] = False
            self.failed_count += 1

        self.notify_job_finished(job)
        self.logger.info("done processing %s", job)
        raise GreenletExit()

    def notify_job_finished(self, job):
        self.sockets.send_safe('push', job)

    def to_dict(self):
        if not self.address:
            address = 'offline'

        else:
            address = self.address

        return dict(
            id=self.id,
            address=address,
            job_type=self.job_type,
            phase_name=self.name,
            success_count=self.success_count,
            failed_count=self.failed_count,
        )

    def keep_alive_loop(self):
        while self.should_run():
            self.notify_available()
            gevent.sleep(1)

    def loop(self, instrumented=False):
        if instrumented:
            GreenletProfiler.set_clock_type('wall')
            GreenletProfiler.start()
        self.pool.spawn(self.keep_alive_loop)
        while self.should_run():
            job = self.sockets.recv_safe('pull')

            if job:
                self.logger.warning('[%s] received job', self)
                self.pool.spawn(self.dispatch, job)

            self.pool.join(0.1)
            if instrumented:
                stats = GreenletProfiler.get_func_stats()
                stats.save('phase.{0}.{1}.callgrind'.format(self.__class__.__name__, os.getpid()), type='callgrind')

            gevent.sleep(0.01)

    def __repr__(self):
        return '{0}(job_type="{1}")'.format(self.__class__.__name__, self.job_type)

    def run(self):
        self.listen()
        self.connect()
        self.loop()

    def exit_gracefully(self, *args, **kw):
        self.stop()
        raise SystemExit(0)
