"""
wrapper for civis-webapp aws project
"""

import requests
import json
import os


#TODO: need to have exception classes and raise errors for all methods


class API(object):
    """
    Provides the 'get', 'post', 'put', and 'delete' methods
    """

    def __init__(self, base_url="https://m39jjvch8d.execute-api.us-east-1.amazonaws.com/api"):
        """
        Constructor
        :param base_url: execution endpoint for api gateway
        """
        self.base_url = self._trailing_slash(base_url)
        self.header = {}
        self.session = requests.Session()

    @staticmethod
    def _trailing_slash(url):
        out = url if url.endswith("/") else url+"/"
        return out

    def _form_url(self, endpoint):
        url = "{}{}".format(self.base_url, endpoint)
        return url

    def get(self, endpoint, params=None):
        """
        Issues a 'get' command to the API server.
        :param endpoint: path to append to the base_url, for example "hello/name"
        :param params: optional url parameters, specify as a dictionary
        :return: the de-serialized payload resulting from the GET response,
        the json text is loaded into python data types (dict, lists, etc.)
        """
        rc = self.session.get(self._form_url(endpoint),
        headers=self.header,
        params=params)
        return rc.json()

    def post(self, endpoint, payload):
        """
        Issues a 'post' command to the API server.
        :param endpoint: path to append to the base_url
        :param payload: a dictionary that will be converted to a json payload
        :return: The deserialized response from the server
        """
        payload_json = json.dumps(payload)
        rc = self.session.post(self._form_url(endpoint), data=payload_json, headers=self.header)
        return rc.json()

    def put(self, endpoint, payload):
        """
        Issues a 'put' command to the API server.
        :param endpoint: path to append to the base_url
        :param payload: a dictionary that will be converted to a json payload
        :return: There is no return, will raise an error if there's a problem
        """
        payload_json = json.dumps(payload)
        rc = self.session.put(self._form_url(endpoint), data=payload_json, headers=self.header)
        return

    def delete(self, endpoint):
        """
        Issues a 'delete' command to the API server.
        :param endpoint: path to append to the base_url
        :return: There is no return, will raise an error if there's a problem
        """
        rc = self.session.delete(self._form_url(endpoint), headers=self.header)
        return
