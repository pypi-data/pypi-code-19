# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

"""Invenio accounts REST errors."""

from invenio_rest.errors import RESTException


class MaxResultWindowRESTError(RESTException):
    """Maximum number of results passed."""

    code = 400
    description = 'Maximum number of results have been reached.'


class PatchJSONFailureRESTError(RESTException):
    """Failed to patch JSON."""

    code = 400
    description = 'Could not patch JSON.'


class MissingOldPasswordError(RESTException):
    """Old password not provided while trying to change user password."""

    code = 400
    description = 'Missing field old_password.'
