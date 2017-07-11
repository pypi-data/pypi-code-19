import unittest
from apprenda_soc_client import ApprendaSOCClient


class TestSocRegistrySettings(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_registry_settings(self):
        client = self.get_client()

        regs = client.get_registry_settings()

        self.assertIsNotNone(regs)

        all_regs = []
        for reg in regs:
            by_id = client.get_registry_setting(reg.name)
            self.assertIsNotNone(by_id)
            self.assertEqual(reg.value, by_id.value)
            all_regs.append(reg)

        self.assertGreaterEqual(len(all_regs), 0)

    # def test_create_registry_settings(self):
    #     client = self.get_client()
    #
    #     test_name = "testsettingeh"
    #
    #     created = client.create_registry_setting(test_name, "boo")
    #     self.assertIsNotNone(created)
    #
    #     get = client.get_registry_setting(test_name)
    #
    #     self.assertIsNotNone(get)
    #     self.assertEqual("boo", get.value)
    #
    #     client.delete_registry_settting(test_name)
    #
    #     thrown = False
    #     try:
    #         client.get_registry_setting(test_name)
    #     except KeyError:
    #         thrown = True
    #
    #     self.assertTrue(thrown)

    @staticmethod
    def get_client():
        return ApprendaSOCClient('https://apps.apprenda.msterling10', 'gsterling@apprenda.com', 'password')