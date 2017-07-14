# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Settings Views
"""

from __future__ import unicode_literals, absolute_import

import re

from rattail.db import model

import formalchemy as fa

from tailbone.db import Session
from tailbone.views import MasterView2 as MasterView


def unique_name(value, field):
    setting = Session.query(model.Setting).get(value)
    if setting:
        raise fa.ValidationError("Setting name must be unique")


class SettingsView(MasterView):
    """
    Master view for the settings model.
    """
    model_class = model.Setting
    feedback = re.compile(r'^rattail\.mail\.user_feedback\..*')
    grid_columns = [
        'name',
        'value',
    ]

    def configure_grid(self, g):
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.default_sortkey = 'name'
        g.set_link('name')

    def _preconfigure_fieldset(self, fs):
        fs.name.set(validate=unique_name)
        if self.editing:
            fs.name.set(readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(include=[
            fs.name,
            fs.value,
        ])

    def editable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True

    def deletable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True


def includeme(config):
    SettingsView.defaults(config)
