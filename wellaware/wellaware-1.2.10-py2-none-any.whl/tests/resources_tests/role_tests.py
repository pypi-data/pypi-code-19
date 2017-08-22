from __future__ import unicode_literals

from wellaware.client import Role, Roles, Token
from wellaware.tests.base import *


class RoleTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'roles')
    @responses.activate
    def test_create_role(self):
        role = Role(name='Test Role')
        resp = {'name': 'Test Role', 'id': 10}
        responses.add(responses.POST, 'http://localhost/roles', json=resp, status=200)

        e = Roles.create(self.token, role=role)
        self.assertIsInstance(e, Role)
        self.assertEquals(role.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'roles')
    @responses.activate
    def test_retrieve_one_role(self):
        role = Role(name='Test Role', id=10)
        resp = {'name': 'Test Role', 'id': 10}
        responses.add(responses.GET, 'http://localhost/roles/10', json=resp, status=200)

        e = Roles.retrieve_one(self.token, role_id=role.id)
        self.assertIsInstance(e, Role)
        self.assertEquals(role.name, e.name)
        self.assertEquals(10, e.id)

        e = Roles.retrieve_one(self.token, role_id=role)
        self.assertIsInstance(e, Role)
        self.assertEquals(role.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'roles')
    @responses.activate
    def test_retrieve_all_roles(self):
        role = Role(name='Test Role', id=10)
        resp = [{'name': 'Test Role', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/roles', json=resp, status=200)

        el = Roles.retrieve_all(self.token)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(role.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'roles')
    @responses.activate
    def test_update_role(self):
        role = Role(name='Test Role', id=10)
        resp = {'name': 'Test Role', 'id': 10}
        responses.add(responses.PUT, 'http://localhost/roles/10', json=resp, status=200)

        e = Roles.update(self.token, role=role)
        self.assertIsInstance(e, Role)
        self.assertEquals(role.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'roles')
    @responses.activate
    def test_delete_role(self):
        role = Role(name='Test Role', id=10)
        resp = {'name': 'Test Role', 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/roles/10', body='', status=204)

        r = Roles.delete(self.token, role_id=role)
        self.assertEquals(204, r.status_code)

        r = Roles.delete(self.token, role_id=role.id)
        self.assertEquals(204, r.status_code)
