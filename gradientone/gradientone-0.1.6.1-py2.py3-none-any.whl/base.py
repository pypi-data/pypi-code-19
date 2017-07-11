"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import datetime
import gzip
import json
import os
import requests
import ssl
import sys
import time
from configparser import ConfigParser
from requests_toolbelt.multipart.encoder import MultipartEncoder

import gateway_helpers as helpers
import schema_forms

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

# Read in config file info
cfg = ConfigParser()
PATH_TO_CFG_FILE = '/etc/gradient_one.cfg'
cfg.read(PATH_TO_CFG_FILE)
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']

# Get Sentry client for Sentry logging
SENTRY_CLIENT = helpers.get_sentry()

# For Non-Sentry logging
logger = helpers.logger

# Set globals
INSTRUMENTS = helpers.get_usbtmc_devices()+helpers.get_copley_devices()  # noqa
SECONDS_BTW_HEALTH_UPDATES = 180
CLIENT_ID = 'ORIGINAL'
SAMPLE_FILE = 'MDO30121M.txt'
CMD_URL = helpers.BASE_URL + '/commands'
logger = helpers.logger
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DIRPATH = os.path.dirname(os.path.realpath(__file__))
if COMMON_SETTINGS['DOMAIN'].find("localhost") == 0 or COMMON_SETTINGS['DOMAIN'].find("127.0.0.1") == 0:  # noqa
    BASE_URL = "http://"+COMMON_SETTINGS['DOMAIN']
else:
    BASE_URL = "https://" + COMMON_SETTINGS['DOMAIN']
COMMAND_URL = BASE_URL + '/commands'
DEFAULT_TEK_TYPE = 'TektronixMDO3012'


def binary_type(input):
    if int(sys.version[0]) < 3:
        return input
    else:
        return bytes(input, "utf-8")


class BaseClient(object):
    """Base client for methods common to all instruments"""
    def __init__(self, client_info=None, tags=[]):
        self.session = requests.session()
        self.session.headers.update(helpers.get_headers())
        self.client_info = client_info
        self.tags = []  # to filter commands

    def check_for_commands(self, client_info=None):
        """starts the loop that checks for commands"""
        if not client_info:
            client_info = self.client_info
        while True:
            try:
                self.check_command_url()
            except Exception:
                logger.warning("check_for_commands exception", exc_info=True)
                SENTRY_CLIENT.captureException()
            time.sleep(1)
            self.update_activity_file(client_info.activity_file)

    def update_activity_file(self, activity_file):
        """Updates counter for nanny to check"""
        with open(activity_file, 'w') as f:
            f.write(datetime.datetime.now().strftime(DATETIME_FORMAT))

    def check_command_url(self, tags=[]):
        """polls the configuration URL for a test run object"""
        command_url = COMMAND_URL
        headers = helpers.get_headers()
        if not tags:
            tags = self.tags
        params = {'status': 'pending', 'tags': self.tags}
        response = self.session.get(command_url, headers=headers,
                                    params=params)
        if response.status_code == 401:
            headers = helpers.get_headers(refresh=True)
            response = self.session.get(command_url, headers=headers)
        if response:
            logger.debug("Processing response: "+str(response.text) +
                         " command_url "+str(command_url))
            self.process_response(response)
        else:
            logger.error("No response from server")

    def http_request(self, url, data=None, params=None, headers=None,
                     kind='get', retry=True):
        """Makes http requests to app engine

        retry - if True means 'yes, retry' for SSLErrors it will
            start a new session and recursively call http_request

        """
        logger.info("making %s request to url: %s" % (kind, url))
        self.session.headers = helpers.get_headers()
        if headers:
            self.session.headers.update(headers)
        reqs = {
            'get': self.session.get,
            'post': self.session.post,
            'put': self.session.put,
            'del': self.session.delete,
        }
        response = None
        try:
            if data:
                response = reqs[kind](url, data=data)
            else:
                response = reqs[kind](url, params=params)
            if response.status_code in [401, 403]:
                hdrs = helpers.get_headers(refresh=True)
                self.session.headers.update(hdrs)  # for refresh
                if headers:
                    self.session.headers.update(headers)  # method arg
                if data:
                    response = reqs[kind](url, data=data)
                else:
                    response = reqs[kind](url, params=params)
            if response.status_code != 200:
                logger.warning("response.text %s" % response.text)
                logger.warning("request headers %s" % self.session.headers)
                logger.warning("request data %s" % data)
        except ssl.SSLError:
            logger.warning("SSLError!", exc_info=True)
            if retry:
                self.session = requests.session()
                response = self.http_request(url, data, params, headers, kind,
                                             retry=False)
            else:
                # if a retry was already attempted, don't retry forever
                logger.warning("Not retrying. Returning None")
        except Exception as e:
            logger.warning("request exc: %s" % e, exc_info=True)
        finally:
            self.session.headers = helpers.get_headers()  # reset the headers
            return response

    def post(self, url, data=None, headers=None):
        return self.http_request(url, data=data, headers=headers, kind='post')

    def put(self, url, data=None, headers=None):
        return self.http_request(url, data=data, headers=headers, kind='put')

    def get(self, url, params=None, headers=None):
        return self.http_request(url, params=params, headers=headers, kind='get')  # noqa

    def delete(self, url, params=None, headers=None):
        return self.http_request(url, params=params, headers=headers, kind='del')  # noqa

    def process_response(self, response):
        """method should be overridden for each instrument"""
        logger.info(response)

    def update_command(self, command_id, status):
        data = json.dumps({'command_id': command_id, 'status': status})
        try:
            response = self.put(COMMAND_URL, data=data)
            assert response.status_code == 200
        except Exception as e:
            logger.error("update_command() exc: %s" % e)

    def post_config_form(self, instruments=None):
        if not instruments:
            instruments = INSTRUMENTS
        # upload all config forms for available instruments
        for instrument in instruments:
            inst_name = instrument["product"]
            if inst_name in dir(schema_forms):
                FORM_DICT = getattr(schema_forms, inst_name).FORM_DICT
                SCHEMA_DICT = getattr(schema_forms, inst_name).SCHEMA_DICT
            else:
                FORM_DICT = "unavailable for instrument: "+inst_name
                SCHEMA_DICT = {}
            if "fancy_name" in instrument.keys():
                inst_fancy_name = instrument["fancy_name"]
            else:
                inst_fancy_name = inst_name
            _data = {"schema": SCHEMA_DICT, "form": FORM_DICT, "defaults": [],
                     "instrument_type": inst_fancy_name}
            schema_url = urljoin(BASE_URL, "schemaform")
            response = self.post(schema_url, data=json.dumps(_data))
            assert response.status_code == 200

    def gzip_and_post_file(self, file, file_key='', command_id='',
                           category=''):
        gzip_file = file + '.gz'
        if not file_key:
            file_key = gzip_file.split('/')[-1]
        with open(file) as f_in, gzip.open(gzip_file, 'wb') as f_out:
            f_out.write(binary_type(f_in.read()))
        data_type = 'application/x-gzip'
        multipartblob = MultipartEncoder(
            fields={
                'file': (file_key, open(gzip_file, 'rb'), data_type),
                'test_run_id': command_id,  # migrate towards just command_id
                'command_id': command_id,
                'file_key': file_key,
                'category': category,
            }
        )
        try:
            blob_url = self.get(BASE_URL + "/upload/geturl")
            headers = {'Content-Type': multipartblob.content_type}
            response = self.post(blob_url.text, data=multipartblob,
                                 headers=headers)
            assert response.status_code == 200
            logger.info("Uploaded file with file_key %s" % file_key)
            return response
        except Exception as e:
            logger.error("gzip_and_post_file() err %s" % e)

    def post_logfile(self, test_run_id=""):
        logfile = logger.handlers[-1].baseFilename
        if not os.path.isfile(logfile):
            logger.warning("Missing logfile!")
            return
        self.gzip_and_post_file(logfile, command_id=test_run_id,
                                category='logfile')

    def update_gateway_state(self, state):
        """post a feedback update from instrument gateway"""
        url = BASE_URL + '/gateway'
        payload = {
            'state': state,
            'company': COMMON_SETTINGS['COMPANYNAME'],
            'name': COMMON_SETTINGS['HARDWARENAME'],
        }
        self.put(url, data=json.dumps(payload))
