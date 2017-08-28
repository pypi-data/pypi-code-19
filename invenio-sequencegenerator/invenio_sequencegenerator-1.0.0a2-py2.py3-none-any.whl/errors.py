# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Errors for sequence generation."""

from __future__ import absolute_import, print_function


class SequenceGeneratorError(Exception):
    """Base class for errors in SequenceGenerator module."""


class SequenceNotFound(SequenceGeneratorError):
    """No such sequence error."""


class InvalidTemplate(SequenceGeneratorError):
    """Invalid template error."""

    def __init__(self, reason):
        """Initialize exception."""
        self.reason = reason

    def __str__(self):
        """String representation of error."""
        return self.reason


class InvalidResetCall(SequenceGeneratorError):
    """Invalid reset call error."""

    def __str__(self):
        """String representation of error."""
        return 'Cannot reset sequence: children exist'
