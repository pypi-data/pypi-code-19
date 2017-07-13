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
Trainwreck views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.time import localtime

from tailbone import forms
from tailbone.db import TrainwreckSession
from tailbone.views import MasterView


class TransactionView(MasterView):
    """
    Master view for Trainwreck transactions
    """
    Session = TrainwreckSession
    # model_class = trainwreck.Transaction
    model_title = "Trainwreck Transaction"
    model_title_plural = "Trainwreck Transactions"
    route_prefix = 'trainwreck.transactions'
    url_prefix = '/trainwreck/transactions'
    creatable = False
    editable = False
    deletable = False

    has_rows = True
    # model_row_class = trainwreck.TransactionItem
    rows_default_pagesize = 100

    def _preconfigure_grid(self, g):
        g.filters['receipt_number'].default_active = True
        g.filters['receipt_number'].default_verb = 'equal'
        g.filters['start_time'].default_active = True
        g.filters['start_time'].default_verb = 'equal'
        g.filters['start_time'].default_value = six.text_type(localtime(self.rattail_config).date())
        g.default_sortkey = 'start_time'
        g.default_sortdir = 'desc'

        g.system.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.TRAINWRECK_SYSTEM))
        g.terminal_id.set(label="Terminal")
        g.receipt_number.set(label="Receipt No.")
        g.customer_id.set(label="Customer ID")
        g.total.set(renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_grid(self, g):
        g.configure(
            include=[
                g.start_time,
                g.system,
                g.terminal_id,
                g.receipt_number,
                g.customer_id,
                g.customer_name,
                g.total,
            ],
            readonly=True)

    def _preconfigure_fieldset(self, fs):
        fs.system.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.TRAINWRECK_SYSTEM))
        fs.terminal_id.set(label="Terminal")
        fs.customer_id.set(label="Customer No.")
        fs.shopper_id.set(label="Shopper No.")
        fs.subtotal.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.discounted_subtotal.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.tax.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.total.set(renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_fieldset(self, fs):
        fs.configure(include=[
            fs.system,
            fs.terminal_id,
            fs.receipt_number,
            fs.start_time,
            fs.end_time,
            fs.customer_id,
            fs.customer_name,
            fs.shopper_id,
            fs.shopper_name,
            fs.subtotal,
            fs.discounted_subtotal,
            fs.tax,
            fs.total,
            fs.void,
        ])

    def get_row_data(self, transaction):
        return self.Session.query(self.model_row_class)\
                           .filter(self.model_row_class.transaction == transaction)\
                           .order_by(self.model_row_class.sequence)

    def get_parent(self, item):
        return item.transaction

    def _preconfigure_row_grid(self, g):
        g.default_sortkey = 'sequence'

        g.item_id.set(label="Item ID")
        g.department_number.set(label="Dept. No.")
        g.unit_quantity.set(renderer=forms.renderers.QuantityFieldRenderer)
        g.subtotal.set(renderer=forms.renderers.CurrencyFieldRenderer)
        g.discounted_subtotal.set(renderer=forms.renderers.CurrencyFieldRenderer)
        g.tax.set(renderer=forms.renderers.CurrencyFieldRenderer)
        g.total.set(renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_row_grid(self, g):
        g.configure(
            include=[
                g.sequence,
                g.item_type,
                g.item_id,
                g.department_number,
                g.description,
                g.unit_quantity,
                g.subtotal,
                g.tax,
                g.total,
                g.void,
            ],
            readonly=True)

    def _preconfigure_row_fieldset(self, fs):
        fs.item_id.set(label="Item ID")
        fs.department_number.set(label="Dept. No.")
        fs.unit_quantity.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.subtotal.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.discounted_subtotal.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.tax.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.total.set(renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_row_fieldset(self, fs):
        fs.configure(include=[
            fs.sequence,
            fs.item_type,
            fs.item_id,
            fs.department_number,
            fs.description,
            fs.unit_quantity,
            fs.subtotal,
            fs.tax,
            fs.total,
            fs.void,
        ])
