""" e-tip5 API operations """
import json
import requests

class Request(object):
    """ An API request """
    def __init__(self, host, port=80):
        self.url = "{}:{}".format(host, port)
    def get(self, path, params=None):
        """ gets a resource """
        return requests.get("{}{}".format(self.url, path), params=params)
    def post(self, path, payload=None):
        """ creates a resource """
        return requests.post("{}{}".format(self.url, path), data=payload)
    def ping(self):
        """ checks for a 200 status code """
        return self.get('/health').status_code == 200
    def authenticate(self, username, password):
        """ gets a new session token """
        credentials = json.dumps({'username': username, 'password': password})
        response = self.post('/v1/authentication/session', credentials)
        if response.status_code != 200:
            raise AuthError(response.text)
        return response.text

class AuthError(Exception):
    """ Authentication error """
    pass
