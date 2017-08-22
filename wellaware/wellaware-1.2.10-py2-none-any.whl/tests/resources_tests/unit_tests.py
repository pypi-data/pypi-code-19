from __future__ import unicode_literals

from wellaware.client import Unit, Units, Token
from wellaware.tests.base import *


class UnitTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)
    
    @attr('unit', 'units')
    def test_unit_serialization(self):
        unit = Unit(name='feet', abbreviation="ft", id=10)
        jdata = unit.get_json_data()
        self.assertDictContainsKeyWithValue(jdata, 'name', 'feet')
        self.assertDictContainsKeyWithValue(jdata, 'abbreviation', 'ft')
        self.assertDictContainsKeyWithValue(jdata, 'id', 10)

    @attr('unit', 'units')
    def test_unit_deserialization(self):
        jdata = {'name': 'feet', 'abbreviation': 'ft', 'id': 10}
        unit = Unit.from_dict(jdata)
        self.assertEquals('feet', unit.name)
        self.assertEquals('ft', unit.abbreviation)
        self.assertEquals(10, unit.id)

    @attr('unit', 'units')
    @responses.activate
    def test_create_unit(self):
        unit = Unit(name='Test Unit')
        resp = {'name': 'Test Unit', 'id': 10}
        responses.add(responses.POST, 'http://localhost/units', json=resp, status=200)

        e = Units.create(self.token, unit=unit)
        self.assertIsInstance(e, Unit)
        self.assertEquals(unit.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'units')
    @responses.activate
    def test_retrieve_one_unit(self):
        unit = Unit(name='Test Unit', id=10)
        resp = {'name': 'Test Unit', 'id': 10}
        responses.add(responses.GET, 'http://localhost/units/10', json=resp, status=200)

        e = Units.retrieve_one(self.token, unit_id=unit.id)
        self.assertIsInstance(e, Unit)
        self.assertEquals(unit.name, e.name)
        self.assertEquals(10, e.id)

        e = Units.retrieve_one(self.token, unit_id=unit)
        self.assertIsInstance(e, Unit)
        self.assertEquals(unit.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'units')
    @responses.activate
    def test_retrieve_all_units(self):
        unit = Unit(name='Test Unit', id=10)
        resp = [{'name': 'Test Unit', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/units', json=resp, status=200)

        el = Units.retrieve_all(self.token)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(unit.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'units')
    @responses.activate
    def test_update_unit(self):
        unit = Unit(name='Test Unit', id=10)
        resp = {'name': 'Test Unit', 'id': 10}
        responses.add(responses.PUT, 'http://localhost/units/10', json=resp, status=200)

        e = Units.update(self.token, unit=unit)
        self.assertIsInstance(e, Unit)
        self.assertEquals(unit.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'units')
    @responses.activate
    def test_delete_unit(self):
        unit = Unit(name='Test Unit', id=10)
        resp = {'name': 'Test Unit', 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/units/10', body='', status=204)

        r = Units.delete(self.token, unit_id=unit)
        self.assertEquals(204, r.status_code)

        r = Units.delete(self.token, unit_id=unit.id)
        self.assertEquals(204, r.status_code)
