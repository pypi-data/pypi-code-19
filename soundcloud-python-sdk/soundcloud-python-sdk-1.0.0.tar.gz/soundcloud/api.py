import requests
from json import JSONDecodeError
from urllib.parse import urlencode
from .exceptions import SoundCloudException


class API:
    _client_id = None
    _client_secret = None
    _access_token = None
    _api_base_url = 'https://api.soundcloud.com/'
    _authorization_url = 'https://api.soundcloud.com/connect'
    _access_token_url = 'https://api.soundcloud.com/oauth2/token'

    def __init__(self, client_id, client_secret, access_token=None):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token

    def get_authorization_url(self, callback, **kwargs):
        return self._authorization_url + '?' + urlencode({**{
            'client_id': self._client_id,
            'response_type': 'code',
            'redirect_uri': callback,
            'state': '9sdfhkj34897skdfh38497sksdf34dfdhfj',
            'scope': 'non-expiring',
            'display': 'popup'
        }, **kwargs})

    def get_access_token(self, code, callback):
        response = requests.post(self._access_token_url, data={
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': callback
        })

        if response.status_code != 200:
            raise SoundCloudException(response.status_code, response.json())

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
        authentication = {
            'client_id': self._client_id,
            'oauth_token': self._access_token
        }

        if 'params' in kwargs:
            kwargs['params'] = {**kwargs['params'], **authentication}

        if 'data' in kwargs:
            kwargs['data'] = {**kwargs['data'], **authentication}

        url = self._api_base_url + endpoint
        response = getattr(requests, method)(url, **kwargs)

        if response.status_code < 200 or response.status_code > 299:
            try:
                raise SoundCloudException(response.status_code, response.json())
            except JSONDecodeError:
                raise SoundCloudException(response.status_code, {'errors': [{'error_message': 'Unknown error'}]})

        return response.json()
