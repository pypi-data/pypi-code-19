"""Provides abstraction classes and methods to access NCC's PA API."""

#    Copyright 2017 NCC Group plc
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from base64 import b64encode
from contextlib import contextmanager
import json
import logging
import time
from urllib.parse import urlencode, urlparse, urlunparse
import certifi
import urllib3


class ApiQueryError(Exception):
    """
    An error occured when querying the API.
    """
    def __init__(self, message, status):
        super().__init__("({0}) {1}".format(status, message))

class AuthenticationError(Exception):
    """
    Error while authenticating with the API.
    """
    pass

class PaAuth:
    """
    Authenticate with PA's Oauth.
    """
    BASE_URL = 'https://api.nccgroup-webperf.com'
    http = None
    username = None
    password = None
    basic_auth = None

    _auth_token = None
    _token_expiry = None

    def __init__(self, username, password, client_username=None,
                 client_password=None, poolmanager=None):
        self.username = username
        self.password = password
        credentials = '{}:{}'.format(client_username, client_password)
        self.basic_auth = b64encode(credentials.encode()).decode()
        if poolmanager is not None:
            self.http = poolmanager
        else:
            self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    @contextmanager
    def authenticate(self):
        """
        Authenticates with the PA Oauth system
        """
        if self._auth_token is None or self._token_expiry < time.time():
            self._perform_auth()

        yield self._auth_token

    def _perform_auth(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if self.basic_auth is not None:
            headers['Authorization'] = 'Basic %s' % (self.basic_auth,)

        logging.info('Authenticating with PA API')

        response = self.http.request_encode_body(
            'POST',
            '%s/authorisation/token' % (self.BASE_URL,),
            fields=urlencode({
                'username': self.username,
                'password': self.password,
                'grant_type': 'password'
            }),
            headers=headers
        )

        if response.status >= 400 and response.status < 500:
            logging.warning("Failed to authenticate with API")
            raise AuthenticationError("Couldn't authenticate to PA API")
        elif response.status >= 500:
            logging.critical("PA API returned a service error")
            raise AuthenticationError("Error communicating with API server")
        else:
            logging.info("Authentication successful %d", response.status)

        data = json.loads(response.data.decode())
        self._auth_token = data['access_token']
        self._token_expiry = (time.time() - 30 + data['expires_in'])

class PaApi:
    """
    Abstraction to access the PA API
    """
    API_URL = 'https://api.nccgroup-webperf.com/pa/1'
    PAGE_SIZE = 1000
    auth_realm = None
    auth = None
    http = None
    def __init__(self, auth, realm, poolmanager=None):
        self.auth_realm = realm
        self.auth = auth
        if poolmanager is not None:
            self.http = poolmanager
        else:
            self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    def _query_api(self, method, url, fields=None, extra_headers=None, req_body=None):
        """
        Abstracts http queries to the API
        """
        with self.auth.authenticate() as token:
            logging.debug('PA Authentication returned token %s', token)
            headers = {
                'Authorization': 'Bearer %s' % (token,),
                'Realm': self.auth_realm
            }
            if extra_headers is not None:
                headers.update(extra_headers)

            logging.info('[%s] %s', method, url)
            if req_body is not None:
                response = self.http.request(method, url, fields, headers, body=req_body)
            else:
                response = self.http.request(method, url, fields, headers)                
            if response.status != 200:
                print(response.data)
                logging.warning('Got non-200 HTTP status from API: %d', response.status)
                raise ApiQueryError("Failed to get API data", response.status)
            return json.loads(response.data.decode())
    def _build_url(self, endpoint, params=None):
        if params is None:
            params = {}
        urlinfo = list(urlparse(self.API_URL))
        urlinfo[2] = '%s/%s' % (urlinfo[2], endpoint)
        urlinfo[4] = urlencode(params)
        return urlunparse(urlinfo)
    def get_all_jobtemplates(self):
        """
        Retrieves the list of jobTemplates for the current realm.
        """
        endpoint = self._build_url('jobTemplates', {
            'paginationPageSize': self.PAGE_SIZE
        })
        data = self._query_api('GET', endpoint)
        return data['results']
    def get_testruns_for_jobtemplate(self, jobtemplate_uri, start_date=None):
        """
        Retrieves a bunch of test runs for a specific job template.
        """
        params = {
            'jobTemplate': jobtemplate_uri,
            'paginationPageSize': self.PAGE_SIZE
        }
        if start_date is not None:
            params['fromDate'] = start_date
        data = self._query_api('GET', self._build_url('testRuns', params))
        return data['results']
    def get_pageobjects_for_testrun(self, testrun_uri):
        """
        Retrieves pageobject data for a particular testrun.
        """
        endpoint = self._build_url('objects', {
            'testRun': testrun_uri,
            'paginationPageSize': self.PAGE_SIZE
        })
        data = self._query_api('GET', endpoint)
        return data['results']
    def create_job_template(self, template):
        """
        Creates a job template
        """
        endpoint = self._build_url('jobTemplates')
        data = self._query_api('POST',
                               endpoint,
                               None,
                               {'Content-Type': 'application/json'},
                               json.dumps(template))
        return data['results']
    def create_job(self, job_template_uri):
        """
        Creates a job
        """
        endpoint = self._build_url('jobs')
        data = self._query_api('POST',
                               endpoint,
                               None,
                               {'Content-Type': 'application/json'},
                               json.dumps({'jobTemplateUri': job_template_uri}))
        return data['results']
