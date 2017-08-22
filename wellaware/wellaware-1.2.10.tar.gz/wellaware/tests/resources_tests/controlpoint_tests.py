from __future__ import unicode_literals

from wellaware.client import ControlPoint, ControlPoints, ControlAudit, SetPointRequest, Token
from wellaware.tests.base import *


class ControlPointTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'control_points')
    def test_control_point_serialization(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False)
        jdict = control_point.get_json_data()
        self.assertDictContainsKeyWithValue(jdict, 'dataType', 'double')
        self.assertDictContainsKeyWithValue(jdict, 'name', 'Test ControlPoint')
        self.assertDictContainsKeyWithValue(jdict, 'enabled', True)
        self.assertDictContainsKeyWithValue(jdict, 'hidden', False)

    @attr('unit', 'control_points')
    def test_control_point_deserialization(self):
        jdata = {'name': 'Test ControlPoint', 'enabled': True, 'dataType': 'double', 'hidden': False, 'id': 10}
        control_point = ControlPoint.from_dict(jdata)
        self.assertEquals('Test ControlPoint', control_point.name)
        self.assertEquals(False, control_point.hidden)
        self.assertEquals(True, control_point.enabled)
        self.assertEquals('double', control_point.data_type)
        self.assertEquals(10, control_point.id)

    @attr('unit', 'control_points')
    @responses.activate
    def test_create_control_point(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False)
        resp = {'name': 'Test ControlPoint', 'enabled': True, 'dataType': 'double', 'hidden': False, 'id': 10}
        responses.add(responses.POST, 'http://localhost/sites/1/assets/2/points/3/controlpoints', json=resp, status=200)

        e = ControlPoints.create(self.token, site_id=1, asset_id=2, point_id=3, control_point=control_point)
        self.assertIsInstance(e, ControlPoint)
        self.assertEquals(control_point.name, e.name)
        self.assertEquals(control_point.enabled, e.enabled)
        self.assertEquals(control_point.data_type, e.data_type)
        self.assertEquals(control_point.hidden, e.hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'control_points')
    @responses.activate
    def test_retrieve_one_control_point(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        resp = {'name': 'Test ControlPoint', 'enabled': True, 'dataType': 'double', 'hidden': False, 'id': 10}
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points/3/controlpoints/10', json=resp,
                      status=200)

        e = ControlPoints.retrieve_one(self.token, site_id=1, asset_id=2, point_id=3,
                                         control_point_id=control_point.id)
        self.assertIsInstance(e, ControlPoint)
        self.assertEquals(control_point.name, e.name)
        self.assertEquals(control_point.enabled, e.enabled)
        self.assertEquals(control_point.data_type, e.data_type)
        self.assertEquals(control_point.hidden, e.hidden)
        self.assertEquals(10, e.id)

        e = ControlPoints.retrieve_one(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=control_point)
        self.assertIsInstance(e, ControlPoint)
        self.assertEquals(control_point.name, e.name)
        self.assertEquals(control_point.enabled, e.enabled)
        self.assertEquals(control_point.data_type, e.data_type)
        self.assertEquals(control_point.hidden, e.hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'control_points')
    @responses.activate
    def test_retrieve_all_control_points(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        resp = [{'name': 'Test ControlPoint', 'enabled': True, 'dataType': 'double', 'hidden': False, 'id': 10}]
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points/3/controlpoints', json=resp, status=200)

        el = ControlPoints.retrieve_all(self.token, site_id=1, asset_id=2, point_id=3)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(control_point.name, e.name)
        self.assertEquals(control_point.enabled, e.enabled)
        self.assertEquals(control_point.data_type, e.data_type)
        self.assertEquals(control_point.hidden, e.hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'control_points')
    @responses.activate
    def test_update_control_point(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        resp = {'name': 'Test ControlPoint', 'enabled': True, 'dataType': 'double', 'hidden': False, 'id': 10}
        responses.add(responses.PUT, 'http://localhost/sites/1/assets/2/points/3/controlpoints/10', json=resp,
                      status=200)

        e = ControlPoints.update(self.token, site_id=1, asset_id=2, point_id=3, control_point=control_point)
        self.assertIsInstance(e, ControlPoint)
        self.assertEquals(control_point.name, e.name)
        self.assertEquals(control_point.enabled, e.enabled)
        self.assertEquals(control_point.data_type, e.data_type)
        self.assertEquals(control_point.hidden, e.hidden)
        self.assertEquals(10, e.id)

    @attr('unit', 'control_points')
    @responses.activate
    def test_delete_control_point(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        resp = {'name': 'Test ControlPoint', 'enabled': True, 'dataType': 'double', 'hidden': False, 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/sites/1/assets/2/points/3/controlpoints/10', body='',
                      status=204)

        r = ControlPoints.delete(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=control_point)
        self.assertEquals(204, r.status_code)

        r = ControlPoints.delete(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=control_point.id)
        self.assertEquals(204, r.status_code)

    @attr('unit', 'control_points')
    @responses.activate
    def test_control_on_demand_read(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        resp = {'status': 'pending', 'quality': 'uncertain', 'id': 100, 'requestType': 'ondemandread'}

        responses.add(responses.POST, 'http://localhost/sites/1/assets/2/points/3/controlpoints/10/read', json=resp,
                      status=200)

        e = ControlPoints.on_demand_read(self.token, site_id=1, asset_id=2, point_id=3,
                                           control_point_id=control_point)
        self.assertIsInstance(e, ControlAudit)
        self.assertEquals('pending', e.status)
        self.assertEquals('uncertain', e.quality)
        self.assertEquals('ondemandread', e.request_type)
        self.assertEquals(100, e.id)

    @attr('unit', 'control_points')
    @responses.activate
    def test_control_on_demand_read_options(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        headers={'Allow': 'OPTIONS,POST'}

        responses.add(responses.OPTIONS, 'http://localhost/sites/1/assets/2/points/3/controlpoints/10/read', body='',
                      adding_headers=headers, status=200)

        e = ControlPoints.on_demand_read_options(self.token, site_id=1, asset_id=2, point_id=3,
                                                   control_point_id=control_point)
        self.assertIsInstance(e, list)
        self.assertListEqual(['OPTIONS', 'POST'], e)

    @attr('unit', 'control_points')
    @responses.activate
    def test_control_set(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        set_point_request = SetPointRequest(value=3, previous_value=1)
        resp = {'status': 'pending', 'quality': 'uncertain', 'id': 100, 'requestType': 'setpointchange'}

        responses.add(responses.POST, 'http://localhost/sites/1/assets/2/points/3/controlpoints/10/set', json=resp,
                      status=200)

        e = ControlPoints.on_demand_set(self.token, site_id=1, asset_id=2, point_id=3,
                                          control_point_id=control_point, set_point_request=set_point_request)

        self.assertIsInstance(e, ControlAudit)
        self.assertEquals('pending', e.status)
        self.assertEquals('uncertain', e.quality)
        self.assertEquals('setpointchange', e.request_type)
        self.assertEquals(100, e.id)

    @attr('unit', 'control_points')
    @responses.activate
    def test_control_set_options(self):
        control_point = ControlPoint(name='Test ControlPoint', enabled=True, data_type='double', hidden=False, id=10)
        headers = {'Allow': 'OPTIONS,POST'}

        responses.add(responses.OPTIONS, 'http://localhost/sites/1/assets/2/points/3/controlpoints/10/set', body='',
                      adding_headers=headers, status=200)

        e = ControlPoints.on_demand_set_options(self.token, site_id=1, asset_id=2, point_id=3,
                                                  control_point_id=control_point)
        self.assertIsInstance(e, list)
        self.assertListEqual(['OPTIONS', 'POST'], e)
