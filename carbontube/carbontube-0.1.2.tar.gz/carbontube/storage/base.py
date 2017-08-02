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


class BaseStorageBackend(object):
    """base class for storage backends"""
    def __init__(self, name, *args, **kw):
        self.pipeline_name = name
        self.initialize(*args, **kw)

    def initialize(self):
        """backend-specific constructor. This method must be overriden by subclasses
        in order to setup database connections and such"""

    def connect(self):
        """this method is called by the pipeline once it started to listen on
        zmq sockets, so this is also an appropriate time to implement
        your own connection to a database in a backend subclass pass
        """

    def register_worker(self, worker):
        """register the worker as available. must return a boolean. True if
        the worker was successfully registered, False otherwise"""
        return True

    def unregister_worker(self, worker):
        """unregisters the worker completely, removing it from the roster"""

    def enqueue_job(self, job):
        """adds the job to its appropriate queue name"""

    def consume_job_of_type(self, job_type):
        """dequeues a job for the given type. must return None when no job is
        ready.

        Make sure to requeue this job in case it could not be fed into
        an immediate worker.
        """

    def get_next_available_worker_for_type(self, job_type):
        """randomly picks a workers that is currently available"""
