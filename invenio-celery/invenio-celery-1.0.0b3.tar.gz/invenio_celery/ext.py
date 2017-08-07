# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Celery application for Invenio."""

from __future__ import absolute_import, print_function

import time

import pkg_resources
from celery.signals import import_modules
from flask_celeryext import FlaskCeleryExt

from . import config


class InvenioCelery(object):
    """Invenio celery extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        self.celery = None

        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, entry_point_group='invenio_celery.tasks',
                 **kwargs):
        """Initialize application object."""
        self.init_config(app)
        self.celery = FlaskCeleryExt(app).celery
        self.entry_point_group = entry_point_group
        app.extensions['invenio-celery'] = self

    def load_entry_points(self):
        """Load tasks from entry points."""
        if self.entry_point_group:
            task_packages = []
            for item in pkg_resources.iter_entry_points(
                    group=self.entry_point_group):
                task_packages.append(item.module_name)

            if task_packages:
                self.celery.autodiscover_tasks(
                    task_packages, related_name='', force=True
                )

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('CELERY_') or k.startswith('BROKER_'):
                app.config.setdefault(k, getattr(config, k))

    def get_queues(self):
        """Return a list of current active Celery queues."""
        res = self.celery.control.inspect().active_queues() or dict()
        return [result.get('name') for host in res.values() for result in host]

    def disable_queue(self, name):
        """Disable given Celery queue."""
        self.celery.control.cancel_consumer(name)

    def enable_queue(self, name):
        """Enable given Celery queue."""
        self.celery.control.add_consumer(name)

    def get_active_tasks(self):
        """Return a list of UUIDs of active tasks."""
        current_tasks = self.celery.control.inspect().active() or dict()
        return [
            task.get('id') for host in current_tasks.values() for task in host]

    def suspend_queues(self, active_queues, sleep_time=10.0):
        """Suspend Celery queues and wait for running tasks to complete."""
        for queue in active_queues:
            self.disable_queue(queue)
        while self.get_active_tasks():
            time.sleep(sleep_time)


@import_modules.connect()
def celery_module_imports(sender, signal=None, **kwargs):
    """Load shared celery tasks."""
    app = getattr(sender, 'flask_app', None)
    if app:
        app.extensions['invenio-celery'].load_entry_points()
