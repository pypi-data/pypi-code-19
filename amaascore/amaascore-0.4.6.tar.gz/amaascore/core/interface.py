from __future__ import absolute_import, division, print_function, unicode_literals

import boto3
from configparser import ConfigParser, NoSectionError
from datetime import datetime
import logging
from os.path import expanduser, join
from os import environ
import requests
from warrant.aws_srp import AWSSRP

from amaascore.config import COGNITO_REGION, COGNITO_CLIENT_ID, COGNITO_POOL, ENDPOINTS, LOCAL_ENDPOINT,\
    NON_PROD_URL, PROD_URL, ENVIRONMENT, API_VERSION
from amaascore.exceptions import AMaaSException


class AMaaSSession(object):

    __shared_state = {}

    def __init__(self, username, password, logger):
        if not AMaaSSession.__shared_state:
            AMaaSSession.__shared_state = self.__dict__
            self.refresh_period = 45 * 60  # minutes * seconds
            self.username = username
            self.password = password
            self.tokens = None
            self.last_authenticated = None
            self.session = requests.Session()
            self.client = boto3.client('cognito-idp', COGNITO_REGION)
            self.aws = AWSSRP(username=self.username, password=self.password, pool_id=COGNITO_POOL,
                              client_id=COGNITO_CLIENT_ID, client=self.client)
            self.logger = logger
        else:
            self.__dict__ = AMaaSSession.__shared_state
        if self.needs_refresh():
            self.login()

    def needs_refresh(self):
        if not (self.last_authenticated and
                (datetime.utcnow() - self.last_authenticated).seconds < self.refresh_period):
            return True
        else:
            return False

    def login(self):
        self.logger.info("Attempting login for: %s", self.username)
        try:
            self.tokens = self.aws.authenticate_user().get('AuthenticationResult')
            self.logger.info("Login successful")
            self.last_authenticated = datetime.utcnow()
            self.session.headers.update({'Authorization': self.tokens.get('IdToken')})
        except self.client.exceptions.NotAuthorizedException as e:
            self.logger.info("Login failed")
            self.logger.error(e.response.get('Error'))
            self.last_authenticated = None

    def put(self, url, data=None, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.put(url=url, data=data, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def post(self, url, data=None, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.post(url=url, data=data, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def delete(self, url, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.delete(url=url, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def get(self, url, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.get(url=url, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def patch(self, url, data=None, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.patch(url=url, data=data, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')


class Interface(object):
    """
    Currently this class doesn't do anything - but I anticipate it will be needed in the future.
    """

    def __init__(self, endpoint_type, endpoint=None, environment=ENVIRONMENT, username=None, password=None,
                 config_filename=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.config_filename = config_filename
        self.endpoint_type = endpoint_type
        self.environment = environment
        self.endpoint = endpoint or self.get_endpoint()
        self.json_header = {'Content-Type': 'application/json'}
        username = username or environ.get('AMAAS_USERNAME') or self.read_config('username')
        password = password or environ.get('AMAAS_PASSWORD') or self.read_config('password')
        self.session = AMaaSSession(username, password, self.logger)
        self.logger.info('Interface Created')

    def get_endpoint(self):
        if self.environment == 'local':
            return LOCAL_ENDPOINT
        url = PROD_URL % API_VERSION if self.environment == 'production' else NON_PROD_URL % self.environment
        endpoint = ENDPOINTS.get(self.endpoint_type)
        if not endpoint:
            raise KeyError('Cannot find endpoint')
        endpoint = endpoint % url
        self.logger.info("Using Endpoint: %s", endpoint)
        return endpoint

    @staticmethod
    def generate_config_filename():
        home = expanduser("~")
        return join(home, '.amaas.cfg')

    def read_config(self, option):
        if self.config_filename is None:
            self.config_filename = self.generate_config_filename()
        parser = ConfigParser()
        parser.read(self.config_filename)
        try:
            option = parser.get(section='auth', option=option)
        except NoSectionError:
            raise AMaaSException('Invalid AMaaS config file')
        return option