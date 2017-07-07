# -*- coding: utf-8 -*-
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
Customer order item views
"""

from __future__ import unicode_literals, absolute_import

import datetime

from sqlalchemy import orm

from rattail.db import model
from rattail.time import localtime

import formalchemy as fa

from tailbone import forms
from tailbone.views import MasterView


class CustomerOrderItemsView(MasterView):
    """
    Master view for customer order items
    """
    model_class = model.CustomerOrderItem
    route_prefix = 'custorders.items'
    url_prefix = '/custorders/items'
    creatable = False
    editable = False
    deletable = False

    has_rows = True
    model_row_class = model.CustomerOrderItemEvent
    rows_title = "Event History"
    rows_filterable = False
    rows_sortable = False
    rows_pageable = False
    rows_viewable = False

    def query(self, session):
        return session.query(model.CustomerOrderItem)\
                      .join(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrderItem.order)\
                               .joinedload(model.CustomerOrder.person))

    def _preconfigure_grid(self, g):

        g.joiners['person'] = lambda q: q.outerjoin(model.Person)
        g.filters['person'] = g.make_filter('person', model.Person.display_name, label="Person Name",
                                            default_active=True, default_verb='contains')
        g.sorters['person'] = g.make_sorter(model.Person.display_name)

        g.filters['product_brand'].label = "Brand"
        g.product_brand.set(label="Brand")

        g.filters['product_description'].label = "Description"
        g.product_description.set(label="Description")

        g.filters['product_size'].label = "Size"
        g.product_size.set(label="Size")

        g.case_quantity.set(renderer=forms.renderers.QuantityFieldRenderer)
        g.cases_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)
        g.units_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)

        g.total_price.set(renderer=forms.renderers.CurrencyFieldRenderer)

        g.filters['status_code'].label = "Status"
        g.status_code.set(label="Status")

        g.append(fa.Field('person', value=lambda i: i.order.person))

        g.sorters['order_created'] = g.make_sorter(model.CustomerOrder.created)
        g.append(fa.Field('order_created',
                          value=lambda i: localtime(self.rattail_config, i.order.created, from_utc=True),
                          renderer=forms.renderers.DateTimeFieldRenderer))

        g.default_sortkey = 'order_created'
        g.default_sortdir = 'desc'

    def configure_grid(self, g):
        g.configure(
            include=[
                g.person,
                g.product_brand,
                g.product_description,
                g.product_size,
                g.case_quantity,
                g.cases_ordered,
                g.units_ordered,
                g.order_created,
                g.status_code,
            ],
            readonly=True)

    def _preconfigure_fieldset(self, fs):
        fs.order.set(renderer=forms.renderers.CustomerOrderFieldRenderer)
        fs.product.set(renderer=forms.renderers.ProductFieldRenderer)
        fs.product_unit_of_measure.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.UNIT_OF_MEASURE))
        fs.case_quantity.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.unit_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.total_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.paid_amount.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.status_code.set(label="Status")
        fs.append(fa.Field('person', value=lambda i: i.order.person,
                           renderer=forms.renderers.PersonFieldRenderer))

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.person,
                fs.product,
                fs.product_brand,
                fs.product_description,
                fs.product_size,
                fs.case_quantity,
                fs.cases_ordered,
                fs.units_ordered,
                fs.unit_price,
                fs.total_price,
                fs.paid_amount,
                fs.status_code,
            ])

    def get_row_data(self, item):
        return self.Session.query(model.CustomerOrderItemEvent)\
                           .filter(model.CustomerOrderItemEvent.item == item)\
                           .order_by(model.CustomerOrderItemEvent.occurred,
                                     model.CustomerOrderItemEvent.type_code)

    def _preconfigure_row_grid(self, g):
        g.occurred.set(label="When")
        g.type_code.set(label="What") # TODO: enum renderer
        g.user.set(label="Who")
        g.note.set(label="Notes")

    def configure_row_grid(self, g):
        g.configure(
            include=[
                g.occurred,
                g.type_code,
                g.user,
                g.note,
            ],
            readonly=True)


def includeme(config):
    CustomerOrderItemsView.defaults(config)
