import unittest

import apprenda_soc_client


class TestGetCustomProperties(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_custom_properties(self):
        client = self.get_client()

        props = client.get_custom_properties()

        self.assertIsNotNone(props)
        for prop in props:
            by_id = client.get_custom_properties(prop.name)

            self.assertIsNotNone(by_id)

    # def test_custom_property_crud(self):
    #     client = self.get_client()
    #
    #     val_options = ValueOptions(possible_values=['this', 'that'], default_values=['this'])
    #
    #     applicable = Applicability()
    #     applicable.applications = ApplicabilityApps(is_applied=True, is_component_level=False)
    #     applicable.compute_servers = ApplicabilityComputeServers(is_applied=True)
    #
    #     custom_property = CustomProperty(name='testProp', display_name="this is a test",
    #                                      description="and it shouldn't stick around",
    #                                      value_options=val_options, applicability=applicable)
    #
    #     client.add_custom_property(custom_property)
    #
    #     retrieved = client.get_custom_properties(custom_property.name)
    #
    #     self.assertIsNotNone(retrieved)
    #
    #     res = client.remove_custom_property(retrieved.id)
    #
    #     threw = False
    #     reget = None
    #     try:
    #         reget = client.get_custom_properties(custom_property.name)
    #     except KeyError:
    #         threw = True
    #
    #     self.assertIsNone(reget)
    #     self.assertTrue(threw)

    def get_client(self):
        client = apprenda_soc_client.ApprendaSOCClient("https://apps.apprenda.msterling10", "gsterling@apprenda.com",
                                                       "password")

        self.assertIsNotNone(client)
        self.assertIsNotNone(client.sessionToken)

        return client