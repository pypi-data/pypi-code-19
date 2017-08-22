from __future__ import unicode_literals

from wellaware.client import ControlAudits, ControlAudit, Token
from wellaware.tests.base import *


class ControlAuditTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'control_audits')
    def test_control_audit_serialization(self):
        control_audit = ControlAudit(status='pending', quality='uncertain', request_type='ondemandread')
        jdict = control_audit.get_json_data()
        self.assertDictContainsKeyWithValue(jdict, 'status', 'pending')
        self.assertDictContainsKeyWithValue(jdict, 'quality', 'uncertain')
        self.assertDictContainsKeyWithValue(jdict, 'requestType', 'ondemandread')

    @attr('unit', 'control_audits')
    def test_control_audit_deserialization(self):
        jdata = {'status': 'pending', 'quality': 'uncertain', 'requestType': 'ondemandread', 'id': 10}
        control_audit = ControlAudit.from_dict(jdata)
        self.assertEquals('pending', control_audit.status)
        self.assertEquals('uncertain', control_audit.quality)
        self.assertEquals('ondemandread', control_audit.request_type)
        self.assertEquals(10, control_audit.id)

        self.assertTrue(control_audit.quality_is_uncertain)
        self.assertFalse(control_audit.quality_is_bad)
        self.assertFalse(control_audit.quality_is_good)
        self.assertTrue(control_audit.status_is_pending)
        self.assertFalse(control_audit.status_is_failed)
        self.assertFalse(control_audit.status_is_success)
        self.assertTrue(control_audit.is_on_demand_read)
        self.assertFalse(control_audit.is_on_demand_set)

    @attr('unit', 'control_audits')
    @responses.activate
    def test_retrieve_one_control_audit(self):
        control_audit = ControlAudit(status='pending', quality='uncertain', request_type='ondemandread', id=10)
        resp = {'status': 'pending', 'quality': 'uncertain', 'requestType': 'ondemandread', 'id': 10}
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/audits/10', json=resp,
                      status=200)

        e = ControlAudits.retrieve_one(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4,
                                         control_audit_id=control_audit.id)
        self.assertIsInstance(e, ControlAudit)
        self.assertEquals(control_audit.quality, e.quality)
        self.assertEquals(control_audit.status, e.status)
        self.assertEquals(control_audit.request_type, e.request_type)
        self.assertEquals(10, e.id)

        e = ControlAudits.retrieve_one(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4,
                                         control_audit_id=control_audit)
        self.assertIsInstance(e, ControlAudit)
        self.assertEquals(control_audit.quality, e.quality)
        self.assertEquals(control_audit.status, e.status)
        self.assertEquals(control_audit.request_type, e.request_type)
        self.assertEquals(10, e.id)

    @attr('unit', 'control_audits')
    @responses.activate
    def test_retrieve_all_control_audits(self):
        control_audit = ControlAudit(status='pending', quality='uncertain', request_type='ondemandread', id=10)
        resp = [{'status': 'pending', 'quality': 'uncertain', 'requestType': 'ondemandread', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/audits', json=resp, status=200)

        el = ControlAudits.retrieve_all(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(control_audit.quality, e.quality)
        self.assertEquals(control_audit.status, e.status)
        self.assertEquals(control_audit.request_type, e.request_type)
        self.assertEquals(10, e.id)

    @attr('unit', 'control_audits')
    @responses.activate
    def test_update_control_audit(self):
        control_audit = ControlAudit(status='pending', quality='uncertain', request_type='ondemandread', id=10)
        resp = {'status': 'pending', 'quality': 'uncertain', 'requestType': 'ondemandread', 'id': 10}
        responses.add(responses.PUT, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/audits/10', json=resp,
                      status=200)

        e = ControlAudits.update(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4,
                                   control_audit=control_audit)
        self.assertIsInstance(e, ControlAudit)
        self.assertEquals(control_audit.quality, e.quality)
        self.assertEquals(control_audit.status, e.status)
        self.assertEquals(control_audit.request_type, e.request_type)
        self.assertEquals(10, e.id)
