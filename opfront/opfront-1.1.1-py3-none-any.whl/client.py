from opfront.exceptions import BadRequestError, ConflictError, ForbiddenError, IntegrityError, ResourceNotFoundError, UnauthorizedError, UnexpectedError

import requests


class OpfrontClient(object):

    """
    OpfrontClient manages the login credentials as well as the token refresh flow

    Args:
        email (str): Email address with which to login
        password (str): Password associated with the email
    """

    def __init__(self, email, password, api_url='https://api.opfront.ca'):

        self._token = None
        self._refresh = None
        self._api_url = api_url

        data = self.do_request('/auth/login', 'POST', body={'email': email, 'password': password})

        self._token = data['auth_token']
        self._refresh = data['refresh_token']

    @property
    def _headers(self):
        headers = {}
        if self._token:
            headers['X-Auth-Token'] = self._token

        return headers

    @classmethod
    def _validate_status_code(cls, resp):
        if resp.status_code == 404:
            raise ResourceNotFoundError()

        elif resp.status_code == 400:
            raise BadRequestError()

        elif resp.status_code == 422:
            raise IntegrityError()

        elif resp.status_code == 403:
            raise ForbiddenError()

        elif resp.status_code == 409:
            raise ConflictError()

        elif resp.status_code == 500:
            raise UnexpectedError()

    def _try_refresh(self):
        if self._token is None or self._refresh is None:
            raise UnauthorizedError

        self._token = None
        data = self.do_request('/auth/refresh', 'POST', body={'refresh_token': self._refresh})
        self._token = data['auth_token']

    def do_request(self, url, method, body=None):
        """
        Perform a request to the Opfront API

        Args:
            url: Endpoint to query
            method: HTTP method
            body: Request payload

        Returns:
            dict: Response body

        """
        resp = None
        request_url = self._api_url + url

        if method == 'GET':
            resp = requests.get(request_url, headers=self._headers)

        elif method == 'POST':
            resp = requests.post(request_url, json=body, headers={**self._headers, 'Content-Type': 'application/json'})

        elif method == 'PATCH':
            resp = requests.patch(request_url, json=body, headers={**self._headers, 'Content-Type': 'application/json'})

        elif method == 'DELETE':
            resp = requests.delete(request_url, headers=self._headers)

        if resp is None:
            raise ValueError('Invalid HTTP method: {}'.format(method))

        OpfrontClient._validate_status_code(resp)

        if resp.status_code == 401 or resp.status_code == 403:
            self._try_refresh()
            self.do_request(url, method, body)

        if resp.status_code == 204:
            return None

        return resp.json()['data']
