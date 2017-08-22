from __future__ import unicode_literals

from wellaware.client import Site, Sites, Token
from wellaware.tests.base import *


class SiteTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'sites')
    @responses.activate
    def test_create_site(self):
        site = Site(name='Test Site', timezone='America/Chicago', latitude=1.0, longitude=2.0)
        resp = {'name': 'Test Site', 'timezone': 'America/Chicago', 'latitude': 1.0, 'id': 10, 'longitude': 2.0}
        responses.add(responses.POST, 'http://localhost/sites', json=resp, status=200)

        s = Sites.create(self.token, site=site)
        self.assertIsInstance(s, Site)
        self.assertEquals(site.name, s.name)
        self.assertEquals(site.timezone, s.timezone)
        self.assertEquals(site.latitude, s.latitude)
        self.assertEquals(site.longitude, s.longitude)
        self.assertEquals(10, s.id)

    @attr('unit', 'sites')
    @responses.activate
    def test_retrieve_one_site(self):
        site = Site(name='Test Site', timezone='America/Chicago', latitude=1.0, longitude=2.0, id=10)
        resp = {'name': 'Test Site', 'timezone': 'America/Chicago', 'latitude': 1.0, 'id': 10, 'longitude': 2.0}
        responses.add(responses.GET, 'http://localhost/sites/10', json=resp, status=200)

        s = Sites.retrieve_one(self.token, site_id=site.id)
        self.assertIsInstance(s, Site)
        self.assertEquals(site.name, s.name)
        self.assertEquals(site.timezone, s.timezone)
        self.assertEquals(site.latitude, s.latitude)
        self.assertEquals(site.longitude, s.longitude)
        self.assertEquals(10, s.id)

        s = Sites.retrieve_one(self.token, site_id=site)
        self.assertIsInstance(s, Site)
        self.assertEquals(site.name, s.name)
        self.assertEquals(site.timezone, s.timezone)
        self.assertEquals(site.latitude, s.latitude)
        self.assertEquals(site.longitude, s.longitude)
        self.assertEquals(10, s.id)

    @attr('unit', 'sites')
    @responses.activate
    def test_retrieve_all_sites(self):
        site = Site(name='Test Site', timezone='America/Chicago', latitude=1.0, longitude=2.0)
        resp = [{'name': 'Test Site', 'timezone': 'America/Chicago', 'latitude': 1.0, 'id': 10, 'longitude': 2.0}]
        responses.add(responses.GET, 'http://localhost/sites', json=resp, status=200)

        sl = Sites.retrieve_all(self.token)
        self.assertIsInstance(sl, list)
        s = sl[0]
        self.assertEquals(site.name, s.name)
        self.assertEquals(site.timezone, s.timezone)
        self.assertEquals(site.latitude, s.latitude)
        self.assertEquals(site.longitude, s.longitude)
        self.assertEquals(10, s.id)

    @attr('unit', 'sites')
    @responses.activate
    def test_update_site(self):
        site = Site(name='Test Site', timezone='America/Chicago', latitude=1.0, longitude=2.0, id=10)
        resp = {'name': 'Test Site', 'timezone': 'America/Chicago', 'latitude': 1.0, 'id': 10, 'longitude': 2.0}
        responses.add(responses.PUT, 'http://localhost/sites/10', json=resp, status=200)

        s = Sites.update(self.token, site=site)
        self.assertIsInstance(s, Site)
        self.assertEquals(site.name, s.name)
        self.assertEquals(site.timezone, s.timezone)
        self.assertEquals(site.latitude, s.latitude)
        self.assertEquals(site.longitude, s.longitude)
        self.assertEquals(10, s.id)

    @attr('unit', 'sites')
    @responses.activate
    def test_delete_site(self):
        site = Site(name='Test Site', timezone='America/Chicago', latitude=1.0, longitude=2.0, id=10)
        resp = {'name': 'Test Site', 'timezone': 'America/Chicago', 'latitude': 1.0, 'id': 10, 'longitude': 2.0}
        responses.add(responses.DELETE, 'http://localhost/sites/10', body='', status=204)

        r = Sites.delete(self.token, site_id=site)
        self.assertEquals(204, r.status_code)

        r = Sites.delete(self.token, site_id=site.id)
        self.assertEquals(204, r.status_code)
