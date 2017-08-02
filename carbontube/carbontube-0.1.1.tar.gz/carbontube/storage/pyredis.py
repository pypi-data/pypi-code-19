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
import time
import json
import redis
import hashlib
import random
import dj_redis_url
from datetime import datetime
from carbontube.models import Job, Worker
from carbontube.util import sanitize_name, read_internal_file
from carbontube.storage.base import BaseStorageBackend


class JobNotFound(Exception):
    pass


def dt_to_string(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def utc_now_string():
    return dt_to_string(datetime.utcnow())


def read_lua_script(name):
    """reads a lua script from "carbontube/storage/redis-lua-scripts/<name>"""
    path = 'storage/redis-lua-scripts/{0}'.format(name)
    return read_internal_file(path).strip()


def create_new_pool_from_uri(redis_uri):
    parts = dj_redis_url.parse(redis_uri)
    if not parts:
        raise RuntimeError('invalid uri: {0}'.format(repr(redis_uri)))

    params = dict(map((lambda (k, v): (k.lower(), v)),
                      parts.items()))

    return redis.ConnectionPool(**params)


class KeyManager(object):
    PREFIX = 'carbontube'

    JOB_STATES = {
        "enqueued",
        "running",
        "success",
        "failed",
    }

    def __init__(self, name):
        self.name = sanitize_name(name)

    def prefix(self, *parts):
        items = [self.PREFIX]
        items.extend(parts)
        return ":".join(items)

    def join(self, *parts):
        return self.prefix(self.name, *parts)

    def mainstream(self):
        return self.join('mainstream')

    def sink(self):
        return self.join('sink')

    def available_worker(self, worker_id):
        return self.join('worker', 'available', worker_id)

    def worker_of_job_type(self, job_type):
        return self.join('worker', 'job_type', job_type)

    def job_type_queue(self, job_type, state):
        return self.join('queue', state, 'job_type', job_type)

    def jobs_hash(self):
        return self.join('persisted_jobs')

    def every_other_state_queue(self, job_type, state):
        other_states = self.JOB_STATES.difference({state})
        return [self.job_type_queue(job_type, s) for s in other_states]

    def known_pipelines(self):
        return self.prefix('known_pipelines')

    def known_job_types(self):
        return self.prefix('known_job_types')


class RedisStorageBackend(BaseStorageBackend):
    """Redis Storage Backend"""

    def initialize(self, redis_uri='redis://', worker_availability_timeout=300):
        self.keys = KeyManager(self.pipeline_name)
        self.pool = None
        self.redis_uri = redis_uri
        self.worker_availability_timeout = worker_availability_timeout

    def serialize(self, data):
        if isinstance(data, dict):
            data = dict(data)

        return json.dumps(data)

    def deserialize(self, data):
        return json.loads(data)

    @property
    def redis(self):
        if not self.pool:
            raise RuntimeError('the RedisStorageBackend can only be used after .connect() was called')

        return redis.StrictRedis(connection_pool=self.pool)

    def connect(self):
        self.pool = create_new_pool_from_uri(self.redis_uri)

    def register_worker(self, worker):
        worker['checkin'] = time.time()
        available_key = self.keys.available_worker(worker.id)
        type_key = self.keys.worker_of_job_type(worker.job_type)

        pipe = self.redis.pipeline()
        pipe = pipe.setex(available_key, self.worker_availability_timeout, self.serialize(worker))
        pipe = pipe.sadd(type_key, worker.id)
        return pipe.execute()[0]

    def unregister_worker(self, worker):
        available_key = self.keys.available_worker(worker.id)
        type_key = self.keys.worker_of_job_type(worker.job_type)

        pipe = self.redis.pipeline()
        pipe = pipe.delete(available_key)
        pipe = pipe.srem(type_key, worker.id)
        return pipe.execute()

    def enqueue_job(self, job, state):
        if state not in self.keys.JOB_STATES:
            raise RuntimeError('invalid state: {0} ({1})'.format(state, self.keys.JOB_STATES))
        job_id = job['id']
        job_type = job['job_type']

        pipe = self.redis.pipeline()

        job['state'] = state

        if state == 'running':
            job['started_at'] = time.time()

        if state == 'enqueued':
            pipe.rpush(self.keys.mainstream(), job_id)
            pipe = pipe.rpush(self.keys.job_type_queue(job_type, state), job_id)
            job['enqueued_at'] = time.time()

        else:
            pipe = pipe.rpush(self.keys.job_type_queue(job_type, state), job_id)

        serialized_job = self.serialize(dict(job))
        pipe = pipe.hset(self.keys.jobs_hash(), job_id, serialized_job)
        return pipe.execute()

    def consume_job(self):
        key = self.keys.mainstream()

        job_id = self.redis.lpop(key)

        if job_id:
            data = self.redis.hget(self.keys.jobs_hash(), job_id)
            job = Job(self.deserialize(data))

            self.enqueue_job(job, 'running')
            return job

    def register_pipeline(self, name):
        self.redis.sadd(self.keys.known_pipelines(), name)

    def list_pipelines(self):
        return list(self.redis.smembers(self.keys.known_pipelines()))

    def register_job_type(self, name):
        self.redis.sadd(self.keys.known_job_types(), name)

    def list_job_types(self):
        return list(self.redis.smembers(self.keys.known_job_types()))

    def list_available_workers_keys(self):
        keys = self.redis.keys(self.keys.available_worker('*'))
        return keys

    def list_keys_for_workers_of_type(self, job_type):
        type_key = self.keys.worker_of_job_type(job_type)
        return self.redis.smembers(type_key)

    def retrieve_all_workers_by_keys(self, keys):
        pipeline = self.redis.pipeline()

        for key in keys:
            pipeline = pipeline.get(key)

        return map(Worker, map(self.deserialize, filter(bool, pipeline.execute())))

    def get_next_available_worker_for_type(self, job_type):
        keys = map(self.keys.available_worker, self.list_keys_for_workers_of_type(job_type))
        found = list(sorted(self.retrieve_all_workers_by_keys(keys), key=lambda x: x['checkin'], reverse=True))
        if found:
            return found[-1]

    def list_all_available_workers(self):
        items = self.retrieve_all_workers_by_keys(self.list_available_workers_keys())
        return self.sort_by_id(items)

    def retrieve_jobs(self):
        job_types = self.list_job_types()
        job_states = list(self.keys.JOB_STATES)

        result = {}
        for state_name in job_states:
            by_type = {}
            for type_name in job_types:
                key = self.keys.job_type_queue(type_name, state_name)
                items = self.sort_by_id(map(self.deserialize, map(lambda job_id: self.get_job_by_id(job_id), self.redis.lrange(key, 0, -1))))
                by_type[type_name] = items

            result[state_name] = by_type

        key = self.keys.mainstream()
        result['mainstream'] = map(self.deserialize, map(lambda job_id: self.get_job_by_id(job_id), self.redis.lrange(key, 0, -1)))
        result['sink'] = self.get_finished_jobs()
        return result

    def get_job_by_id(self, job_id):
        key = self.keys.jobs_hash()
        return self.redis.hget(key, job_id)

    def sort_by_id(self, items):
        return sorted(items, key=lambda x: x['id'])

    def report_job_running(self, data):
        job_id = data['id']
        job_type = data['job_type']
        running_key = self.keys.job_type_queue(job_type, 'running')
        self.redis.lrem(running_key, 0, job_id)

    def report_job_completion(self, data):
        job_id = data['id']
        job_type = data['job_type']
        success = data.get('success', False)
        state = success and 'success' or 'failed'
        running_key = self.keys.job_type_queue(job_type, state)
        self.redis.lrem(running_key, 0, job_id)

    def report_pipeline_completion(self, data):
        pipe = self.redis.pipeline()
        pipe.lpush(self.keys.sink(), json.dumps(data))
        return pipe.execute()

    def get_finished_jobs(self):
        return map(json.loads, filter(bool, self.redis.lrange(self.keys.sink(), 0, -1)))


def sha1(data):
    return hashlib.sha1(data).hexdigest()


class LuaBridge(object):
    scripts = {
        'enqueue': read_lua_script('enqueue.lua'),
        'consume': read_lua_script('consume.lua'),
        'consume_by_type': read_lua_script('consume-by-type.lua'),
        'list_pending': read_lua_script('list-pending-jobs.lua'),
        'list_pending_by_type': read_lua_script('list-pending-jobs-by-type.lua'),
    }

    def __init__(self, parent):
        self.hashes = dict([(n, sha1(s)) for n, s in self.scripts.items()])
        self.actions = {}
        self.parent = parent

    def register_script(self, name, script):
        self.actions[name] = self.redis.register_script(script)

    def register_all_scripts(self):
        for name, script in self.scripts.items():
            self.register_script(name, script)

    @property
    def redis(self):
        return self.parent.redis

    def execute(self, name, *args):
        action = self.actions.get(name)
        if not action:
            raise RuntimeError('unregistered action: {0}'.format(name))

        return action(keys=[], args=args, client=self.redis)


class RedisJobStorage(RedisStorageBackend):

    def initialize(self, redis_uri='redis://', worker_availability_timeout=300):
        self.keys = KeyManager(self.pipeline_name)
        self.pool = None
        self.redis_uri = redis_uri
        self.worker_availability_timeout = worker_availability_timeout
        self.lua = LuaBridge(self)

    def connect(self):
        self.pool = create_new_pool_from_uri(self.redis_uri)
        self.lua.register_all_scripts()

    def enqueue(self, pipeline_name, job):
        args = [
            job['id'],
            job['job_type'],
            pipeline_name,
            json.dumps(dict(job)),
        ]
        return self.lua.execute('enqueue', *args)

    def list_pending_jobs_of_type(self, pipeline_name, job_type):
        args = [
            pipeline_name,
            job_type
        ]
        result = self.lua.execute('list_pending_by_type', *args)
        return map(json.loads, filter(bool, result))

    def list_pending_jobs(self, pipeline_name):
        args = [
            pipeline_name,
        ]
        result = self.lua.execute('list_pending', *args)
        return map(json.loads, filter(bool, result))

    def consume(self, pipeline_name):
        args = [
            pipeline_name,
        ]
        result = self.lua.execute('consume', *args)
        return json.loads(result)

    def consume_by_type(self, pipeline_name, job_type):
        args = [
            pipeline_name,
            job_type,
        ]
        result = self.lua.execute('consume_by_type', *args)
        return json.loads(result)
