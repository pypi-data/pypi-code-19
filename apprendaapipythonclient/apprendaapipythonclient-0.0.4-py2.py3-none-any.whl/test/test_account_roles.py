import unittest
from apprenda_account_client import ApprendaAccountClient


class TestAccountRoles(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_roles(self):
        client = self.get_client()

        roles = client.get_roles()

        self.assertIsNotNone(roles)

        self.assertGreaterEqual(len(roles), 0)

        for role in roles:
            by_id = client.get_role(role.id)

            self.assertIsNotNone(by_id)
            self.assertEqual(role.name, by_id.name)

    # def test_create_role(self):
    #     client = self.get_client()
    #
    #     # noinspection PyBroadException
    #     try:
    #         roles = client.get_roles()
    #         for role in roles:
    #             if role.name == "test_role":
    #                 client.delete_role(role.id)
    #     except:
    #         pass
    #
    #     created = client.create_role("test_role", "automated testing")
    #
    #     self.assertIsNotNone(created)
    #
    #     get = client.get_role(created.id)
    #     self.assertIsNotNone(get)
    #     self.assertEqual(created.name, get.name)
    #     self.assertEqual(created.description, get.description)
    #
    #     client.delete_role(get.id)
    #
    #     thrown = False
    #     try:
    #         client.get_role(created.id)
    #     except KeyError:
    #         thrown = True
    #
    #     self.assertTrue(thrown)

    @staticmethod
    def get_client():
        return ApprendaAccountClient('https://apps.apprenda.msterling10', 'gsterling@apprenda.com', 'password')