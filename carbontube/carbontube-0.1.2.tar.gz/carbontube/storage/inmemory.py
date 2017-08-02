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

import random

from collections import defaultdict
from carbontube.storage.base import BaseStorageBackend


class EphemeralStorageBackend(BaseStorageBackend):
    """in-memory storage backend. It dies with the process and has no
    option for persistence whatsoever. Used only for testing purposes."""

    def initialize(self):
        self.workers = {}
        self.workers_by_job_type = defaultdict(set)
        self.jobs_by_type = defaultdict(list)

    def connect(self):
        pass

    def register_worker(self, worker):
        if worker.id in self.workers:
            # already registered
            return False

        self.workers[worker.id] = worker
        self.workers_by_job_type[worker.job_type].add(worker.id)
        return True

    def unregister_worker(self, worker):
        self.workers.pop(worker.id, None)
        self.workers_by_job_type[worker.job_type].remove(worker.id)

    def enqueue_job(self, job):
        self.jobs_by_type[job.type].append(job)

    def consume_job_of_type(self, job_type):
        try:
            return self.jobs_by_type[job_type].pop(0)
        except IndexError:
            return None

    def get_next_available_worker_for_type(self, job_type):
        worker_ids = list(self.workers_by_job_type[job_type])
        if not worker_ids:
            return None

        try:
            wid = random.choice(worker_ids)
            return self.workers.get(wid)
        except KeyError:
            return None
