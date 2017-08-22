from __future__ import unicode_literals

from wellaware.client import ControlRule, ControlRules, Token
from wellaware.tests.base import *


class ControlRuleTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'controlrules')
    @responses.activate
    def test_create_controlrule(self):
        rule = ControlRule(name='Test ControlRule')
        resp = {'name': 'Test ControlRule', 'id': 10}
        responses.add(responses.POST, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/rules',
                      json=resp, status=200)

        e = ControlRules.create(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4, control_rule=rule)
        self.assertIsInstance(e, ControlRule)
        self.assertEquals(rule.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'controlrules')
    @responses.activate
    def test_retrieve_one_controlrule(self):
        rule = ControlRule(name='Test ControlRule', id=10)
        resp = {'name': 'Test ControlRule', 'id': 10}
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/rules/10',
                      json=resp, status=200)

        e = ControlRules.retrieve_one(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4,
                                      control_rule_id=rule)
        self.assertIsInstance(e, ControlRule)
        self.assertEquals(rule.name, e.name)
        self.assertEquals(10, e.id)

        e = ControlRules.retrieve_one(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4,
                                      control_rule_id=rule.id)
        self.assertIsInstance(e, ControlRule)
        self.assertEquals(rule.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'controlrules')
    @responses.activate
    def test_retrieve_all_controlrules(self):
        rule = ControlRule(name='Test ControlRule', id=10)
        resp = [{'name': 'Test ControlRule', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/rules',
                      json=resp, status=200)

        el = ControlRules.retrieve_all(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(rule.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'controlrules')
    @responses.activate
    def test_update_controlrule(self):
        rule = ControlRule(name='Test ControlRule', id=10)
        resp = {'name': 'Test ControlRule', 'id': 10}
        responses.add(responses.PUT, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/rules/10',
                      json=resp, status=200)

        e = ControlRules.update(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4, control_rule=rule)
        self.assertIsInstance(e, ControlRule)
        self.assertEquals(rule.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'controlrules')
    @responses.activate
    def test_delete_controlrule(self):
        rule = ControlRule(name='Test ControlRule', id=10)
        resp = {'name': 'Test ControlRule', 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/sites/1/assets/2/points/3/controlpoints/4/rules/10',
                      body='', status=204)

        r = ControlRules.delete(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4, control_rule_id=rule)
        self.assertEquals(204, r.status_code)

        r = ControlRules.delete(self.token, site_id=1, asset_id=2, point_id=3, control_point_id=4,
                                control_rule_id=rule.id)
        self.assertEquals(204, r.status_code)
