import mock
import unittest

from pastry.resources.users import Users


class UsersTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.users.Base.index', return_value='index')
    def test_index(self, base):
        self.assertEqual(Users.index(), 'index')

    @mock.patch('pastry.resources.users.Base.get', return_value='user')
    def test_get(self, base):
        self.assertEqual(Users.get('username'), 'user')

    @mock.patch('pastry.resources.users.Base.create', return_value='user')
    def test_create(self, base):
        self.assertEqual(Users.create({}), 'user')

    @mock.patch('pastry.resources.users.Base.update', return_value='user')
    def test_update(self, base):
        self.assertEqual(Users.update('user', {}), 'user')

    @mock.patch('pastry.resources.users.Base.delete', return_value='user')
    def test_delete(self, base):
        self.assertEqual(Users.delete('user'), 'user')

    @mock.patch('pastry.resources.users.Base.exists', return_value=True)
    def test_exists(self, base):
        self.assertEqual(Users.exists('user'), True)
