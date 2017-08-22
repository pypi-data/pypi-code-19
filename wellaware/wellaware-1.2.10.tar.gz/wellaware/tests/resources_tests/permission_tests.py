from __future__ import unicode_literals

from wellaware.client import Permission, Permissions, Token
from wellaware.tests.base import *


class PermissionTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'permissions')
    @responses.activate
    def test_create_permission(self):
        permission = Permission(name='Test Permission')
        resp = {'name': 'Test Permission', 'id': 10}
        responses.add(responses.POST, 'http://localhost/roles/1/permissions', json=resp, status=200)

        e = Permissions.create(self.token, role_id=1, permission=permission)
        self.assertIsInstance(e, Permission)
        self.assertEquals(permission.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'permissions')
    @responses.activate
    def test_retrieve_one_permission(self):
        permission = Permission(name='Test Permission', id=10)
        resp = {'name': 'Test Permission', 'id': 10}
        responses.add(responses.GET, 'http://localhost/roles/1/permissions/10', json=resp, status=200)

        e = Permissions.retrieve_one(self.token, role_id=1, permission_id=permission)
        self.assertIsInstance(e, Permission)
        self.assertEquals(permission.name, e.name)
        self.assertEquals(10, e.id)

        e = Permissions.retrieve_one(self.token, role_id=1, permission_id=permission.id)
        self.assertIsInstance(e, Permission)
        self.assertEquals(permission.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'permissions')
    @responses.activate
    def test_retrieve_all_permissions(self):
        permission = Permission(name='Test Permission', id=10)
        resp = [{'name': 'Test Permission', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/roles/1/permissions', json=resp, status=200)

        el = Permissions.retrieve_all(self.token, role_id=1)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(permission.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'permissions')
    @responses.activate
    def test_update_permission(self):
        permission = Permission(name='Test Permission', id=10)
        resp = {'name': 'Test Permission', 'id': 10}
        responses.add(responses.PUT, 'http://localhost/roles/1/permissions/10', json=resp, status=200)

        e = Permissions.update(self.token, role_id=1, permission=permission)
        self.assertIsInstance(e, Permission)
        self.assertEquals(permission.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'permissions')
    @responses.activate
    def test_delete_permission(self):
        permission = Permission(name='Test Permission', id=10)
        resp = {'name': 'Test Permission', 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/roles/1/permissions/10', body='', status=204)

        r = Permissions.delete(self.token, role_id=1, permission_id=permission)
        self.assertEquals(204, r.status_code)

        r = Permissions.delete(self.token, role_id=1, permission_id=permission.id)
        self.assertEquals(204, r.status_code)
