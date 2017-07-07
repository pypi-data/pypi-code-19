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
Views for purchase order batches
"""

from __future__ import unicode_literals, absolute_import

import re
import logging

from sqlalchemy import orm

from rattail import pod
from rattail.db import model, api
from rattail.db.util import make_full_description
from rattail.gpc import GPC
from rattail.time import localtime
from rattail.core import Object
from rattail.util import pretty_quantity

import formalchemy as fa
import formencode as fe
from pyramid import httpexceptions

from tailbone import forms, newgrids as grids
from tailbone.db import Session
from tailbone.views.batch import BatchMasterView


log = logging.getLogger(__name__)


class ReceivingForm(forms.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    mode = fe.validators.OneOf(['received', 'damaged', 'expired', 'mispick'])
    product = forms.validators.ValidProduct()
    upc = forms.validators.ValidGPC()
    brand_name = fe.validators.String()
    description = fe.validators.String()
    size = fe.validators.String()
    case_quantity = fe.validators.Number()
    cases = fe.validators.Number()
    units = fe.validators.Number()
    expiration_date = fe.validators.DateValidator()
    trash = fe.validators.Bool()
    ordered_product = forms.validators.ValidProduct()


class PurchaseBatchView(BatchMasterView):
    """
    Master view for purchase order batches.
    """
    model_class = model.PurchaseBatch
    model_row_class = model.PurchaseBatchRow
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'
    route_prefix = 'purchases.batch'
    url_prefix = '/purchases/batches'
    rows_creatable = True
    rows_editable = True
    edit_with_rows = False
    supports_mobile = True

    order_form_header_columns = [
        "UPC",
        "Brand",
        "Description",
        "Case",
        "Vend. Code",
        "Pref.",
        "Unit Cost",
    ]

    def get_instance_title(self, batch):
        return '{} ({})'.format(batch.id_str, self.enum.PURCHASE_BATCH_MODE[batch.mode])

    def _preconfigure_grid(self, g):
        super(PurchaseBatchView, self)._preconfigure_grid(g)

        g.filters['mode'].set_value_renderer(grids.filters.EnumValueRenderer(self.enum.PURCHASE_BATCH_MODE))

        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

        g.joiners['department'] = lambda q: q.join(model.Department)
        g.filters['department'] = g.make_filter('department', model.Department.name)
        g.sorters['department'] = g.make_sorter(model.Department.name)

        g.joiners['buyer'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['buyer'] = g.make_filter('buyer', model.Person.display_name,
                                           default_active=True, default_verb='contains')
        g.sorters['buyer'] = g.make_sorter(model.Person.display_name)

        if self.request.has_perm('purchases.batch.execute'):
            g.filters['complete'].default_active = True
            g.filters['complete'].default_verb = 'is_true'

        g.date_ordered.set(label="Ordered")
        g.date_received.set(label="Received")
        g.mode.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.PURCHASE_BATCH_MODE))

    def configure_grid(self, g):
        g.configure(
            include=[
                g.id,
                g.mode,
                g.vendor,
                g.department,
                g.buyer,
                g.date_ordered,
                g.created,
                g.created_by,
                g.executed,
            ],
            readonly=True)

    def make_form(self, batch, **kwargs):
        if self.creating:
            kwargs.setdefault('id', 'new-purchase-form')
        form = super(PurchaseBatchView, self).make_form(batch, **kwargs)
        return form

    def _preconfigure_fieldset(self, fs):
        super(PurchaseBatchView, self)._preconfigure_fieldset(fs)
        fs.mode.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.PURCHASE_BATCH_MODE))
        fs.store.set(renderer=forms.renderers.StoreFieldRenderer)
        fs.purchase.set(renderer=forms.renderers.PurchaseFieldRenderer, options=[])
        fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer,
                      attrs={'selected': 'vendor_selected',
                             'cleared': 'vendor_cleared'})
        fs.department.set(renderer=forms.renderers.DepartmentFieldRenderer,
                          options=self.get_department_options())
        fs.buyer.set(renderer=forms.renderers.EmployeeFieldRenderer)
        fs.po_number.set(label="PO Number")
        fs.po_total.set(label="PO Total", readonly=True, renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_total.set(readonly=True, renderer=forms.renderers.CurrencyFieldRenderer)
        fs.notes.set(renderer=fa.TextAreaFieldRenderer, size=(80, 10))

        fs.append(fa.Field('vendor_email', readonly=True,
                           value=lambda b: b.vendor.email.address if b.vendor.email else None))
        fs.append(fa.Field('vendor_fax', readonly=True,
                           value=self.get_vendor_fax_number))
        fs.append(fa.Field('vendor_contact', readonly=True,
                           value=lambda b: b.vendor.contact or None))
        fs.append(fa.Field('vendor_phone', readonly=True,
                           value=self.get_vendor_phone_number))

    def get_department_options(self):
        departments = Session.query(model.Department).order_by(model.Department.number)
        return [('{} {}'.format(d.number, d.name), d.uuid) for d in departments]

    def get_vendor_phone_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Voice':
                return phone.number

    def get_vendor_fax_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Fax':
                return phone.number

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id,
                fs.mode,
                fs.store,
                fs.buyer,
                fs.vendor,
                fs.department,
                fs.purchase,
                fs.vendor_email,
                fs.vendor_fax,
                fs.vendor_contact,
                fs.vendor_phone,
                fs.date_ordered,
                fs.date_received,
                fs.po_number,
                fs.po_total,
                fs.invoice_date,
                fs.invoice_number,
                fs.invoice_total,
                fs.notes,
                fs.created,
                fs.created_by,
                fs.complete,
                fs.executed,
                fs.executed_by,
            ])

        if self.creating:
            del fs.po_total
            del fs.invoice_total
            del fs.complete
            del fs.vendor_email
            del fs.vendor_fax
            del fs.vendor_phone
            del fs.vendor_contact

            # default store may be configured
            store = self.rattail_config.get('rattail', 'store')
            if store:
                store = api.get_store(Session(), store)
                if store:
                    fs.model.store = store

            # default buyer is current user
            if self.request.method != 'POST':
                buyer = self.request.user.employee
                if buyer:
                    fs.model.buyer = buyer

            # TODO: something tells me this isn't quite safe..
            # all dates have today as default
            today = localtime(self.rattail_config).date()
            fs.model.date_ordered = today
            fs.model.date_received = today

            # available batch modes are restricted via permission
            modes = dict(self.enum.PURCHASE_BATCH_MODE)
            if not self.request.has_perm('purchases.batch.create.ordering'):
                del modes[self.enum.PURCHASE_BATCH_MODE_ORDERING]
            if not self.request.has_perm('purchases.batch.create.receiving'):
                del modes[self.enum.PURCHASE_BATCH_MODE_RECEIVING]
            if not self.request.has_perm('purchases.batch.create.invoicing'):
                del modes[self.enum.PURCHASE_BATCH_MODE_COSTING]
            fs.mode.set(renderer=forms.renderers.EnumFieldRenderer(modes))

        elif self.editing:
            fs.mode.set(readonly=True)
            fs.store.set(readonly=True)
            fs.vendor.set(readonly=True)
            fs.department.set(readonly=True)
            fs.purchase.set(readonly=True)

    def eligible_purchases(self, vendor_uuid=None, mode=None):
        if not vendor_uuid:
            vendor_uuid = self.request.GET.get('vendor_uuid')
        vendor = Session.query(model.Vendor).get(vendor_uuid) if vendor_uuid else None
        if not vendor:
            return {'error': "Must specify a vendor."}

        if mode is None:
            mode = self.request.GET.get('mode')
            mode = int(mode) if mode and mode.isdigit() else None
        if not mode or mode not in self.enum.PURCHASE_BATCH_MODE:
            return {'error': "Unknown mode: {}".format(mode)}

        purchases = Session.query(model.Purchase)\
                           .filter(model.Purchase.vendor == vendor)
        if mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_ORDERED)\
                                 .order_by(model.Purchase.date_ordered, model.Purchase.created)
        elif mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_RECEIVED)\
                                 .order_by(model.Purchase.date_received, model.Purchase.created)

        return {'purchases': [{'key': p.uuid,
                               'department_uuid': p.department_uuid or '',
                               'display': self.render_eligible_purchase(p)}
                              for p in purchases]}

    def render_eligible_purchase(self, purchase):
        if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
            date = purchase.date_ordered
            total = purchase.po_total
        elif purchase.status == self.enum.PURCHASE_STATUS_RECEIVED:
            date = purchase.date_received
            total = purchase.invoice_total
        return '{} for ${:0,.2f} ({})'.format(date, total, purchase.department or purchase.buyer)

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(PurchaseBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        kwargs['mode'] = batch.mode
        if batch.store:
            kwargs['store'] = batch.store
        elif batch.store_uuid:
            kwargs['store_uuid'] = batch.store_uuid
        if batch.vendor:
            kwargs['vendor'] = batch.vendor
        elif batch.vendor_uuid:
            kwargs['vendor_uuid'] = batch.vendor_uuid
        if batch.department:
            kwargs['department'] = batch.department
        elif batch.department_uuid:
            kwargs['department_uuid'] = batch.department_uuid
        if batch.buyer:
            kwargs['buyer'] = batch.buyer
        elif batch.buyer_uuid:
            kwargs['buyer_uuid'] = batch.buyer_uuid
        kwargs['po_number'] = batch.po_number

        # TODO: should these always get set?
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            kwargs['date_ordered'] = batch.date_ordered
        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            kwargs['date_ordered'] = batch.date_ordered
            kwargs['date_received'] = batch.date_received
            kwargs['invoice_number'] = batch.invoice_number
        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            kwargs['invoice_date'] = batch.invoice_date
            kwargs['invoice_number'] = batch.invoice_number

        if batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                          self.enum.PURCHASE_BATCH_MODE_COSTING):
            if batch.purchase_uuid:
                purchase = Session.query(model.Purchase).get(batch.purchase_uuid)
                assert purchase
                kwargs['purchase'] = purchase
                kwargs['buyer'] = purchase.buyer
                kwargs['buyer_uuid'] = purchase.buyer_uuid
                kwargs['date_ordered'] = purchase.date_ordered
                kwargs['po_total'] = purchase.po_total

        return kwargs

    def template_kwargs_view(self, **kwargs):
        kwargs = super(PurchaseBatchView, self).template_kwargs_view(**kwargs)
        vendor = kwargs['batch'].vendor
        kwargs['vendor_cost_count'] = Session.query(model.ProductCost)\
                                             .filter(model.ProductCost.vendor == vendor)\
                                             .count()
        kwargs['vendor_cost_threshold'] = self.rattail_config.getint(
            'tailbone', 'purchases.order_form.vendor_cost_warning_threshold', default=699)
        return kwargs

    def template_kwargs_create(self, **kwargs):
        kwargs['purchases_field'] = 'purchase_uuid'
        return kwargs

    def get_row_data(self, batch):
        query = super(PurchaseBatchView, self).get_row_data(batch)
        return query.options(orm.joinedload(model.PurchaseBatchRow.credits))

    def _preconfigure_row_grid(self, g):
        super(PurchaseBatchView, self)._preconfigure_row_grid(g)

        g.filters['upc'].label = "UPC"
        g.filters['brand_name'].label = "Brand"

        g.upc.set(label="UPC")
        g.brand_name.set(label="Brand")
        g.cases_ordered.set(label="Cases Ord.", renderer=forms.renderers.QuantityFieldRenderer)
        g.units_ordered.set(label="Units Ord.", renderer=forms.renderers.QuantityFieldRenderer)
        g.cases_received.set(label="Cases Rec.", renderer=forms.renderers.QuantityFieldRenderer)
        g.units_received.set(label="Units Rec.", renderer=forms.renderers.QuantityFieldRenderer)
        g.po_total.set(label="Total", renderer=forms.renderers.CurrencyFieldRenderer)
        g.invoice_total.set(label="Total", renderer=forms.renderers.CurrencyFieldRenderer)
        g.append(fa.Field('has_credits', type=fa.types.Boolean, label="Credits?",
                          value=lambda row: bool(row.credits)))

    def configure_row_grid(self, g):
        batch = self.get_instance()

        g.configure(
            include=[
                g.sequence,
                g.upc,
                g.item_id,
                g.brand_name,
                g.description,
                g.size,
                g.cases_ordered,
                g.units_ordered,
                g.cases_received,
                g.units_received,
                g.po_total,
                g.invoice_total,
                g.has_credits,
                g.status_code,
            ],
            readonly=True)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            del g.cases_received
            del g.units_received
            del g.has_credits
            del g.invoice_total
        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            del g.po_total

    def make_row_grid_tools(self, batch):
        return self.make_default_row_grid_tools(batch)

    def row_grid_row_attrs(self, row, i):
        attrs = {}
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            attrs['class_'] = 'warning'
        elif row.status_code in (row.STATUS_INCOMPLETE,
                                 row.STATUS_ORDERED_RECEIVED_DIFFER):
            attrs['class_'] = 'notice'
        return attrs

    def _preconfigure_row_fieldset(self, fs):
        super(PurchaseBatchView, self)._preconfigure_row_fieldset(fs)
        fs.upc.set(label="UPC")
        fs.brand_name.set(label="Brand")
        fs.case_quantity.set(renderer=forms.renderers.QuantityFieldRenderer, readonly=True)
        fs.cases_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_received.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_received.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_damaged.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_damaged.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_expired.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_expired.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_mispick.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_mispick.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.po_line_number.set(label="PO Line Number")
        fs.po_unit_cost.set(label="PO Unit Cost", renderer=forms.renderers.CurrencyFieldRenderer)
        fs.po_total.set(label="PO Total", renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_unit_cost.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_total.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.credits.set(readonly=True)
        fs.append(fa.Field('item_lookup', label="Item Lookup Code", required=True,
                           validate=self.item_lookup))

    def item_lookup(self, value, field=None):
        """
        Try to locate a single product using ``value`` as a lookup code.
        """
        batch = self.get_instance()
        product = api.get_product_by_vendor_code(Session(), value, vendor=batch.vendor)
        if product:
            return product.uuid
        if value.isdigit():
            product = api.get_product_by_upc(Session(), GPC(value))
            if not product:
                product = api.get_product_by_upc(Session(), GPC(value, calc_check_digit='upc'))
            if product:
                if not product.cost_for_vendor(batch.vendor):
                    raise fa.ValidationError("Product {} exists but has no cost for vendor {}".format(
                        product.upc.pretty(), batch.vendor))
                return product.uuid
        raise fa.ValidationError("Product not found")

    def configure_row_fieldset(self, fs):
        try:
            batch = self.get_instance()
        except httpexceptions.HTTPNotFound:
            batch = self.get_row_instance().batch

        fs.configure(
            include=[
                fs.item_lookup,
                fs.upc,
                fs.product,
                fs.brand_name,
                fs.description,
                fs.size,
                fs.case_quantity,
                fs.cases_ordered,
                fs.units_ordered,
                fs.cases_received,
                fs.units_received,
                fs.cases_damaged,
                fs.units_damaged,
                fs.cases_expired,
                fs.units_expired,
                fs.cases_mispick,
                fs.units_mispick,
                fs.po_line_number,
                fs.po_unit_cost,
                fs.po_total,
                fs.invoice_line_number,
                fs.invoice_unit_cost,
                fs.invoice_total,
                fs.status_code,
                fs.credits,
            ])

        if self.creating:
            del fs.upc
            del fs.product
            del fs.po_total
            del fs.invoice_total
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
                del fs.cases_received
                del fs.units_received
            elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                del fs.cases_ordered
                del fs.units_ordered

        elif self.editing:
            del fs.item_lookup
            fs.upc.set(readonly=True)
            fs.product.set(readonly=True)
            del fs.po_total
            del fs.invoice_total
            del fs.status_code

        elif self.viewing:
            del fs.item_lookup
            if fs.model.product:
                del (fs.brand_name,
                     fs.description,
                     fs.size)
            else:
                del fs.product

    def before_create_row(self, form):
        row = form.fieldset.model
        batch = self.get_instance()
        batch.add_row(row)
        # TODO: this seems heavy-handed but works..
        row.product_uuid = self.item_lookup(form.fieldset.item_lookup.value)

    def after_create_row(self, row):
        self.handler.refresh_row(row)

    def after_edit_row(self, row):
        batch = row.batch

        # first undo any totals previously in effect for the row
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING and row.po_total:
            batch.po_total -= row.po_total
        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING and row.invoice_total:
            batch.invoice_total -= row.invoice_total

        self.handler.refresh_row(row)

    def redirect_after_create_row(self, row):
        self.request.session.flash("Added item: {} {}".format(row.upc.pretty(), row.product))
        return self.redirect(self.request.current_route_url())

    def delete_row(self):
        """
        Update the PO total in addition to marking row as removed.
        """
        row = self.Session.query(self.model_row_class).get(self.request.matchdict['uuid'])
        if not row:
            raise httpexceptions.HTTPNotFound()
        if row.po_total:
            row.batch.po_total -= row.po_total
        if row.invoice_total:
            row.batch.invoice_total -= row.invoice_total
        row.removed = True
        return self.redirect(self.get_action_url('view', row.batch))

    def get_execute_success_url(self, batch, result, **kwargs):
        # if batch execution yielded a Purchase, redirect to it
        if isinstance(result, model.Purchase):
            return self.request.route_url('purchases.view', uuid=result.uuid)

        # otherwise just view batch again
        return self.get_action_url('view', batch)

    def order_form(self):
        """
        View for editing a purchase batch as an order form.
        """
        batch = self.get_instance()
        if batch.executed:
            return self.redirect(self.get_action_url('view', batch))

        # organize existing batch rows by product
        order_items = {}
        for row in batch.data_rows:
            if not row.removed:
                order_items[row.product_uuid] = row

        # organize vendor catalog costs by dept / subdept
        departments = {}
        costs = self.get_order_form_costs(batch.vendor)
        costs = self.sort_order_form_costs(costs)
        for cost in costs:

            department = cost.product.department
            if department:
                departments.setdefault(department.uuid, department)
            else:
                if None not in departments:
                    department = Object(name=None, number=None)
                    departments[None] = department
                department = departments[None]
            
            subdepartments = getattr(department, '_order_subdepartments', None)
            if subdepartments is None:
                subdepartments = department._order_subdepartments = {}

            subdepartment = cost.product.subdepartment
            if subdepartment:
                subdepartments.setdefault(subdepartment.uuid, subdepartment)
            else:
                if None not in subdepartments:
                    subdepartment = Object(name=None, number=None)
                    subdepartments[None] = subdepartment
                subdepartment = subdepartments[None]

            subdept_costs = getattr(subdepartment, '_order_costs', None)
            if subdept_costs is None:
                subdept_costs = subdepartment._order_costs = []
            subdept_costs.append(cost)
            cost._batchrow = order_items.get(cost.product_uuid)

            # do anything else needed to satisfy template display requirements etc.
            self.decorate_order_form_cost(cost)

        # fetch recent purchase history, sort/pad for template convenience
        history = self.get_order_form_history(batch, costs, 6)
        for i in range(6 - len(history)):
            history.append(None)
        history = list(reversed(history))

        title = self.get_instance_title(batch)
        return self.render_to_response('order_form', {
            'batch': batch,
            'instance': batch,
            'instance_title': title,
            'index_title': "{}: {}".format(self.get_model_title(), title),
            'index_url': self.get_action_url('view', batch),
            'vendor': batch.vendor,
            'departments': departments,
            'history': history,
            'get_upc': lambda p: p.upc.pretty() if p.upc else '',
            'header_columns': self.order_form_header_columns,
            'ignore_cases': self.handler.ignore_cases,
        })

    def get_order_form_history(self, batch, costs, count):

        # fetch last 6 purchases for this vendor, organize line items by product
        history = []
        purchases = Session.query(model.Purchase)\
                           .filter(model.Purchase.vendor == batch.vendor)\
                           .filter(model.Purchase.status >= self.enum.PURCHASE_STATUS_ORDERED)\
                           .order_by(model.Purchase.date_ordered.desc(), model.Purchase.created.desc())\
                           .options(orm.joinedload(model.Purchase.items))
        for purchase in purchases[:count]:
            items = {}
            for item in purchase.items:
                items[item.product_uuid] = item
            history.append({'purchase': purchase, 'items': items})
        
        return history

    def get_order_form_costs(self, vendor):
        return Session.query(model.ProductCost)\
                      .join(model.Product)\
                      .outerjoin(model.Brand)\
                      .filter(model.ProductCost.vendor == vendor)\
                      .options(orm.joinedload(model.ProductCost.product)\
                               .joinedload(model.Product.department))\
                      .options(orm.joinedload(model.ProductCost.product)\
                               .joinedload(model.Product.subdepartment))

    def sort_order_form_costs(self, costs):
        return costs.order_by(model.Brand.name,
                              model.Product.description,
                              model.Product.size)

    def decorate_order_form_cost(self, cost):
        pass

    def order_form_update(self):
        """
        Handles AJAX requests to update current batch, from Order Form view.
        """
        batch = self.get_instance()

        cases_ordered = self.request.POST.get('cases_ordered', '0')
        if not cases_ordered or not cases_ordered.isdigit():
            return {'error': "Invalid value for cases ordered: {}".format(cases_ordered)}
        cases_ordered = int(cases_ordered)

        units_ordered = self.request.POST.get('units_ordered', '0')
        if not units_ordered or not units_ordered.isdigit():
            return {'error': "Invalid value for units ordered: {}".format(units_ordered)}
        units_ordered = int(units_ordered)

        uuid = self.request.POST.get('product_uuid')
        product = Session.query(model.Product).get(uuid) if uuid else None
        if not product:
            return {'error': "Product not found"}

        row = None
        rows = [r for r in batch.data_rows if r.product_uuid == uuid]
        if rows:
            assert len(rows) == 1
            row = rows[0]
            if row.po_total and not row.removed:
                batch.po_total -= row.po_total
            if cases_ordered or units_ordered:
                row.cases_ordered = cases_ordered or None
                row.units_ordered = units_ordered or None
                row.removed = False
                self.handler.refresh_row(row)
            else:
                row.removed = True

        elif cases_ordered or units_ordered:
            row = model.PurchaseBatchRow()
            row.sequence = max([0] + [r.sequence for r in batch.data_rows]) + 1
            row.product = product
            batch.data_rows.append(row)
            row.cases_ordered = cases_ordered or None
            row.units_ordered = units_ordered or None
            self.handler.refresh_row(row)

        return {
            'row_cases_ordered': '' if not row or row.removed else int(row.cases_ordered or 0),
            'row_units_ordered': '' if not row or row.removed else int(row.units_ordered or 0),
            'row_po_total': '' if not row or row.removed else '${:0,.2f}'.format(row.po_total),
            'batch_po_total': '${:0,.2f}'.format(batch.po_total or 0),
        }

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

    def receiving_form(self):
        """
        Workflow view for receiving items on a purchase batch.
        """
        batch = self.get_instance()
        if batch.executed:
            return self.redirect(self.get_action_url('view', batch))

        form = forms.SimpleForm(self.request, schema=ReceivingForm)
        if form.validate():

            mode = form.data['mode']
            shipped_product = form.data['product']
            product = form.data['ordered_product'] if mode == 'mispick' else shipped_product
            if product:
                rows = [row for row in batch.active_rows() if row.product is product]
            else:
                upc = form.data['upc']
                rows = [row for row in batch.active_rows() if not row.product and row.upc == upc]
            if rows:
                if len(rows) > 1:
                    log.warning("found {} matching rows in batch {} for product: {}".format(
                        len(rows), batch.id_str, product.upc.pretty()))
                row = rows[0]
            else:
                row = model.PurchaseBatchRow()
                row.product = product
                row.upc = form.data['upc']
                row.brand_name = form.data['brand_name']
                row.description = form.data['description']
                row.size = form.data['size']
                row.case_quantity = form.data['case_quantity']
                batch.add_row(row)

            cases = form.data['cases']
            units = form.data['units']
            if cases:
                setattr(row, 'cases_{}'.format(mode),
                        (getattr(row, 'cases_{}'.format(mode)) or 0) + cases)
            if units:
                setattr(row, 'units_{}'.format(mode),
                        (getattr(row, 'units_{}'.format(mode)) or 0) + units)

            if mode in ('damaged', 'expired', 'mispick'):
                self.attach_credit(row, mode, cases, units,
                                   expiration_date=form.data['expiration_date'],
                                   discarded=form.data['trash'],
                                   mispick_product=shipped_product)

            self.handler.refresh_row(row)

            description = make_full_description(form.data['brand_name'],
                                                form.data['description'],
                                                form.data['size'])
            self.request.session.flash("({}) {} cases, {} units: {} {}".format(
                form.data['mode'], form.data['cases'] or 0, form.data['units'] or 0,
                form.data['upc'].pretty(), description))
            return self.redirect(self.request.current_route_url())

        title = self.get_instance_title(batch)
        return self.render_to_response('receive_form', {
            'batch': batch,
            'instance': batch,
            'instance_title': title,
            'index_title': "{}: {}".format(self.get_model_title(), title),
            'index_url': self.get_action_url('view', batch),
            'vendor': batch.vendor,
            'form': forms.FormRenderer(form),
        })

    def receiving_lookup(self):
        """
        Try to locate a product by UPC, and validate it in the context of
        current batch, returning some data for client JS.
        """
        batch = self.get_instance()
        if batch.executed:
            return {
                'error': "Current batch has already been executed",
                'redirect': self.get_action_url('view', batch),
            }
        data = {}
        upc = self.request.GET.get('upc', '').strip()
        upc = re.sub(r'\D', '', upc)
        if upc:

            # first try to locate existing batch row by UPC match
            provided = GPC(upc, calc_check_digit=False)
            checked = GPC(upc, calc_check_digit='upc')
            rows = Session.query(model.PurchaseBatchRow)\
                          .filter(model.PurchaseBatchRow.batch == batch)\
                          .filter(model.PurchaseBatchRow.upc.in_((provided, checked)))\
                          .all()
            if rows:
                if len(rows) > 1:
                    log.warning("found multiple UPC matches for {} in batch {}: {}".format(
                        upc, batch.id_str, batch))
                row = rows[0]
                data['uuid'] = row.product_uuid
                data['upc'] = unicode(row.upc)
                data['upc_pretty'] = row.upc.pretty()
                data['full_description'] = make_full_description(row.brand_name, row.description, row.size)
                data['brand_name'] = row.brand_name
                data['description'] = row.description
                data['size'] = row.size
                data['case_quantity'] = pretty_quantity(row.case_quantity)
                data['image_url'] = pod.get_image_url(self.rattail_config, row.upc)
                data['found_in_batch'] = True
                data['cases_ordered'] = pretty_quantity(row.cases_ordered, empty_zero=True)
                data['units_ordered'] = pretty_quantity(row.units_ordered, empty_zero=True)
                data['cases_received'] = pretty_quantity(row.cases_received, empty_zero=True)
                data['units_received'] = pretty_quantity(row.units_received, empty_zero=True)
                data['cases_damaged'] = pretty_quantity(row.cases_damaged, empty_zero=True)
                data['units_damaged'] = pretty_quantity(row.units_damaged, empty_zero=True)
                data['cases_expired'] = pretty_quantity(row.cases_expired, empty_zero=True)
                data['units_expired'] = pretty_quantity(row.units_expired, empty_zero=True)
                data['cases_mispick'] = pretty_quantity(row.cases_mispick, empty_zero=True)
                data['units_mispick'] = pretty_quantity(row.units_mispick, empty_zero=True)

            else: # no match in our batch, do full product search
                product = api.get_product_by_upc(Session(), provided)
                if not product:
                    product = api.get_product_by_upc(Session(), checked)
                if product and (not product.deleted or self.request.has_perm('products.view_deleted')):
                    data['uuid'] = product.uuid
                    data['upc'] = unicode(product.upc)
                    data['upc_pretty'] = product.upc.pretty()
                    data['full_description'] = product.full_description
                    data['brand_name'] = unicode(product.brand or '')
                    data['description'] = product.description
                    data['size'] = product.size
                    data['case_quantity'] = 1 # default
                    cost = product.cost_for_vendor(batch.vendor)
                    if cost:
                        data['cost_found'] = True
                        data['cost_case_size'] = pretty_quantity(cost.case_size)
                        data['case_quantity'] = pretty_quantity(cost.case_size)
                    else:
                        data['cost_found'] = False
                    data['image_url'] = pod.get_image_url(self.rattail_config, product.upc)
                    data['found_in_batch'] = product in [row.product for row in batch.active_rows()]

        result = {'product': data or None, 'upc': None}
        if not data and upc:
            upc = GPC(upc)
            result['upc'] = unicode(upc)
            result['upc_pretty'] = upc.pretty()
            result['image_url'] = pod.get_image_url(self.rattail_config, upc)
        return result

    def mobile_menu(self):
        """
        Mobile menu page for purchasing/receiving batches
        """
        return self.render_to_response('menu', {}, mobile=True)

    def get_mobile_data(self, session=None):
        # TODO: for now, only show receiving batches..
        return self.get_data(session=session)\
                   .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)

    def mobile_create(self):
        """
        View for creating a new purchasing batch via mobile
        """
        # TODO: make this dynamic somehow, support other modes
        mode = self.enum.PURCHASE_BATCH_MODE_RECEIVING
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
                        self.request.session.flash("Created new purchasing batch: {}".format(batch))
                        # TODO: redirect to mobile receiving view etc. instead
                        return self.redirect(self.request.route_url('purchases.batch.mobile_create'))

        data['mode_title'] = self.enum.PURCHASE_BATCH_MODE[mode].capitalize()
        if vendor:
            purchases = self.eligible_purchases(vendor.uuid, mode=mode)
            data['purchases'] = [(p['key'], p['display']) for p in purchases['purchases']]
        return self.render_to_response('mobile_create', data)

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # mobile menu
        config.add_route('{}.mobile_menu'.format(route_prefix), '/mobile{}/menu'.format(url_prefix))
        config.add_view(cls, attr='mobile_menu', route_name='{}.mobile_menu'.format(route_prefix),
                        permission='{}.list'.format(permission_prefix))

        # mobile create
        config.add_route('{}.mobile_create'.format(route_prefix), '/mobile{}/new'.format(url_prefix))
        config.add_view(cls, attr='mobile_create', route_name='{}.mobile_create'.format(route_prefix),
                        permission='{}.create'.format(permission_prefix))

        # eligible purchases (AJAX)
        config.add_route('{}.eligible_purchases'.format(route_prefix), '{}/eligible-purchases'.format(url_prefix))
        config.add_view(cls, attr='eligible_purchases', route_name='{}.eligible_purchases'.format(route_prefix),
                        renderer='json', permission='{}.view'.format(permission_prefix))

        # defaults
        cls._batch_defaults(config)
        cls._defaults(config)

        # extra perms for creating batches per "mode"
        config.add_tailbone_permission(permission_prefix, '{}.create.ordering'.format(permission_prefix),
                                       "Create new {} of mode 'ordering'".format(model_title))
        config.add_tailbone_permission(permission_prefix, '{}.create.receiving'.format(permission_prefix),
                                       "Create new {} of mode 'receiving'".format(model_title))
        config.add_tailbone_permission(permission_prefix, '{}.create.invoicing'.format(permission_prefix),
                                       "Create new {} of mode 'invoicing'".format(model_title))

        # ordering form
        config.add_tailbone_permission(permission_prefix, '{}.order_form'.format(permission_prefix),
                                       "Edit new {} in Order Form mode".format(model_title))
        config.add_route('{}.order_form'.format(route_prefix), '{}/{{{}}}/order-form'.format(url_prefix, model_key))
        config.add_view(cls, attr='order_form', route_name='{}.order_form'.format(route_prefix),
                        permission='{}.order_form'.format(permission_prefix))
        config.add_route('{}.order_form_update'.format(route_prefix), '{}/{{{}}}/order-form/update'.format(url_prefix, model_key))
        config.add_view(cls, attr='order_form_update', route_name='{}.order_form_update'.format(route_prefix),
                        renderer='json', permission='{}.order_form'.format(permission_prefix))

        # receiving form, lookup
        config.add_tailbone_permission(permission_prefix, '{}.receiving_form'.format(permission_prefix),
                                       "Edit 'receiving' {} in Receiving Form mode".format(model_title))
        config.add_route('{}.receiving_form'.format(route_prefix), '{}/{{{}}}/receiving-form'.format(url_prefix, model_key))
        config.add_view(cls, attr='receiving_form', route_name='{}.receiving_form'.format(route_prefix),
                        permission='{}.receiving_form'.format(permission_prefix))
        config.add_route('{}.receiving_lookup'.format(route_prefix), '{}/{{{}}}/receiving-form/lookup'.format(url_prefix, model_key))
        config.add_view(cls, attr='receiving_lookup', route_name='{}.receiving_lookup'.format(route_prefix),
                        renderer='json', permission='{}.receiving_form'.format(permission_prefix))


def includeme(config):
    PurchaseBatchView.defaults(config)
