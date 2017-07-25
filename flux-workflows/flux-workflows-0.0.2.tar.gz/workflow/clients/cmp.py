import requests
import json

requests.packages.urllib3.disable_warnings()


class Client(object):
    def __init__(self, url, auth=None, access_token=None, verify_ssl=True):
        self._session = requests.Session()
        self._url = url
        self._auth = auth
        self._verify = verify_ssl
        self._access_token = access_token
        self._session.headers = {
            'User-Agent': 'nflex-client',
            'Content-Type': 'application/json',
        }
        if auth and len(auth) == 2 and auth[0] and auth[1]:
            self._session.auth = auth

        elif access_token:
            self._session.headers['Cookie'] = access_token

    @property
    def api_url(self):
        return self._url

    @property
    def api_auth(self):
        return self._auth

    @property
    def api_token(self):
        return self._access_token

    @api_token.setter
    def api_token(self, value):
        self._access_token = value
        self._session.headers['Cookie'] = value

    @property
    def headers(self):
        return self._session.headers

    @headers.setter
    def headers(self, value):
        self._session.headers.update(value)

    def url(self, path):
        """Construct an endpoint path using the CMP base URL.

        Args:
            path (str): The path to use

        Returns:
            str: The full CMP API endpoint path
        """
        return self._url + path

    def get(self, path, params=None):
        """Execute a GET request.

        Args:
            path (str): The CMP API endpoint path
            params (dict): Dict with the GET request parameters

        Returns:
            requests.Response: The response of the request
        """
        return self._session.get(self.url(path), params=params, verify=self._verify)

    def post(self, path, data):
        """Execute a POST request.

        Args:
            path (str): The CMP API endpoint path
            data (dict): Dict with the POST request payload

        Returns:
            requests.Response: The response of the request
        """
        return self._session.post(self.url(path), json=data, verify=self._verify)

    def post_file(self, path, file, file_name):
        """Execute a POST request to upload a file.

        Since the request library must automatically determine the Content-Type
        header when uploading a file, we have to pop it from the session
        headers and put it back in after the request has finished

        Args:
            path (str): The CMP API endpoint path
            file (file): A file to upload
            file_name (str): The name of the zip file to upload

        Returns:
            requests.Response: The response of the request
        """
        files = {
            'file': (file_name, file)
        }
        cth = self._session.headers.pop("Content-Type", None)
        try:
            result = self._session.post(self.url(path), files=files, verify=self._verify)
        finally:
            self._session.headers["Content-Type"] = cth

        return result

    def put(self, path, data):
        """Execute a PUT request.

        Args:
            path (str): The CMP API endpoint path
            data (dict): Dict with the PUT request payload

        Returns:
            requests.Response: The response of the request
        """
        return self._session.put(url=self.url(path), data=json.dumps(data), verify=self._verify)

    def put_file(self, path, data):
        """Execute a PUT request to upload a file.

        Args:
            path (str): The CMP API endpoint path
            data: The data to upload

        Returns:
            requests.Response: The response of the request
        """
        cth = self._session.headers.pop("Content-Type", None)
        try:
            result = self._session.put(url=self.url(path), data=data, verify=self._verify)
        finally:
            self._session.headers["Content-Type"] = cth

        return result

    def delete(self, path, params=None):
        """Execute a DELETE request.

        Args:
            path (str): The CMP API endpoint path
            params (dict): Dict with the DELETE request parameters

        Returns:
            requests.Response: The response of the request
        """
        return self._session.delete(self.url(path), params=params, verify=self._verify)

    def patch(self, path, data):
        """Execute a PATCH request.

        Args:
            path (str): The CMP API endpoint path
            data (dict): Dict with the PUT request payload

        Returns:
            requests.Response: The response of the request
        """
        return self._session.patch(self.url(path), data=json.dumps(data), verify=self._verify)
