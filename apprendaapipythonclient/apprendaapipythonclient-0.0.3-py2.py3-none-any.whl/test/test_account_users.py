import unittest
from apprenda_account_client import ApprendaAccountClient


def get_client():
    return ApprendaAccountClient('https://apps.apprenda.msterling10', 'gsterling@apprenda.com', 'password')


class TestAccountUsers(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_users(self):
        client = get_client()

        users = client.get_users()

        self.assertIsNotNone(users)

        # for user in users:
        #     by_id = client.get_user(user.identifier)
        #
        #     self.assertIsNotNone(by_id)
        #     self.assertEqual(user.last_name, by_id.last_name)

    def test_create_user(self):
        client = get_client()

        try:
            client.delete_user("test@test.com")
        except KeyError:
            pass

        created = client.create_user("testy", "mctesterson", "test@test.com", "test@test.com", True)

        self.assertIsNotNone(created)
        self.assertEqual("testy", created.first_name)

        client.delete_user(created.identifier)