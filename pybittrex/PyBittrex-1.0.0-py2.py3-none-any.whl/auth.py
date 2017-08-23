import hmac
import hashlib

from requests.auth import AuthBase

class BittrexAuth(AuthBase):
    """Sign requests to Market and Account API. Don't call this class directly."""
    def __init__(self, api_secret):
        self.api_secret = api_secret

    def __call__(self, request):
        uri = request.url
        signature = hmac.HMAC(
            key=bytes(self.api_secret, 'utf-8'),
            msg=bytes(uri, 'utf-8'),
            digestmod=hashlib.sha512
        ).hexdigest()

        request.headers['apisign'] = signature

        return request
