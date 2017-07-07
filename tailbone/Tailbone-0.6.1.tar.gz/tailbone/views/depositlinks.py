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
Deposit Link Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone import forms
from tailbone.views import MasterView


class DepositLinksView(MasterView):
    """
    Master view for deposit links.
    """
    model_class = model.DepositLink
    url_prefix = '/deposit-links'

    def _preconfigure_grid(self, g):
        g.filters['description'].default_active = True
        g.filters['description'].default_verb = 'contains'
        g.default_sortkey = 'code'
        g.amount.set(renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_grid(self, g):
        g.configure(
            include=[
                g.code,
                g.description,
                g.amount,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.code,
                fs.description,
                fs.amount,
            ])


def includeme(config):
    DepositLinksView.defaults(config)
