import datetime
from unittest import TestCase

from golosdata.utils import typify


class UtilsTest(TestCase):

    def test_typify(self):
        untyped = {'balance': '203.259 GOLOS',
                   'created': '2016-11-18T10:41:42',
                   'last_account_recovery': '1970-01-01T00:00:00',
                   'last_account_update': '2017-08-01T06:53:24',
                   'last_active_proved': '1970-01-01T00:00:00',
                   'last_bandwidth_update': '2017-08-05T10:38:18',
                   'last_market_bandwidth_update': '2017-08-04T08:10:12',
                   'last_owner_proved': '1970-01-01T00:00:00',
                   'last_owner_update': '2017-08-01T06:53:24',
                   'last_post': '2017-08-05T10:38:18',
                   'last_root_post': '2017-08-05T09:32:51',
                   'last_vote_time': '2017-08-05T10:05:30',
                   'lifetime_bandwidth': '6008163000000',
                   'lifetime_vote_count': 0,
                   'new_average_bandwidth': '223669710595',
                   'new_average_market_bandwidth': '32920383728',
                   'owner_challenged': False,
                   'post_bandwidth': 14091,
                   'recovery_account': 'golosio',
                   'reputation': '125050204777407',
                   'savings_balance': '0.000 GOLOS',
                   'savings_sbd_balance': '0.009 GBG',
                   'savings_sbd_seconds': '2277',
                   'savings_withdraw_requests': 0,
                   'sbd_balance': '5757.191 GBG',
                   'sbd_seconds': '3049229894037',
                   'to_withdraw': 0,
                   'vesting_balance': '0.000 GOLOS',
                   'vesting_shares': '103385172.249067 GESTS',
                   'vesting_withdraw_rate': '0.000000 GESTS'
                   }

        typed = {'balance': {'amount': 203.259, 'asset': 'GOLOS'},
                 'created': datetime.datetime(2016, 11, 18, 10, 41, 42),
                 'last_account_recovery': datetime.datetime(1970, 1, 1, 0, 0),
                 'last_account_update': datetime.datetime(2017, 8, 1, 6, 53, 24),
                 'last_active_proved': datetime.datetime(1970, 1, 1, 0, 0),
                 'last_bandwidth_update': datetime.datetime(2017, 8, 5, 10, 38, 18),
                 'last_market_bandwidth_update': datetime.datetime(2017, 8, 4, 8, 10, 12),
                 'last_owner_proved': datetime.datetime(1970, 1, 1, 0, 0),
                 'last_owner_update': datetime.datetime(2017, 8, 1, 6, 53, 24),
                 'last_post': datetime.datetime(2017, 8, 5, 10, 38, 18),
                 'last_root_post': datetime.datetime(2017, 8, 5, 9, 32, 51),
                 'last_vote_time': datetime.datetime(2017, 8, 5, 10, 5, 30),
                 'lifetime_bandwidth': '6008163000000',
                 'lifetime_vote_count': 0,
                 'new_average_bandwidth': '223669710595',
                 'new_average_market_bandwidth': '32920383728',
                 'owner_challenged': False,
                 'post_bandwidth': 14091,
                 'recovery_account': 'golosio',
                 'reputation': '125050204777407',
                 'savings_balance': {'amount': 0.000, 'asset': 'GOLOS'},
                 'savings_sbd_balance': {'amount': 0.009, 'asset': 'GBG'},
                 'savings_sbd_seconds': '2277',
                 'savings_withdraw_requests': 0,
                 'sbd_balance': {'amount': 5757.191, 'asset': 'GBG'},
                 'sbd_seconds': '3049229894037',
                 'to_withdraw': 0,
                 'vesting_balance': {'amount': 0.000, 'asset': 'GOLOS'},
                 'vesting_shares':  {'amount': 103385172.249067, 'asset': 'GESTS'},
                 'vesting_withdraw_rate': {'amount': 0.000000, 'asset': 'GESTS'},
                 }

        self.assertEqual(typify(untyped), typed)
