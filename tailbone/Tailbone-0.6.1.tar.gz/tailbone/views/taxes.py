# -*- coding: utf-8 -*-
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
Tax Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView


class TaxesView(MasterView):
    """
    Master view for taxes.
    """
    model_class = model.Tax
    model_title_plural = "Taxes"
    route_prefix = 'taxes'

    def configure_grid(self, g):
        g.filters['description'].default_active = True
        g.filters['description'].default_verb = 'contains'
        g.default_sortkey = 'code'
        g.configure(
            include=[
                g.code,
                g.description,
                g.rate,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.code,
                fs.description,
                fs.rate,
            ])


def includeme(config):
    TaxesView.defaults(config)
