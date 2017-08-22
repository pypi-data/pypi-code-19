from __future__ import unicode_literals

from wellaware.client import Asset, Assets, Token
from wellaware.tests.base import *


class AssetTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'assets')
    @responses.activate
    def test_create_asset(self):
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        resp = {'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'TANK', 'id': 10}
        responses.add(responses.POST, 'http://localhost/sites/1/assets', json=resp, status=200)

        a = Assets.create(self.token, site_id=1, asset=asset)
        self.assertIsInstance(a, Asset)
        self.assertEquals(asset.name, a.name)
        self.assertEquals(asset.timezone, a.timezone)
        self.assertEquals(asset.asset_type, a.asset_type)
        self.assertEquals(10, a.id)

    @attr('unit', 'assets')
    @responses.activate
    def test_retrieve_one_asset(self):
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='TANK', id=10)
        resp = {'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'TANK', 'id': 10}
        responses.add(responses.GET, 'http://localhost/sites/1/assets/10', json=resp, status=200)

        a = Assets.retrieve_one(self.token, site_id=1, asset_id=asset.id)
        self.assertIsInstance(a, Asset)
        self.assertEquals(asset.name, a.name)
        self.assertEquals(asset.timezone, a.timezone)
        self.assertEquals(asset.asset_type, a.asset_type)
        self.assertEquals(10, a.id)

        a = Assets.retrieve_one(self.token, site_id=1, asset_id=asset)
        self.assertIsInstance(a, Asset)
        self.assertEquals(asset.name, a.name)
        self.assertEquals(asset.timezone, a.timezone)
        self.assertEquals(asset.asset_type, a.asset_type)
        self.assertEquals(10, a.id)

    @attr('unit', 'assets')
    @responses.activate
    def test_retrieve_all_assets(self):
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        resp = [{'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'TANK', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/sites/1/assets', json=resp, status=200)

        al = Assets.retrieve_all(self.token, site_id=1)
        self.assertIsInstance(al, list)
        a = al[0]
        self.assertEquals(asset.name, a.name)
        self.assertEquals(asset.timezone, a.timezone)
        self.assertEquals(asset.asset_type, a.asset_type)
        self.assertEquals(10, a.id)

    @attr('unit', 'assets')
    @responses.activate
    def test_update_asset(self):
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='TANK', id=10)
        resp = {'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'TANK', 'id': 10}
        responses.add(responses.PUT, 'http://localhost/sites/1/assets/10', json=resp, status=200)

        a = Assets.update(self.token, site_id=1, asset=asset)
        self.assertIsInstance(a, Asset)
        self.assertEquals(asset.name, a.name)
        self.assertEquals(asset.timezone, a.timezone)
        self.assertEquals(asset.asset_type, a.asset_type)
        self.assertEquals(10, a.id)

    @attr('unit', 'assets')
    @responses.activate
    def test_delete_asset(self):
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='TANK', id=10)
        resp = {'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'TANK', 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/sites/1/assets/10', body='', status=204)

        r = Assets.delete(self.token, site_id=1, asset_id=asset)
        self.assertEquals(204, r.status_code)

        r = Assets.delete(self.token, site_id=1, asset_id=asset.id)
        self.assertEquals(204, r.status_code)
