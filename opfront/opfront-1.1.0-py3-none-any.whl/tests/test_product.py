from opfront.model import Model
from opfront.product import ProductResource

from unittest.mock import MagicMock

import unittest


class TestProductResource(unittest.TestCase):

    def setUp(self):
        super()
        self.resource = ProductResource('/products', MagicMock())

    def test_product_resource_get_model_builds_spectacle_from_data(self):
        prod_data = {
            'hello': 'world',
            'spectacle': {
                'id': '1234',
                'name': 'A Spectacle'
            }
        }

        product = self.resource._make_model(**prod_data)

        self.assertIsInstance(product.spectacle, Model)
        self.assertIsNot(product.spectacle._res, self.resource)

        self.assertEqual(product.spectacle.id, prod_data['spectacle']['id'])
