# -*- coding: utf-8 -*-

from .context import mdspy

reload(mdspy)

import unittest
from smartobjects import SmartObjectsClient


class SmartObjectsTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_search_api(self):
        hostname = 'https://rest.sandbox.mnubo.com'
        client_id = "52WnB4443RqSRtinp1ROw8sG4POKrP5LOfPuXctGQWIblRRZD6"
        client_secret = "MvODHcM48EF0sBds7lA82ZpsfqJOIT2Dxd1dzUh16M7Zk5fnYr"
        mnubo_client = SmartObjectsClient(client_id, client_secret, hostname)

        query = {
            "from": "event",
            "select": [
                {
                    "count": "*"
                }
            ]
        }
        df_query = mdspy.smartobjects.search_api(query, mnubo_client)
        self.assertEqual(df_query['COUNT(*)'].values[0], 126056211)

        query = {
            "from": "event",
            "groupByTime": {
                "field": "x_timestamp",
                "interval": "month"
            },
            "select": [
                {
                    "count": "*"
                }
            ]
        }
        df_query = mdspy.smartobjects.search_api(query, mnubo_client, ['month'])
        self.assertEqual(df_query[df_query['month'] == '2000-01-01']['COUNT(*)'].values[0], 13)

    def test_empty_results(self):
        hostname = 'https://rest.sandbox.mnubo.com'
        client_id = "52WnB4443RqSRtinp1ROw8sG4POKrP5LOfPuXctGQWIblRRZD6"
        client_secret = "MvODHcM48EF0sBds7lA82ZpsfqJOIT2Dxd1dzUh16M7Zk5fnYr"
        mnubo_client = SmartObjectsClient(client_id, client_secret, hostname)

        query = {
            "from": "event",
            "where": {
                "and": [
                    {
                        "x_timestamp": {
                            "dateBetween": "1900-01-01T00:00:00-05:00",
                            "and": "1900-01-02T00:00:00-05:00"
                        }
                    }
                ]
            },
            "select": [
                {
                    "value": "button"
                }
            ]
        }
        df_query = mdspy.smartobjects.search_api(query, mnubo_client)
        print df_query
        self.assertEqual(df_query, [])


if __name__ == '__main__':
    unittest.main()
