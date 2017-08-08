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
Views for "true" purchase credits
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone import forms
from tailbone.views import MasterView2 as MasterView


class PurchaseCreditView(MasterView):
    """
    Master view for purchase credits
    """
    model_class = model.PurchaseCredit
    route_prefix = 'purchases.credits'
    url_prefix = '/purchases/credits'
    creatable = False
    editable = False

    grid_columns = [
        'vendor',
        'invoice_number',
        'invoice_date',
        'upc',
        'brand_name',
        'description',
        'size',
        'cases_shorted',
        'units_shorted',
        'credit_type',
        'mispick_upc',
        'date_received',
        'status',
    ]

    def configure_grid(self, g):
        super(PurchaseCreditView, self).configure_grid(g)

        g.set_joiner('vendor', lambda q: q.outerjoin(model.Vendor))
        g.set_sorter('vendor', model.Vendor.name)

        g.default_sortkey = 'date_received'
        g.default_sortdir = 'desc'

        # g.set_type('upc', 'gpc')
        g.set_type('cases_shorted', 'quantity')
        g.set_type('units_shorted', 'quantity')

        g.set_label('invoice_number', "Invoice No.")
        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('cases_shorted', "Cases")
        g.set_label('units_shorted', "Units")
        g.set_label('credit_type', "Type")
        g.set_label('mispick_upc', "Mispick UPC")
        g.set_label('date_received', "Date")


def includeme(config):
    PurchaseCreditView.defaults(config)
