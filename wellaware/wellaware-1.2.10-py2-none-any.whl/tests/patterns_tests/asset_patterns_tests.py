from __future__ import unicode_literals

from wellaware._compat import array_types
from wellaware.client import Asset, Assets, Token, AssetPatterns, Point, DataRetrieveResponse, Observation
from wellaware.tests.base import *


class AssetPatternsTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'assets', 'patterns')
    @responses.activate
    def test_asset_retrieve_data(self):
        # GET /assets?assetType=TANK
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        resp = [{'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'TANK', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/assets?assetType=TANK?limit=1000&offset=0',
                      json=resp, status=200, match_querystring=True)

        # GET /sites/0/assets/<asset.id>/points
        point = Point(name='Test Point', timezone='America/Chicago', point_type='TOP_GAUGE')
        resp = [{'name': 'Test Point', 'timezone': 'America/Chicago', 'point_type': 'TOP_GAUGE', 'id': 11}]
        responses.add(responses.GET, 'http://localhost/sites/0/assets/10/points?limit=1000&offset=0',
                      json=resp, status=200, match_querystring=True)

        # POST /data/retrieve
        resp = {'errors': [
        ], 'observations': {
            '11': [{'timestamp': 12345, 'value': 'test'}]
        }}
        responses.add(responses.POST, 'http://localhost/data/retrieve?start=0&end=100000', json=resp, status=200,
                      match_querystring=True)

        data = AssetPatterns.retrieve_data(self.token, asset_id=10, start=0, end=100000)
        self.assertIsInstance(data, DataRetrieveResponse)
        self.assertEquals(1, len(data.observations))
        self.assertIsInstance(data.observations[11][0], Observation)
        o = data.observations[11][0]
        self.assertEquals(12345, o.timestamp)
        self.assertEquals('test', o.value)

    @attr('unit', 'assets', 'patterns')
    @responses.activate
    def test_find_assets_by_asset_type(self):
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        resp = [{'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'TANK', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/assets?assetType=TANK&offset=0&limit=1000',
                      json=resp, status=200, match_querystring=True)

        al = AssetPatterns.find_assets_by_asset_type(self.token, asset_type_filter=asset.asset_type)
        self.assertIsInstance(al, array_types)
        self.assertEqual(1, len(al))
        a = al[0]
        self.assertIsInstance(a, Asset)
        self.assertEquals(asset.name, a.name)
        self.assertEquals(asset.timezone, a.timezone)
        self.assertEquals(asset.asset_type, a.asset_type)
        self.assertEquals(10, a.id)

    @attr('unit', 'assets', 'patterns')
    @responses.activate
    def test_find_assets_by_parameter_point_value(self):
        asset = Asset(name='Test Asset', timezone='America/Chicago', asset_type='WELL')
        point = Point(name='Test Parameter', timezone='America/Chicago', point_type='API_NUMBER', data_type='string',
                      unit='none')

        assets_resp = [{'id': 10, 'name': 'Test Asset', 'timezone': 'America/Chicago', 'assetType': 'WELL'}]
        points_resp = [{'id': 11, 'name': 'Test Parameter', 'timezone': 'America/Chicago', 'pointType': 'API_NUMBER',
                        'dataType': 'string', 'unit': 'none'}]
        data_resp = {
            'errors': [],
            'observations': {
                '11': [
                    {'timestamp': 12345, 'value': 'test'}
                ]
            }
        }

        responses.add(responses.GET, 'http://localhost/assets?assetType=WELL&limit=1000&offset=0',
                      json=assets_resp, status=200, match_querystring=True)
        responses.add(responses.GET,
                      'http://localhost/sites/0/assets/10/points?pointType=API_NUMBER&limit=1000&offset=0',
                      json=points_resp, status=200, match_querystring=True)
        responses.add(responses.POST, 'http://localhost/data/retrieve?start=0&limit=1&order=-timestamp',
                      json=data_resp, status=200, match_querystring=True)

        matching_assets = AssetPatterns.find_assets_by_parameter_point_value(
            token=self.token, asset_type_filter=asset.asset_type, parameter_point_type=point.point_type,
            parameter_point_value='test'
        )

        self.assertIsInstance(matching_assets, dict)
        asset, obs = matching_assets.items()[0]
        self.assertIsInstance(asset, Asset)
        self.assertIsInstance(obs, Observation)
        self.assertEquals(10, asset.id)
        self.assertEquals('test', obs.value)