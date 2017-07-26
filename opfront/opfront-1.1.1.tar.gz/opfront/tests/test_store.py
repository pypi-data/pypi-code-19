from opfront.model import Model
from opfront.store import StoreResource

from unittest.mock import MagicMock

import unittest


class TestStoreResource(unittest.TestCase):

    def setUp(self):
        super()
        self.resource = StoreResource('/stores', MagicMock())

    def test_store_resource_get_model_builds_banner_from_data(self):
        store_data = {
            'hello': 'world',
            'banner': {
                'id': '1234',
                'name': 'A Banner'
            }
        }

        store = self.resource._make_model(**store_data)

        self.assertIsInstance(store.banner, Model)
        self.assertIsNot(store.banner._res, self.resource)

        self.assertEqual(store.banner.id, store_data['banner']['id'])
