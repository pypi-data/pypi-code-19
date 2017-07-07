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
Views for pricing batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone import forms
from tailbone.views.batch import BatchMasterView


class PricingBatchView(BatchMasterView):
    """
    Master view for pricing batches.
    """
    model_class = model.PricingBatch
    model_row_class = model.PricingBatchRow
    default_handler_spec = 'rattail.batch.pricing:PricingBatchHandler'
    model_title_plural = "Pricing Batches"
    route_prefix = 'batch.pricing'
    url_prefix = '/batches/pricing'
    creatable = False
    rows_editable = True
    bulk_deletable = True

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id,
                fs.min_diff_threshold,
                fs.created,
                fs.created_by,
                fs.executed,
                fs.executed_by,
            ])

    def _preconfigure_row_grid(self, g):
        super(PricingBatchView, self)._preconfigure_row_grid(g)
        g.upc.set(label="UPC")
        g.brand_name.set(label="Brand")
        g.regular_unit_cost.set(label="Reg. Cost")
        g.discounted_unit_cost.set(label="Disc. Cost")
        g.old_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        g.new_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        g.price_margin.set(label="Margin")
        g.price_markup.set(label="Markup")
        g.price_diff.set(label="Diff", renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_row_grid(self, g):
        g.configure(
            include=[
                g.sequence,
                g.upc,
                g.brand_name,
                g.description,
                g.size,
                g.discounted_unit_cost,
                g.old_price,
                g.new_price,
                g.price_margin,
                g.price_diff,
                g.status_code,
            ],
            readonly=True)

    def row_grid_row_attrs(self, row, i):
        attrs = {}
        if row.status_code in (row.STATUS_PRICE_INCREASE,
                               row.STATUS_PRICE_DECREASE):
            attrs['class_'] = 'notice'
        elif row.status_code == row.STATUS_CANNOT_CALCULATE_PRICE:
            attrs['class_'] = 'warning'
        return attrs

    def _preconfigure_row_fieldset(self, fs):
        super(PricingBatchView, self)._preconfigure_row_fieldset(fs)
        fs.upc.set(label="UPC")
        fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer)
        fs.old_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.new_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.price_diff.set(renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_row_fieldset(self, fs):
        fs.configure(
            include=[
                fs.sequence,
                fs.product,
                fs.upc,
                fs.brand_name,
                fs.description,
                fs.size,
                fs.department_number,
                fs.department_name,
                fs.vendor,
                fs.regular_unit_cost,
                fs.discounted_unit_cost,
                fs.old_price,
                fs.new_price,
                fs.price_diff,
                fs.price_margin,
                fs.price_markup,
                fs.status_code,
                fs.status_text,
            ])


def includeme(config):
    PricingBatchView.defaults(config)
