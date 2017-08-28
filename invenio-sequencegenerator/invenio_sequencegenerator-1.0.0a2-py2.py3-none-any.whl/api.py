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

"""User-level API."""

from __future__ import absolute_import, print_function

from invenio_db import db
from werkzeug.utils import cached_property

from .errors import SequenceNotFound
from .models import TemplateDefinition


class Template(object):
    """API for defining sequences."""

    def __init__(self, name, _model=None):
        """Initialize template.

        :param name: The identifier of the template.
        :param _model: The model object of the template.
        """
        self.model = _model or TemplateDefinition.query.get(name)
        if self.model is None:
            raise SequenceNotFound()
        assert name == self.model.name

    @classmethod
    def create(cls, name, meta_template, start=0, step=1):
        """Create a new sequence definition.

        :param name: The identifier of the template definition.
        :param meta_template: The template generator.
        :param start: The starting counter of sequences based on this template.
        :param step: The incremental step of sequences based on this template.
        """
        with db.session.begin_nested():
            definition = TemplateDefinition(
                name=name, meta_template=meta_template, start=start, step=step
            )
            db.session.add(definition)
        return cls(name, _model=definition)


class Sequence(object):
    """Iterator for sequences."""

    def __init__(self, template, **kwargs):
        r"""Initialize.

        :param template: The template that this sequence is based on.
        :param \**kwargs: The kwargs to instantiate the template.
        """
        if not isinstance(template, Template):
            template = Template(template)
        self.template = template
        self.kwargs = kwargs

    @cached_property
    def counter(self):
        """Cache internal counter."""
        return self.template.model.counter(**self.kwargs)

    def next(self):  # Python 2.x
        """Get next identifier."""
        return self.counter.increment()

    def __next__(self):  # Python 3.x
        """Get next identifier."""
        return self.next()

    def __iter__(self):
        """Enable iterative capabilities."""
        return self
