""" e-tip5 API operations """
import datetime
import json
import copy
import logging
import requests
import jwt
import coloredlogs

# setup logging
LOG = logging.getLogger('EtipsApi')
coloredlogs.install(
    fmt='[%(asctime)s.%(msecs)03d] %(levelname)s %(message)s'
)

class Request(object):
    """ An API request """
    def __init__(self, host, port=80):
        self.url = "{}:{}".format(host, port)
        self.jwt_string = None
        self.jwt = None
        self.status_code = None
    def headers(self, items_from=0, items_to='*'):
        """ get request headers """
        headers = {
            'Content-Type': 'application/json',
            'range': 'items={}-{}'.format(items_from, items_to)
        }
        if self.is_authenticated():
            headers['Authorization'] = 'Bearer {}'.format(self.jwt_string)
        return headers
    def get(self, path, params=None, items_from=0, items_to='*'):
        """ gets a resource """
        LOG.info(
            'GET %s%s?%s',
            self.url,
            path,
            '' if params is None else params
        )
        response = requests.get(
            "{}{}".format(self.url, path),
            headers=self.headers(items_from, items_to),
            params=params
        )
        self.status_code = response.status_code
        LOG.info('HTTP %s', self.status_code)
        return json.loads(response.text)
    def post(self, path, params=None, payload=None):
        """ creates a resource """
        LOG.info(
            'POST %s%s?%s %s',
            self.url,
            path,
            '' if params is None else params,
            json.dumps(obfuscate_payload(payload))
        )
        response = requests.post(
            "{}{}".format(self.url, path),
            headers=self.headers(),
            params=params,
            data=json.dumps(payload)
        )
        self.status_code = response.status_code
        LOG.info('HTTP %s', self.status_code)
        if response.text:
            return json.loads(response.text)
    def ping(self):
        """ checks for a 200 status code """
        self.get('/health')
        return self.status_code == 200
    def authenticate(self, username, password):
        """ gets a new session token """
        response = self.post(
            '/v1/authentication/session',
            payload={'username': username, 'password': password}
        )
        if self.status_code != 200:
            if response is not None:
                raise AuthError(response)
            else:
                raise Exception('Authentication failed (HTTP {})'.format(self.status_code))
        self.jwt_string = response['token']
        self.jwt = jwt.decode(self.jwt_string, verify=False)
        return True
    def is_authenticated(self):
        """ are we already authenticated? """
        return self.jwt is not None

def convert_time_str_to_datetime(string_date):
    """ convert a date string to a datetime """
    return datetime.datetime.strptime(string_date, "%Y-%m-%dT%H:%M:%SZ")

def convert_date_str_to_datetime(string_date):
    """ convert a date string to a datetime """
    return datetime.datetime.strptime(string_date, "%Y-%m-%d")

def obfuscate_payload(payload):
    """ obfuscates passwords and the like """
    keys = ['password']
    obfuscated = copy.deepcopy(payload)
    for key in keys:
        if key in payload:
            obfuscated[key] = '[redacted]'
    return obfuscated

class AuthError(Exception):
    """ Authentication error """
    pass
