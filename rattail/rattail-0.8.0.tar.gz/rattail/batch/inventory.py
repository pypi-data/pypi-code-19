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
Handler for inventory batches
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import api, model
from rattail.batch import BatchHandler


class InventoryBatchHandler(BatchHandler):
    """
    Handler for inventory batches.
    """
    batch_model_class = model.InventoryBatch

    def should_populate(self, batch):
        # all inventory batches must (currently) come from handheld batch
        return True

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from an input data file, parsed according
        to the batch device type.
        """
        if not batch.handheld_batches:
            raise ValueError("Inventory batch does not have data source from which to populate")

        def append(hh, i):
            row = model.InventoryBatchRow()
            row.upc = hh.upc
            row.cases = hh.cases or None
            row.units = hh.units or None
            batch.add_row(row)
            self.refresh_row(row)

        data = []
        for handheld in batch.handheld_batches:
            data.extend(handheld.active_rows())
        self.progress_loop(append, data, progress,
                           message="Adding initial rows to batch")

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        if not row.upc:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        session = orm.object_session(row)
        product = api.get_product_by_upc(session, row.upc)
        if not product:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        # current / static attributes
        row.product = product
        if product.brand:
            row.brand_name = product.brand.name
        row.description = product.description
        row.size = product.size
        row.status_code = row.STATUS_OK
