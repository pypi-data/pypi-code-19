"""
Tests get_item()

"""

import unittest

from algolia import HackerNews
from algolia import Item


class TestGetItem(unittest.TestCase):
    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        item = self.hn.get_item(11116274)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 11116274)
        self.assertEqual(item.author, "epaga")


if __name__ == '__main__':
    unittest.main()
