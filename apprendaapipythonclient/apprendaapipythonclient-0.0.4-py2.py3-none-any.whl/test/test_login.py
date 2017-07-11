import unittest
import apprenda_soc_client
import apprenda_developer_client


class TestLogin(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_canConstructSOCClient(self):
        client = apprenda_soc_client.ApprendaSOCClient("https://apps.apprenda.msterling10", "gsterling@apprenda.com",
                                                       "password")

        self.assertIsNotNone(client)
        self.assertIsNotNone(client.sessionToken)

    def test_canConstructDeveloperClient(self):
        client = apprenda_developer_client.ApprendaDeveloperClient("https://apps.apprenda.msterling10",
                                                                   "gsterling@apprenda.com",
                                                                   "password")

        self.assertIsNotNone(client)
        self.assertIsNotNone(client.sessionToken)


if __name__ == '__main__':
    unittest.main()
