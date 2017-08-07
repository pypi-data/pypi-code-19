import json
import sys
import unittest
try:
    from unittest import mock
except ImportError:
    from mock import mock
sys.modules['helga.plugins'] = mock.Mock() # hack to avoid py3 errors in test
from helga.db import db
from helga_trade.helga_trade import logic, fetch_crypto_data, try_crypto


CRYPTO_BTC = """
{
"USD": 3274.73
}
"""
CRYPTO_COINLIST = """
{
"Response": "Success",
"Message": "Coin list succesfully returned!",
"BaseImageUrl": "https://www.cryptocompare.com",
"BaseLinkUrl": "https://www.cryptocompare.com",
"Data": {
  "BTC": {
    "Id": "1111",
    "Url": "/coins/btc/overview",
    "ImageUrl": "/media/12345/btc.png",
    "Name": "BTC",
    "CoinName": "Bitcoin",
    "FullName": "Bitcoin (BTC)",
    "Algorithm": "Scrypt",
    "ProofType": "PoW",
    "SortOrder": "2"
  }
},
"Type": 100
}
"""


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def json(self):
            return json.loads(self.content)

    if 'data/price' in args[0]:
        return MockResponse(CRYPTO_BTC, 200)
    elif 'data/coinlist' in args[0]:
        return MockResponse(CRYPTO_COINLIST, 200)
    return MockResponse({}, 404)


class Testtrade(unittest.TestCase):
    @mock.patch('helga_trade.helga_trade.requests.get', side_effect=mocked_requests_get)
    def test_fetch_crypto_data(self, mock_get):
        data = fetch_crypto_data()
        self.assertEqual('1111', data['btc']['Id'])

    @mock.patch('helga_trade.helga_trade.requests.get', side_effect=mocked_requests_get)
    def test_try_crypto(self, mock_get):
        price = try_crypto('btc')
        self.assertEqual(3274.73, price)
        try:
            try_crypto('ltc')
            self.assertEqual('Exception!', 'Should be thrown')
        except ValueError:
            print('Exception thrown, good job :)')


if __name__ == '__main__':
    unittest.main()
