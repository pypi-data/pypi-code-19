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
Views for inventory batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import formalchemy as fa

from tailbone import forms
from tailbone.views.batch import BatchMasterView


class InventoryBatchView(BatchMasterView):
    """
    Master view for inventory batches.
    """
    model_class = model.InventoryBatch
    model_title_plural = "Inventory Batches"
    default_handler_spec = 'rattail.batch.inventory:InventoryBatchHandler'
    route_prefix = 'batch.inventory'
    url_prefix = '/batch/inventory'
    creatable = False
    editable = False

    model_row_class = model.InventoryBatchRow
    rows_editable = True

    def _preconfigure_grid(self, g):
        super(InventoryBatchView, self)._preconfigure_grid(g)
        g.mode.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.INVENTORY_MODE),
                   label="Count Mode")

    def configure_grid(self, g):
        g.configure(include=[
            g.id,
            g.created,
            g.created_by,
            g.rowcount,
            g.executed,
            g.executed_by,
            g.mode,
        ], readonly=True)

    def _preconfigure_fieldset(self, fs):
        super(InventoryBatchView, self)._preconfigure_fieldset(fs)
        fs.mode.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.INVENTORY_MODE),
                    label="Count Mode")
        fs.append(fa.Field('handheld_batches', renderer=forms.renderers.HandheldBatchesFieldRenderer, readonly=True,
                           value=lambda b: b._handhelds))

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id,
                fs.created,
                fs.created_by,
                fs.handheld_batches,
                fs.mode,
                fs.rowcount,
                fs.executed,
                fs.executed_by,
            ])

    def _preconfigure_row_grid(self, g):
        super(InventoryBatchView, self)._preconfigure_row_grid(g)
        g.upc.set(label="UPC")
        g.brand_name.set(label="Brand")
        g.cases.set(renderer=forms.renderers.QuantityFieldRenderer)
        g.units.set(renderer=forms.renderers.QuantityFieldRenderer)
        g.status_code.set(label="Status")

    def configure_row_grid(self, g):
        g.configure(
            include=[
                g.sequence,
                g.upc,
                g.brand_name,
                g.description,
                g.size,
                g.cases,
                g.units,
                g.status_code,
            ],
            readonly=True)

    def row_grid_row_attrs(self, row, i):
        attrs = {}
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            attrs['class_'] = 'warning'
        return attrs

    def _preconfigure_row_fieldset(self, fs):
        super(InventoryBatchView, self)._preconfigure_row_fieldset(fs)
        fs.upc.set(readonly=True, label="UPC", renderer=forms.renderers.GPCFieldRenderer,
                   attrs={'link': lambda r: self.request.route_url('products.view', uuid=r.product_uuid)})
        fs.brand_name.set(readonly=True)
        fs.description.set(readonly=True)
        fs.size.set(readonly=True)

    def configure_row_fieldset(self, fs):
        fs.configure(
            include=[
                fs.sequence,
                fs.upc,
                fs.brand_name,
                fs.description,
                fs.size,
                fs.status_code,
                fs.cases,
                fs.units,
            ])


def includeme(config):
    InventoryBatchView.defaults(config)
