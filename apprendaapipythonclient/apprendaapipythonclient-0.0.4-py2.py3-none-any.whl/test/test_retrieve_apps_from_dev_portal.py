import unittest
import apprenda_developer_client


class TestRetrieveAppsFromDevPortal(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # def test_canRetrieveAppsFromDevPortal(self):
    #     client = apprenda_developer_client.ApprendaDeveloperClient("https://apps.apprenda.msterling10", "gsterling@apprenda.com",
    #                                                    "password")
    #
    #     apps = client.get_applications()
    #     self.assertIsNotNone(apps)
    #
    #     for app in apps:
    #         by_id = client.get_application(app.alias)
    #
    #         self.assertIsNotNone(by_id)


