"""
Tests get_user()

"""

import unittest

from algolia import HackerNews
from algolia import User


class TestGetUser(unittest.TestCase):
    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        user = self.hn.get_user('epaga')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'epaga')


if __name__ == '__main__':
    unittest.main()
