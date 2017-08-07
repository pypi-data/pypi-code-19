# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015, 2016, 2017 CERN.
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

"""Default configuration values for Celery integration.

For further Celery configuration variables see
`Celery <http://docs.celeryproject.org/en/3.1/configuration.html>`_
documentation.
"""

BROKER_URL = 'redis://localhost:6379/0'
CELERY_BROKER_URL = BROKER_URL  # For Celery 4
"""Broker settings."""

CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
"""The backend used to store task results."""

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
"""A whitelist of content-types/serializers."""

CELERY_RESULT_SERIALIZER = 'msgpack'
"""Result serialization format. Default is ``msgpack``."""

CELERY_TASK_SERIALIZER = 'msgpack'
"""The default serialization method to use. Default is ``msgpack``."""
