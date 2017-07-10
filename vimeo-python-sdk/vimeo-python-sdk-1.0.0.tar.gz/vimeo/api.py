import requests
from base64 import b64encode
from urllib.parse import urlencode
from .exceptions import VimeoException


class API:
    _client_id = None
    _client_secret = None
    _access_token = None
    _api_base_url = 'https://api.vimeo.com/'
    _authorization_url = 'https://api.vimeo.com/oauth/authorize'
    _access_token_url = 'https://api.vimeo.com/oauth/access_token'

    def __init__(self, client_id, client_secret, access_token=None):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token

    def get_authorization_url(self, callback, **kwargs):
        return self._authorization_url + '?' + urlencode({**{
            'client_id': self._client_id,
            'redirect_uri': callback,
            'response_type': 'code'
        }, **kwargs})

    def get_access_token(self, code, callback):
        response = requests.post(self._access_token_url, data={
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': callback,
            'code': code
        })

        if response.status_code != 200:
            raise VimeoException(response.status_code, response.json())

        token = response.json()
        self.set_access_token(token['access_token'])
        return token

    def set_access_token(self, access_token):
        self._access_token = access_token

    def get(self, endpoint, **kwargs):
        return self.request('get', endpoint, params=kwargs)

    def post(self, endpoint, **kwargs):
        return self.request('post', endpoint, data=kwargs)

    def request(self, method, endpoint, **kwargs):
        url = self._api_base_url + endpoint if 'url' not in kwargs else kwargs['url']

        if self._access_token:
            authorization = 'bearer ' + self._access_token
        else:
            authorization = 'basic ' + b64encode((self._client_id + ':' + self._client_secret).encode('ascii')).decode()

        response = getattr(requests, method)(url, headers={'Authorization': authorization}, **kwargs)

        if response.status_code < 200 or response.status_code > 299:
            raise VimeoException(response.status_code, response.json())

        return response.json()
