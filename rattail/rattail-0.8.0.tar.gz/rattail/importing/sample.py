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
Sample -> Rattail data import
"""

from __future__ import unicode_literals, absolute_import

import os
import logging

from rattail import importing
from rattail.util import OrderedDict
from rattail.csvutil import UnicodeDictReader
from rattail.files import resource_path
from rattail.config import parse_bool


log = logging.getLogger(__name__)


class FromSampleToRattail(importing.ToRattailHandler):
    """
    Handler for Sample -> Rattail data import.
    """
    host_title = "Sample"
    local_title = "Rattail"

    def get_importers(self):
        importers = OrderedDict()
        importers['Person'] = PersonImporter
        importers['User'] = UserImporter
        importers['Store'] = StoreImporter
        importers['Employee'] = EmployeeImporter
        importers['EmployeeStore'] = EmployeeStoreImporter
        importers['Customer'] = CustomerImporter
        importers['CustomerPerson'] = CustomerPersonImporter
        importers['Vendor'] = VendorImporter
        importers['VendorContact'] = VendorContactImporter
        importers['Department'] = DepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Brand'] = BrandImporter
        importers['Product'] = ProductImporter
        importers['ProductCost'] = ProductCostImporter
        # importers['ProductPrice'] = ProductPriceImporter
        return importers


class FromSample(importing.Importer):
    """
    Base class for Sample -> Rattail data importers.
    """

    @property
    def supported_fields(self):
        """
        Support all (but only) simple fields by default.
        """
        return self.simple_fields

    @property
    def filename(self):
        return '{}.csv'.format(self.model_name)

    def setup(self):
        if not hasattr(self, 'data_path'):
            self.data_path = resource_path('rattail:data/sample/{}'.format(self.filename))
            if not os.path.exists(self.data_path):
                log.warning("data path does not exist: {}".format(self.data_path))

    def get_host_objects(self):
        """
        Return all data rows from CSV file, as returned by CSV parser.
        """
        with open(self.data_path, 'rb') as csv_file:
            reader = UnicodeDictReader(csv_file)
            return list(reader)                


class PersonImporter(FromSample, importing.model.PersonImporter):

    supported_fields = [
        'uuid',
        'first_name',
        'middle_name',
        'last_name',
        'display_name',
    ]


class UserImporter(FromSample, importing.model.AdminUserImporter):

    supported_fields = [
        'uuid',
        'person_uuid',
        'username',
        'plain_password',
        'active',
        'admin',
    ]

    def normalize_host_object(self, row):
        data = dict(row)
        data['active'] = parse_bool(data['active']) if data['active'] else None
        data['admin'] = parse_bool(data['admin']) if data['admin'] else None
        return data


class StoreImporter(FromSample, importing.model.StoreImporter):

    supported_fields = [
        'uuid',
        'id',
        'name',
    ]


class EmployeeImporter(FromSample, importing.model.EmployeeImporter):

    def normalize_host_object(self, row):
        data = dict(row)
        data['id'] = int(data['id']) if data['id'] else None
        data['status'] = int(data['status']) if data['status'] else None
        return data


class EmployeeStoreImporter(FromSample, importing.model.EmployeeStoreImporter):
    pass

class CustomerImporter(FromSample, importing.model.CustomerImporter):
    pass

class CustomerPersonImporter(FromSample, importing.model.CustomerPersonImporter):
    pass


class VendorImporter(FromSample, importing.model.VendorImporter):

    supported_fields = [
        'uuid',
        'id',
        'name',
    ]


class VendorContactImporter(FromSample, importing.model.VendorContactImporter):
    pass

class DepartmentImporter(FromSample, importing.model.DepartmentImporter):
    pass

class SubdepartmentImporter(FromSample, importing.model.SubdepartmentImporter):
    pass

class BrandImporter(FromSample, importing.model.BrandImporter):
    pass


class ProductImporter(FromSample, importing.model.ProductImporter):

    supported_fields = [
        'uuid',
        'upc',
        'department_uuid',
        'subdepartment_uuid',
        'brand_uuid',
        'description',
        'size',
    ]


class ProductCostImporter(FromSample, importing.model.ProductCostImporter):

    supported_fields = [
        'uuid',
        'product_uuid',
        'vendor_uuid',
        'preference',
        'code',
        'case_size',
        'case_cost',
        'unit_cost',
    ]


# class ProductPriceImporter(FromSample, importing.model.ProductPriceImporter):
#     pass
