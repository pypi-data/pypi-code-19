# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Model for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from rattail.db.model import Base, BatchMixin, ProductBatchRowMixin, uuid_column, getset_factory


class InventoryBatch(BatchMixin, Base):
    """
    Batch for product inventory counts; note that this requires a data file.
    """
    __tablename__ = 'batch_inventory'
    __batchrow_class__ = 'InventoryBatchRow'
    batch_key = 'inventory'

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['handheld_batch_uuid'], ['batch_handheld.uuid'],
                                    name='batch_inventory_fk_handheld_batch'),
            )

    handheld_batch_uuid = sa.Column(sa.String(length=32), nullable=True)

    handheld_batch = orm.relationship(
        'HandheldBatch',
        doc="""
        Reference to the handheld batch from which this inventory batch originated.
        """,
        backref=orm.backref('inventory_batch', uselist=False, doc="""
        Reference to the inventory batch to which this handheld batch was converted.
        """))

    mode = sa.Column(sa.Integer(), nullable=True, doc="""
    Specifies the "mode" for the inventory count batch, i.e. how the count data
    should ultimately be interpreted/applied.
    """)


class InventoryBatchFromHandheld(Base):
    """
    Primary data model for inventory batches.
    """
    __tablename__ = 'batch_inventory_handheld'
    __table_args__ = (
        sa.ForeignKeyConstraint(['batch_uuid'], ['batch_inventory.uuid'],
                                name='batch_inventory_handheld_fk_batch'),
        sa.ForeignKeyConstraint(['handheld_uuid'], ['batch_handheld.uuid'],
                                name='batch_inventory_handheld_fk_handheld'),
    )

    uuid = uuid_column()

    batch_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)
    batch = orm.relationship(
        InventoryBatch,
        doc="""
        Reference to the inventory batch, with which handheld batch(es) are associated.
        """,
        backref=orm.backref(
            '_handhelds',
            collection_class=ordering_list('ordinal', count_from=1),
            order_by=ordinal,
            cascade='all, delete-orphan',
            doc="""
            Sequence of raw inventory / handheld batch associations.
            """))
    
    handheld_uuid = sa.Column(sa.String(length=32), nullable=False)
    handheld = orm.relationship(
        'HandheldBatch',
        doc="""
        Reference to the handheld batch from which this inventory batch originated.
        """,
        backref=orm.backref(
            '_inventory_batch',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Indirect reference to the inventory batch to which this handheld batch was converted.
            """))


InventoryBatch.handheld_batches = association_proxy('_handhelds', 'handheld',
                                                    creator=lambda batch: InventoryBatchFromHandheld(handheld=batch),
                                                    getset_factory=getset_factory)


class InventoryBatchRow(ProductBatchRowMixin, Base):
    """
    Rows for inventory batches.
    """
    __tablename__ = 'batch_inventory_row'
    __batch_class__ = InventoryBatch

    STATUS_OK = 1
    STATUS_PRODUCT_NOT_FOUND = 2

    STATUS = {
        STATUS_OK:                      "ok",
        STATUS_PRODUCT_NOT_FOUND:       "product not found",
    }

    cases = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case quantity for the record.
    """)

    units = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Unit quantity for the record.
    """)
