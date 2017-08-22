from __future__ import unicode_literals

from wellaware.client import Point, Points, Token
from wellaware.tests.base import *


class PointTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'points')
    @responses.activate
    def test_create_point(self):
        point = Point(name='Test Point', timezone='America/Chicago', point_type='VOLTAGE', data_type='double',
                      is_hidden=False)
        resp = {'name': 'Test Point', 'timezone': 'America/Chicago', 'pointType': 'VOLTAGE', 'dataType': 'double',
                'isHidden': False, 'id': 10}
        responses.add(responses.POST, 'http://localhost/sites/1/assets/2/points', json=resp, status=200)

        e = Points.create(self.token, site_id=1, asset_id=2, point=point)
        self.assertIsInstance(e, Point)
        self.assertEquals(point.name, e.name)
        self.assertEquals(point.timezone, e.timezone)
        self.assertEquals(point.point_type, e.point_type)
        self.assertEquals(point.data_type, e.data_type)
        self.assertEquals(point.is_hidden, e.is_hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'points')
    @responses.activate
    def test_retrieve_one_point(self):
        point = Point(name='Test Point', timezone='America/Chicago', point_type='VOLTAGE', data_type='double',
                      is_hidden=False, id=10)
        resp = {'name': 'Test Point', 'timezone': 'America/Chicago', 'pointType': 'VOLTAGE', 'dataType': 'double',
                'isHidden': False, 'id': 10}
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points/10', json=resp, status=200)

        e = Points.retrieve_one(self.token, site_id=1, asset_id=2, point_id=point.id)
        self.assertIsInstance(e, Point)
        self.assertEquals(point.name, e.name)
        self.assertEquals(point.timezone, e.timezone)
        self.assertEquals(point.point_type, e.point_type)
        self.assertEquals(point.data_type, e.data_type)
        self.assertEquals(point.is_hidden, e.is_hidden)
        self.assertEquals(10, e.id)

        e = Points.retrieve_one(self.token, site_id=1, asset_id=2, point_id=point)
        self.assertIsInstance(e, Point)
        self.assertEquals(point.name, e.name)
        self.assertEquals(point.timezone, e.timezone)
        self.assertEquals(point.point_type, e.point_type)
        self.assertEquals(point.data_type, e.data_type)
        self.assertEquals(point.is_hidden, e.is_hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'points')
    @responses.activate
    def test_retrieve_all_points(self):
        point = Point(name='Test Point', timezone='America/Chicago', point_type='VOLTAGE', data_type='double',
                      is_hidden=False)
        resp = [{'name': 'Test Point', 'timezone': 'America/Chicago', 'pointType': 'VOLTAGE', 'dataType': 'double',
                 'isHidden': False, 'id': 10}]
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points', json=resp, status=200)

        el = Points.retrieve_all(self.token, site_id=1, asset_id=2)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(point.name, e.name)
        self.assertEquals(point.timezone, e.timezone)
        self.assertEquals(point.point_type, e.point_type)
        self.assertEquals(point.data_type, e.data_type)
        self.assertEquals(point.is_hidden, e.is_hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'points')
    @responses.activate
    def test_update_point(self):
        point = Point(name='Test Point', timezone='America/Chicago', point_type='VOLTAGE', data_type='double',
                      is_hidden=False, id=10)
        resp = {'name': 'Test Point', 'timezone': 'America/Chicago', 'pointType': 'VOLTAGE', 'dataType': 'double',
                'isHidden': False, 'id': 10}
        responses.add(responses.PUT, 'http://localhost/sites/1/assets/2/points/10', json=resp, status=200)

        e = Points.update(self.token, site_id=1, asset_id=2, point=point)
        self.assertIsInstance(e, Point)
        self.assertEquals(point.name, e.name)
        self.assertEquals(point.timezone, e.timezone)
        self.assertEquals(point.point_type, e.point_type)
        self.assertEquals(point.data_type, e.data_type)
        self.assertEquals(point.is_hidden, e.is_hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'points')
    @responses.activate
    def test_delete_point(self):
        point = Point(name='Test Point', timezone='America/Chicago', point_type='VOLTAGE', data_type='double',
                      is_hidden=False, id=10)
        resp = {'name': 'Test Point', 'timezone': 'America/Chicago', 'pointType': 'VOLTAGE', 'dataType': 'double',
                'isHidden': False, 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/sites/1/assets/2/points/10', body='', status=204)

        r = Points.delete(self.token, site_id=1, asset_id=2, point_id=point)
        self.assertEquals(204, r.status_code)

        r = Points.delete(self.token, site_id=1, asset_id=2, point_id=point.id)
        self.assertEquals(204, r.status_code)
