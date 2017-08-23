import requests
import time

from pybittrex.auth import BittrexAuth

class Client(object):
    """Create a new session to the Bittrex exchange."""
    def __init__(self, api_key, api_secret):
        self.api_version = 'v1.1'
        self.api_base = 'https://bittrex.com/api/%s' % (self.api_version)

        self.api_key = api_key
        self.api_secret = api_secret

        # create a session object
        self.session = requests.Session()

    def get_api_version(self):
        return self.api_version

    def _get_nonce(self):
        """Authenticated requests all require a nonce."""
        return str(round(time.time()))

    def _build_url(self, endpoint):
        """Helper function to build the full URL."""
        return self.api_base + endpoint

    def _call(self, url, params=None):
        """Call the API """

        if not params:
            # for authenticated requests with no parameters
            params = {}

        # figure out if we need to authenticate or not
        if 'public' in url:
            auth = None
        else:
            auth = BittrexAuth(self.api_secret)
            params['apikey'] = self.api_key
            params['nonce'] = self._get_nonce()

        return self.session.get(url, params=params, auth=auth)

    # Public API
    # ----------

    def get_markets(self):
        """Used to get the open and available trading markets at Bittrex along with other metadata."""
        url = self._build_url('/public/getmarkets')

        return self._call(url)

    def get_currencies(self):
        """Used to get all supported currencies at Bittrex along with other metadata."""
        url = self._build_url('/public/getcurrencies')

        return self._call(url)

    def get_ticker(self, market, *args, **kwargs):
        """Used to get the current tick values for a market."""
        url = self._build_url('/public/getticker')

        payload = {'market': market}

        return self._call(url, params=payload)

    def get_market_summaries(self):
        """Used to get the last 24 hour summary of all active exchanges."""
        url = self._build_url('/public/getmarketsummaries')

        return self._call(url)

    def get_market_summary(self, market, *args, **kwargs):
        """Used to get the last 24 hour summary of all active exchanges."""
        url = self._build_url('/public/getmarketsummary')

        payload = {'market': market}

        return self._call(url, params=payload)

    def get_orderbook(self, market, type, *args, **kwargs):
        """Used to get retrieve the orderbook for a given market."""
        url = self._build_url('/public/getorderbook')

        payload = {'market': market, 'type': type}

        return self._call(url, params=payload)

    def get_market_history(self, market, *args, **kwargs):
        """Used to retrieve the latest trades that have occured for a specific market."""
        url = self._build_url('/public/getmarkethistory')

        payload = {'market': market}

        return self._call(url, params=payload)

    # Market API
    # ----------

    def buy_limit(self, market, qty, price, *args, **kwargs):
        """Used to place a buy order in a specific market. Use buylimit to place limit orders. Make sure you have the proper permissions set on your API keys for this call to work."""
        url = self._build_url('/market/buylimit')

        payload = {'market': market, 'quantity': qty, 'rate': price}

        return self._call(url, params=payload)

    def sell_limit(self, market, qty, price, *args, **kwargs):
        """Used to place an sell order in a specific market. Use selllimit to place limit orders. Make sure you have the proper permissions set on your API keys for this call to work."""
        url = self._build_url('/market/selllimit')

        payload = {'market': market, 'quantity': qty, 'rate': price}

        return self._call(url, params=payload)

    def market_cancel(self, uuid, *args, **kwargs):
        """Used to cancel a buy or sell order."""
        url = self._build_url('/market/cancel')

        payload = {'uuid': uuid}

        return self._call(url, params=payload)

    def get_open_orders(self, market=None, *args, **kwargs):
        """Get all orders that you currently have opened. A specific market can be requested."""
        url = self._build_url('/market/getopenorders')

        payload = {'market': market} if market else ''

        return self._call(url, params=payload)

    # Account API
    # -----------

    def get_balances(self, *args, **kwargs):
        """Used to retrieve balances from your account."""
        url = self._build_url('/account/getbalances')

        return self._call(url, params=payload)

    def get_balance(self, currency, *args, **kwargs):
        """Used to retrieve the balance from your account for a specific currency."""
        url = self._build_url('/account/getbalance')

        payload = {'currency': currency}

        return self._call(url, params=payload)

    def get_deposit_address(self, currency, *args, **kwargs):
        """Used to retrieve or generate an address for a specific currency. If one does not exist, the call will fail and return ADDRESS_GENERATING until one is available."""
        url = self._build_url('/account/getdepositaddress')

        payload = {'currency': currency}

        return self._call(url, params=payload)

    def withdraw(self, currency, qty, address, memo=None, *args, **kwargs):
        """Used to withdraw funds from your account. note: please account for txfee."""
        url = self._build_url('/account/withdraw')

        payload = {'currency': currency, 'quantity': qty, 'address': address, 'paymentid': memo}

        return self._call(url, params=payload)

    def get_order(self, uuid, *args, **kwargs):
        """Used to retrieve a single order by uuid."""
        url = self._build_url('/account/getorder')

        payload = {'uuid': uuid}

        return self._call(url, params=payload)

    def get_order_history(self, market=None, *args, **kwargs):
        """Used to retrieve your order history."""

        url = self._build_url('/account/getorderhistory')

        payload = {'market': market} if market else None

        return self._call(url, params=payload)

    def get_withdrawal_history(self, currency=None, *args, **kwargs):
        """Used to retrieve your withdrawal history."""

        url = self._build_url('/account/getwithdrawalhistory')

        paload = {'currency': currency} if currency else None

        return self._call(url, params=payload)

    def get_deposit_history(self, currency=None, *args, **kwargs):
        """Used to retrieve your deposit history."""

        url = self._build_url('/account/getdeposithistory')

        payload = {'currency': currency} if currency else None

        return self._call(url, params=payload)
