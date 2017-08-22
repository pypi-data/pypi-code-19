from __future__ import unicode_literals

from wellaware.client import Tenant, Tenants, Token
from wellaware.tests.base import *


class TenantTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'tenants')
    @responses.activate
    def test_create_tenant(self):
        tenant = Tenant(name='Test Tenant', timezone='America/Chicago', effective_timestamp=12345)
        resp = {'name': 'Test Tenant', 'timezone': 'America/Chicago', 'effectiveTimestamp': 12345, 'id': 10}
        responses.add(responses.POST, 'http://localhost/tenants', json=resp, status=200)

        t = Tenants.create(self.token, tenant=tenant)
        self.assertIsInstance(t, Tenant)
        self.assertEquals(tenant.name, t.name)
        self.assertEquals(tenant.timezone, t.timezone)
        self.assertEquals(tenant.effective_timestamp, t.effective_timestamp)
        self.assertEquals(10, t.id)

    @attr('unit', 'tenants')
    @responses.activate
    def test_retrieve_one_tenant(self):
        tenant = Tenant(name='Test Tenant', timezone='America/Chicago', effective_timestamp=56789, id=10)
        resp = {'name': 'Test Tenant', 'timezone': 'America/Chicago', 'effectiveTimestamp': 56789, 'id': 10}
        responses.add(responses.GET, 'http://localhost/tenants/10', json=resp, status=200)

        t = Tenants.retrieve_one(self.token, tenant_id=tenant.id)
        self.assertIsInstance(t, Tenant)
        self.assertEquals(tenant.name, t.name)
        self.assertEquals(tenant.timezone, t.timezone)
        self.assertEquals(tenant.effective_timestamp, t.effective_timestamp)
        self.assertEquals(10, t.id)

        t = Tenants.retrieve_one(self.token, tenant_id=tenant)
        self.assertIsInstance(t, Tenant)
        self.assertEquals(tenant.name, t.name)
        self.assertEquals(tenant.timezone, t.timezone)
        self.assertEquals(tenant.effective_timestamp, t.effective_timestamp)
        self.assertEquals(10, t.id)

    @attr('unit', 'tenants')
    @responses.activate
    def test_retrieve_all_tenants(self):
        tenant = Tenant(name='Test Tenant', timezone='America/Chicago', effective_timestamp=12345)
        resp = [{'name': 'Test Tenant', 'timezone': 'America/Chicago', 'effectiveTimestamp': 12345, 'id': 10}]
        responses.add(responses.GET, 'http://localhost/tenants', json=resp, status=200)

        tl = Tenants.retrieve_all(self.token)
        self.assertIsInstance(tl, list)
        t = tl[0]
        self.assertEquals(tenant.name, t.name)
        self.assertEquals(tenant.timezone, t.timezone)
        self.assertEquals(tenant.effective_timestamp, t.effective_timestamp)
        self.assertEquals(10, t.id)

    @attr('unit', 'tenants')
    @responses.activate
    def test_retrieve_my_tenant(self):
        tenant = Tenant(name='Test Tenant', timezone='America/Chicago', effective_timestamp=56789, id=10)
        resp = {'name': 'Test Tenant', 'timezone': 'America/Chicago', 'effectiveTimestamp': 56789, 'id': 10}
        responses.add(responses.GET, 'http://localhost/tenants/me', json=resp, status=200)

        t = Tenants.me(self.token)
        self.assertIsInstance(t, Tenant)
        self.assertEquals(tenant.name, t.name)
        self.assertEquals(tenant.timezone, t.timezone)
        self.assertEquals(tenant.effective_timestamp, t.effective_timestamp)
        self.assertEquals(10, t.id)

    @attr('unit', 'tenants')
    @responses.activate
    def test_update_tenant(self):
        tenant = Tenant(name='Test Tenant', timezone='America/Chicago', effective_timestamp=56789, id=10)
        resp = {'name': 'Test Tenant', 'timezone': 'America/Chicago', 'effectiveTimestamp': 56789, 'id': 10}
        responses.add(responses.PUT, 'http://localhost/tenants/10', json=resp, status=200)

        t = Tenants.update(self.token, tenant=tenant)
        self.assertIsInstance(t, Tenant)
        self.assertEquals(tenant.name, t.name)
        self.assertEquals(tenant.timezone, t.timezone)
        self.assertEquals(tenant.effective_timestamp, t.effective_timestamp)
        self.assertEquals(10, t.id)

    @attr('unit', 'tenants')
    @responses.activate
    def test_delete_tenant(self):
        tenant = Tenant(name='Test Tenant', timezone='America/Chicago', effective_timestamp=56789, id=10)
        resp = {'name': 'Test Tenant', 'timezone': 'America/Chicago', 'effectiveTimestamp': 56789, 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/tenants/10', body='', status=204)

        r = Tenants.delete(self.token, tenant_id=tenant)
        self.assertEquals(204, r.status_code)

        r = Tenants.delete(self.token, tenant_id=tenant.id)
        self.assertEquals(204, r.status_code)
