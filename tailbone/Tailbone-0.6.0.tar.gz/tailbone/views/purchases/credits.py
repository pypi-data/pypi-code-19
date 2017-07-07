# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for "true" purchase credits
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone import forms
from tailbone.views import MasterView


class PurchaseCreditView(MasterView):
    """
    Master view for purchase credits
    """
    model_class = model.PurchaseCredit
    route_prefix = 'purchases.credits'
    url_prefix = '/purchases/credits'
    creatable = False
    editable = False

    def _preconfigure_grid(self, g):

        g.joiners['vendor'] = lambda q: q.outerjoin(model.Vendor)
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

        g.default_sortkey = 'date_received'
        g.default_sortdir = 'desc'

        g.upc.set(label="UPC")
        g.brand_name.set(label="Brand")
        g.cases_shorted.set(label="Cases", renderer=forms.renderers.QuantityFieldRenderer)
        g.units_shorted.set(label="Units", renderer=forms.renderers.QuantityFieldRenderer)
        g.credit_type.set(label="Type")
        g.date_received.set(label="Date")

    def configure_grid(self, g):
        g.configure(
            include=[
                g.vendor,
                g.upc,
                g.brand_name,
                g.description,
                g.size,
                g.cases_shorted,
                g.units_shorted,
                g.credit_type,
                g.date_received,
                g.status,
            ],
            readonly=True)


def includeme(config):
    PurchaseCreditView.defaults(config)
