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
Views for 'receiving' (purchasing) batches
"""

from __future__ import unicode_literals, absolute_import

import re

import sqlalchemy as sa

from rattail import pod
from rattail.db import model
from rattail.gpc import GPC
from rattail.util import pretty_quantity

import formalchemy as fa
import formencode as fe
from webhelpers2.html import tags

from tailbone import forms
from tailbone.views.purchasing import PurchasingBatchView


class ReceivingBatchView(PurchasingBatchView):
    """
    Master view for receiving batches
    """
    route_prefix = 'receiving'
    url_prefix = '/receiving'
    model_title = "Receiving Batch"
    model_title_plural = "Receiving Batches"
    creatable = False
    rows_deletable = False
    supports_mobile = True
    mobile_creatable = True
    mobile_rows_viewable = True

    @property
    def batch_mode(self):
        return self.enum.PURCHASE_BATCH_MODE_RECEIVING

    def mobile_create(self):
        """
        Mobile view for creating a new receiving batch
        """
        mode = self.batch_mode
        data = {'mode': mode}

        vendor = None
        if self.request.method == 'POST' and self.request.POST.get('vendor'):
            vendor = self.Session.query(model.Vendor).get(self.request.POST['vendor'])
            if vendor:
                data['vendor'] = vendor

                if self.request.POST.get('purchase'):
                    purchase = self.get_purchase(self.request.POST['purchase'])
                    if purchase:

                        batch = self.model_class()
                        batch.mode = mode
                        batch.vendor = vendor
                        batch.store = self.rattail_config.get_store(self.Session())
                        batch.buyer = self.request.user.employee
                        batch.created_by = self.request.user
                        kwargs = self.get_batch_kwargs(batch, mobile=True)
                        batch = self.handler.make_batch(self.Session(), **kwargs)
                        if self.handler.should_populate(batch):
                            self.handler.populate(batch)
                        return self.redirect(self.request.route_url('mobile.receiving.view', uuid=batch.uuid))

        data['mode_title'] = self.enum.PURCHASE_BATCH_MODE[mode].capitalize()
        if vendor:
            purchases = self.eligible_purchases(vendor.uuid, mode=mode)
            data['purchases'] = [(p['key'], p['display']) for p in purchases['purchases']]
        return self.render_to_response('create', data, mobile=True)

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(ReceivingBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        if mobile:

            purchase = self.get_purchase(self.request.POST['purchase'])
            kwargs['sms_transaction_number'] = purchase.F1032

            numbers = [d.F03 for d in purchase.details]
            if numbers:
                number = max(set(numbers), key=numbers.count)
                kwargs['department'] = self.Session.query(model.Department)\
                                                   .filter(model.Department.number == number)\
                                                   .one()

        else:
            kwargs['sms_transaction_number'] = batch.sms_transaction_number
        return kwargs

    def get_mobile_data(self, session=None):
        # TODO: this hard-codes list view to show Pending only
        return super(ReceivingBatchView, self).get_mobile_data(session=session)\
                                              .filter(model.PurchaseBatch.executed == None)\
                                              .filter(sa.or_(
                                                  model.PurchaseBatch.complete == None,
                                                  model.PurchaseBatch.complete == False))

    def configure_mobile_grid(self, g):
        super(ReceivingBatchView, self).configure_mobile_grid(g)
        g.listitem.set(renderer=ReceivingBatchRenderer)

    def configure_mobile_fieldset(self, fs):
        fs.configure(include=[
            fs.vendor.with_renderer(fa.TextFieldRenderer),
            fs.department.with_renderer(fa.TextFieldRenderer),
        ])

    def get_mobile_row_data(self, batch):
        return super(ReceivingBatchView, self).get_mobile_row_data(batch)\
                                              .order_by(model.PurchaseBatchRow.sequence)

    def render_mobile_row_listitem(self, row, **kwargs):
        if row is None:
            return ''
        title = "({}) {}".format(row.upc.pretty(), row.product.full_description)
        url = self.request.route_url('mobile.receiving.rows.view', uuid=row.uuid)
        return tags.link_to(title, url)

    def mobile_lookup(self):
        """
        Try to locate a product by UPC, and validate it in the context of
        current batch, returning some data for client JS.
        """
        batch = self.get_instance()
        upc = self.request.GET.get('upc', '').strip()
        upc = re.sub(r'\D', '', upc)
        if upc:

            # first try to locate existing batch row by UPC match
            provided = GPC(upc, calc_check_digit=False)
            checked = GPC(upc, calc_check_digit='upc')
            rows = self.Session.query(model.PurchaseBatchRow)\
                               .filter(model.PurchaseBatchRow.batch == batch)\
                               .filter(model.PurchaseBatchRow.upc.in_((provided, checked)))\
                               .all()

            if rows:
                if len(rows) > 1:
                    log.warning("found multiple UPC matches for {} in batch {}: {}".format(
                        upc, batch.id_str, batch))
                row = rows[0]
                return self.redirect(self.request.route_url('mobile.{}.view'.format(self.get_row_route_prefix()), uuid=row.uuid))

        # TODO: how to handle product not found in system / purchase ?
        raise NotImplementedError

    def mobile_view_row(self):
        """
        Mobile view for receiving batch row items.  Note that this also handles
        updating a row.
        """
        self.viewing = True
        row = self.get_row_instance()
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': pod.get_image_url(self.rattail_config, row.upc),
            'form': form,
        }

        if self.request.has_perm('{}.edit'.format(self.get_row_permission_prefix())):
            update_form = forms.SimpleForm(self.request, schema=ReceivingForm)
            if update_form.validate():
                row = update_form.data['row']
                mode = update_form.data['mode']
                cases = update_form.data['cases']
                units = update_form.data['units']
                if cases:
                    setattr(row, 'cases_{}'.format(mode),
                            (getattr(row, 'cases_{}'.format(mode)) or 0) + cases)
                if units:
                    setattr(row, 'units_{}'.format(mode),
                            (getattr(row, 'units_{}'.format(mode)) or 0) + units)

                # if mode in ('damaged', 'expired', 'mispick'):
                if mode in ('damaged', 'expired'):
                    self.attach_credit(row, mode, cases, units,
                                       expiration_date=update_form.data['expiration_date'],
                                       # discarded=update_form.data['trash'],
                                       # mispick_product=shipped_product)
                    )

                # first undo any totals previously in effect for the row, then refresh
                if row.invoice_total:
                    row.batch.invoice_total -= row.invoice_total
                self.handler.refresh_row(row)

                return self.redirect(self.request.route_url('mobile.{}.view'.format(self.get_route_prefix()), uuid=row.batch_uuid))

        return self.render_to_response('view_row', context, mobile=True)

    def attach_credit(self, row, credit_type, cases, units, expiration_date=None, discarded=None, mispick_product=None):
        batch = row.batch
        credit = model.PurchaseBatchCredit()
        credit.credit_type = credit_type
        credit.store = batch.store
        credit.vendor = batch.vendor
        credit.date_ordered = batch.date_ordered
        credit.date_shipped = batch.date_shipped
        credit.date_received = batch.date_received
        credit.invoice_number = batch.invoice_number
        credit.invoice_date = batch.invoice_date
        credit.product = row.product
        credit.upc = row.upc
        credit.brand_name = row.brand_name
        credit.description = row.description
        credit.size = row.size
        credit.department_number = row.department_number
        credit.department_name = row.department_name
        credit.case_quantity = row.case_quantity
        credit.cases_shorted = cases
        credit.units_shorted = units
        credit.invoice_line_number = row.invoice_line_number
        credit.invoice_case_cost = row.invoice_case_cost
        credit.invoice_unit_cost = row.invoice_unit_cost
        credit.invoice_total = row.invoice_total
        credit.product_discarded = discarded
        if credit_type == 'expired':
            credit.expiration_date = expiration_date
        elif credit_type == 'mispick' and mispick_product:
            credit.mispick_product = mispick_product
            credit.mispick_upc = mispick_product.upc
            if mispick_product.brand:
                credit.mispick_brand_name = mispick_product.brand.name
            credit.mispick_description = mispick_product.description
            credit.mispick_size = mispick_product.size
        row.credits.append(credit)
        return credit

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        model_key = cls.get_model_key()
        row_permission_prefix = cls.get_row_permission_prefix()

        # mobile lookup
        config.add_route('mobile.{}.lookup'.format(route_prefix), '/mobile{}/{{{}}}/lookup'.format(url_prefix, model_key))
        config.add_view(cls, attr='mobile_lookup', route_name='mobile.{}.lookup'.format(route_prefix),
                        renderer='json', permission='{}.view'.format(row_permission_prefix))

        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)


class ReceivingBatchRenderer(fa.FieldRenderer):

    def render_readonly(self, **kwargs):
        batch = self.raw_value
        title = "({}) {} for ${:0,.2f} - {}, {}".format(
            batch.id_str,
            batch.vendor,
            batch.po_total or 0,
            batch.department,
            batch.created_by)
        url = self.request.route_url('mobile.receiving.view', uuid=batch.uuid)
        return tags.link_to(title, url)


class ValidBatchRow(forms.validators.ModelValidator):
    model_class = model.PurchaseBatchRow

    def _to_python(self, value, state):
        row = super(ValidBatchRow, self)._to_python(value, state)
        if row.batch.executed:
            raise fe.Invalid("Batch has already been executed", value, state)
        return row


class ReceivingForm(forms.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    row = ValidBatchRow()
    mode = fe.validators.OneOf(['received', 'damaged', 'expired',
                                # 'mispick',
    ])
    # product = forms.validators.ValidProduct()
    # upc = forms.validators.ValidGPC()
    # brand_name = fe.validators.String()
    # description = fe.validators.String()
    # size = fe.validators.String()
    # case_quantity = fe.validators.Number()
    cases = fe.validators.Number()
    units = fe.validators.Number()
    expiration_date = fe.validators.DateValidator()
    # trash = fe.validators.Bool()
    # ordered_product = forms.validators.ValidProduct()


def includeme(config):
    ReceivingBatchView.defaults(config)
