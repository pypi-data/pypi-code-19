from opfront.model import Model
from opfront.order import OrderResource

from unittest.mock import MagicMock

import unittest


class TestorderResource(unittest.TestCase):

    def setUp(self):
        super()
        self.resource = OrderResource('/orders', MagicMock())

    def test_order_resource_get_model_builds_store_and_products_from_data(self):
        order_data = {
            'hello': 'world',
            'store': {
                'id': '1234',
                'name': 'A store'
            },
            'products': [
                {
                    'id': 1
                },
                {
                    'id': 2
                }
            ]
        }

        order = self.resource._make_model(**order_data)

        self.assertIsInstance(order.store, Model)
        self.assertIsNot(order.store._res, self.resource)

        self.assertEqual(order.store.id, order_data['store']['id'])

        self.assertTrue(all([isinstance(x, Model) for x in order.products]))
        self.assertEqual([p.id for p in order.products], [p['id'] for p in order_data['products']])
