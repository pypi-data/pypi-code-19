from __future__ import unicode_literals

from wellaware.client import Asset, Token
from wellaware.tests.base import *


class BaseEntityTest(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'base_entity')
    def test_dict_keys(self):
        asset = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        keys = asset.keys()
        self.assertEquals(4, len(keys))
        self.assertIn('id', keys)
        self.assertIn('name', keys)
        self.assertIn('timezone', keys)
        self.assertIn('asset_type', keys)

    @attr('unit', 'base_entity')
    def test_dict_values(self):
        asset = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        values = asset.values()
        self.assertEquals(4, len(values))
        self.assertIn(10, values)
        self.assertIn('Test Asset', values)
        self.assertIn('America/Chicago', values)
        self.assertIn('TANK', values)

    @attr('unit', 'base_entity')
    def test_dict_items(self):
        asset = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        items = asset.items()
        self.assertEquals(4, len(items))
        self.assertIn(('id', 10), items)
        self.assertIn(('name', 'Test Asset'), items)
        self.assertIn(('timezone', 'America/Chicago'), items)
        self.assertIn(('asset_type', 'TANK'), items)

    @attr('unit', 'base_entity')
    def test_equality(self):
        asset1 = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        asset2 = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        self.assertEquals(asset1, asset2)

        asset3 = Asset(id=11, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        self.assertNotEqual(asset1, asset3)

    @attr('unit', 'base_entity')
    def test_string_representation(self):
        asset = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        self.assertEquals("Asset(asset_type=TANK, id=10, name=Test Asset, timezone=America/Chicago)", str(asset))

    @attr('unit', 'base_entity')
    def test_json_representation(self):
        asset = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        self.assertEquals(
            '{"id": 10, "timezone": "America/Chicago", "name": "Test Asset", "assetType": "TANK"}',
            asset.to_json()
        )

    @attr('unit', 'base_entity')
    def test_from_json_representation(self):
        asset = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        asset_decoded = Asset.from_json(
            '{"id": 10, "timezone": "America/Chicago", "name": "Test Asset", "assetType": "TANK"}'
        )
        self.assertEquals(asset, asset_decoded)

    @attr('unit', 'base_entity')
    def test_from_dict_representation(self):
        asset = Asset(id=10, name='Test Asset', timezone='America/Chicago', asset_type='TANK')
        asset_decoded = Asset.from_dict(
            {"id": 10, "timezone": "America/Chicago", "name": "Test Asset", "assetType": "TANK"}
        )
        self.assertEquals(asset, asset_decoded)
