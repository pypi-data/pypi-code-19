import base64

from braintreehttp import Environment


class PayPalEnvironment(Environment):

    LIVE = "https://api.paypal.com"
    SANDBOX = "https://api.sandbox.paypal.com"

    def __init__(self, client_id, client_secret, mode):
        self.client_id = client_id
        self.client_secret = client_secret
        self._base_url = mode

    def base_url(self):
        return self._base_url

    def authorization_string(self):
        return "Basic {0}".format(base64.b64encode((self.client_id + ":" + self.client_secret).encode()).decode())

