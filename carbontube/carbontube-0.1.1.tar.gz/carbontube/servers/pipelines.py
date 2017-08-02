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

import re
import sys
import time
import signal
import gevent
import gevent.pool
import logging
import gevent.monkey
import zmq.green as zmq
import GreenletProfiler
from gevent.event import Event
from speakers import Speaker
from agentzero import SocketManager
from carbontube.storage import EphemeralStorageBackend
from carbontube.models import Worker
from carbontube.models import Job
from carbontube.util import sanitize_name


class Pipeline(object):
    """Pipeline server class

    A pipeline must be defined only after you already at least one
    :py:class:`~carbontube.servers.Phase`.

    """

    def __init__(self, name, concurrency=10, backend_class=EphemeralStorageBackend):
        """
        :param name: the name of the pipeline
        :param concurrency: concurrency factor, the number of coroutines for phases is multiplied by it.
        :param backend_class: a subclass of :py:class:`carbontube.storage.base.BaseStorageBackend`
        """
        self.name = sanitize_name(name)
        self.actions = Speaker(
            'actions',
            [
                'available',
                'failed',
                'started',
                'finished',
                'success',
                'error',
                'logs',
            ]
        )
        self.concurrency = concurrency
        self.context = zmq.Context()
        self.sockets = SocketManager(zmq, self.context, polling_timeout=1, timeout=0.0001)
        self.backend_class = backend_class
        self.sockets.create('jobs-in', zmq.PULL)
        self.sockets.create('phase-events', zmq.SUB)
        # self.sockets.set_socket_option('jobs-in', zmq.RCVHWM, 1)
        self.sockets.set_socket_option('phase-events', zmq.RCVHWM, 1)

        self.connections = {}
        for action in self.actions.actions.keys():
            self.bind_action(action)

        self._allowed_to_run = Event()
        self._allowed_to_run.set()
        self.default_interval = 0.1
        self.logger = logging.getLogger('pipeline')
        self.pool = gevent.pool.Pool(concurrency)
        self.backend = self.backend_class(self.name)
        self.initialize()
        self.main_pool = gevent.pool.Pool(concurrency)

        signal.signal(signal.SIGABRT | signal.SIGFPE | signal.SIGILL | signal.SIGINT | signal.SIGSEGV | signal.SIGTERM, self.exit_gracefully)

    def initialize(self):
        """Initializes the backend.

        Subclasses can overload this in order to define their own
        backends.
        """

    def on_started(self, event):
        """called when a job just started processing.

        This method is ok to be overriden by subclasses in order to take
        action appropriate action.
        """
        worker = Worker.from_event(event)
        self.logger.info('%s [%s] started to process a job', worker.job_type, worker.id)

    def on_finished(self, event):
        """called when a job just finished processing. You can override this at will"""
        job = Job(event.data)
        self.handle_finished_job(job)

    def handle_finished_job(self, job):
        """called when a job just finished processing.

        When overriding this method make sure to call ``super()`` first
        """
        self.backend.report_job_completion(job)
        if 'error' in job:
            self.actions.error.shout(job)
            return False

        if bool(job.get('success')) is True:
            self.actions.success.shout(job)
        else:
            self.actions.failed.shout(job)
            return False

        self.logger.info('%s [%s] finished to process a job', job.type, job.id)
        return True

    def connect_to_worker(self, worker):
        self.sockets.ensure_and_connect(worker.address, zmq.PUSH, worker.address, zmq.POLLOUT)
        self.connections[worker.id] = time.time()

    def on_available(self, event):
        worker = Worker.from_event(event)
        self.backend.register_job_type(worker.job_type)
        self.backend.register_worker(worker)

        if worker.id not in self.connections:
            self.connect_to_worker(worker)
            self.logger.info('connected to worker: {phase_name}[{address}]'.format(**dict(worker)))

    def on_failed(self, job):
        self.logger.critical('%s [%s] failed: %s', job['job_type'], job['id'], job['error'])

    def on_success(self, job):
        self.logger.info('%s [%s] success', job['job_type'], job['id'])

    def on_error(self, job):
        self.logger.error('%s [%s] error: %s', job['job_type'], job['id'], job['error'])

    def on_logs(self, event):
        sys.stderr.write('\033[1;33m[from: {0}]\033[1;36m{msg}\033[0m'.format(event.topic, **event.data))
        sys.stderr.flush()

    def notify_entire_pipeline_completion(self, job_data):
        self.backend.report_pipeline_completion(job_data)

    def enqueue_next_job(self, data):
        instructions = data.get('instructions') or data
        if not instructions:
            self.logger.critical("missing instructions %s", instructions)
            gevent.sleep(0.001)
            return

        self.backend.report_job_running(data)
        phase_index = map(lambda phase: phase.job_type, self.phases).index(data['job_type'])

        try:
            next_job_type = self.phases[phase_index + 1].job_type
        except IndexError:
            self.notify_entire_pipeline_completion(data)
            return

        if next_job_type:
            job = Job.new(next_job_type, instructions.get('instructions') or instructions)
            self.logger.info("enqueuing next job: %s - %s", next_job_type, dict(job))
            self.backend.enqueue_job(job, 'enqueued')

    def bind_action(self, name, method=None):
        action = getattr(self.actions, name, None)
        if not action:
            raise KeyError('undefined action: {0}'.format(name))

        method = method or getattr(self, 'on_{0}'.format(name), None)
        if not method:
            raise TypeError('{0} does not have method {1}(self, topic, data)'.format(self.__class__, name))

        action(lambda _, event: method(event))

    def stop(self, *args, **kw):
        self.main_pool.kill()
        self._allowed_to_run.clear()

    def __del__(self):
        self.stop()

    def should_run(self):
        return self._allowed_to_run.is_set()

    def listen(
            self,
            sub_bind_address=None,
            pull_bind_address=None,
            pull_connect_addresses=[],
            sub_connect_addresses=[],
    ):
        if sub_bind_address:
            self.sockets.bind('phase-events', sub_bind_address, zmq.POLLIN)

        for address in sub_connect_addresses:
            self.sockets.connect('phase-events', address, zmq.POLLIN)

        if pull_bind_address:
            self.sockets.bind('jobs-in', pull_bind_address, zmq.POLLIN)

        for address in pull_connect_addresses:
            self.sockets.connect('jobs-in', address, zmq.POLLIN)

        self.logger.info('listening for events on %s', sub_bind_address or sub_connect_addresses)
        self.logger.info('listening for instructions on %s', pull_bind_address or pull_connect_addresses)
        self.backend.connect()
        self.backend.register_pipeline(self.name)
        for Phase in self.phases:
            self.backend.register_job_type(Phase.job_type)

    def route_event_internally(self, event):
        if not event:
            return

        ROUTES = map(lambda action: (re.compile(action), getattr(self.actions, action)),
                     self.actions.actions.keys())
        matched = False

        for regex, action in ROUTES:
            if regex.search(event.topic):
                action.shout(event)
                matched = True

        if not matched:
            self.logger.critical('unmatched event %s: %s', event.topic, event.data)

    def handle_pipeline_input(self, data):
        first_phase = self.phases[0].job_type

        job = Job.new(first_phase, data.get('instructions', {}))
        self.route_job_to_executer(job)

    def route_job_to_executer(self, job):
        self.backend.enqueue_job(job, 'enqueued')

    def drain_jobs_out(self):
        while self.should_run():
            self.drain_one_job_out()
            gevent.sleep(0.001)

    def drain_one_job_out(self):
        job = self.backend.consume_job()
        if not job:
            gevent.sleep(0.001)
            return

        self.logger.info('consuming job %s', job)
        job_type = job['job_type']
        worker = self.backend.get_next_available_worker_for_type(job_type)

        if not worker:
            self.logger.warning('re-queueing job {0}'.format(job_type))
            self.backend.enqueue_job(job, 'enqueued')
            gevent.sleep(0.001)
            return

        self.spawn(self.sockets.send_safe, worker.address, job.to_dict())
        self.logger.info('pushed job to worker %s [%s]', job_type, worker.address)

    def drain_one_job_in(self):
        data = self.sockets.recv_safe('jobs-in')
        if not data:
            return

        finished = 'job_finished_at' in data
        if finished:
            ok = self.handle_finished_job(Job(data))

        if finished and ok:
            # ensure there are instructions
            ok = 'instructions' in data

        if 'pipeline' in data:
            data.pop('pipeline')
            self.handle_pipeline_input(data)

        elif ok:
            self.backend.enqueue_job(data, 'success')
            self.enqueue_next_job(data)
        else:
            retries = data.get('retries', 0)
            retries += 1
            data['retries'] = retries

            # retry 2 times before setting as failed
            if retries < 2:
                self.backend.enqueue_job(data, 'enqueued')
            else:
                self.backend.enqueue_job(data, 'failed')

            self.logger.error(data['error']['traceback'])

    def drain_jobs_in(self):
        while self.should_run():
            self.drain_one_job_in()
            gevent.sleep(0.001)

    def spawn(self, *args, **kw):
        self.pool.spawn(*args, **kw)

    def clear_old_connections(self, seconds):
        for worker_id, last_seen in list(self.connections.items()):
            if time.time() - last_seen > seconds:
                self.connections.pop(worker_id, None)

    def loop(self, instrumented=False):
        if instrumented:
            GreenletProfiler.set_clock_type('wall')
            GreenletProfiler.start()
        for _ in range(16):
            self.dispatch_ins_and_outs()

        while self.should_run():
            self.loop_once()
            if instrumented:
                stats = GreenletProfiler.get_func_stats()
                stats.save('pipeline.{0}.callgrind'.format(self.__class__.__name__), type='callgrind')

            gevent.sleep(1)

    def dispatch_ins_and_outs(self):
        self.main_pool.spawn(self.drain_jobs_out)
        self.main_pool.spawn(self.process_events)
        self.main_pool.spawn(self.drain_jobs_in)
        self.main_pool.spawn(self.drain_jobs_in)

    def process_events(self):
        while self.should_run():
            event = self.sockets.recv_event_safe('phase-events')
            if event:
                self.route_event_internally(event)
                gevent.sleep(0.001)

    def loop_once(self):
        self.drain_one_job_in()
        self.clear_old_connections(seconds=300)

    def run(self, sub_bind_address='tcp://127.0.0.1:6000', pull_bind_address='tcp://127.0.0.1:7000', pull_connect_addresses=[], sub_connect_addresses=[]):
        self.listen(
            sub_bind_address=sub_bind_address,
            pull_bind_address=pull_bind_address,
            pull_connect_addresses=pull_connect_addresses,
            sub_connect_addresses=sub_connect_addresses,
        )
        self.loop()

    def exit_gracefully(self, *args, **kw):
        self.stop()
        raise SystemExit(0)
