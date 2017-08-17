import requests
import sys

import russell
from russell.manager.auth_config import AuthConfigManager
from russell.exceptions import AuthenticationException, BadRequestException, NotFoundException, OverLimitException, InvalidResponseException, NoRequestException
from russell.log import logger as russell_logger
import json


class RussellHttpClient(object):
    """
    Base client for all HTTP operations
    """
    def __init__(self):
        self.base_url = "{}/api/v1".format(russell.russell_host)
        self.access_token = AuthConfigManager.get_access_token()

    def request(self,
                method,
                url,
                params=None,
                data=None,
                files=None,
                timeout=5,
                access_token=None):
        """
        Execute the request using requests library
        """
        request_url = self.base_url + url
        russell_logger.debug("Starting request to url: {} with params: {}, data: {}".format(request_url, params, data))
        if access_token:
            headers = {"Authorization": "Basic {}".format(access_token)}
        else:
            headers = {"Authorization": "Basic {}".format(
                self.access_token.token if self.access_token else None)
            }

        try:
            # print "url: {}".format(request_url)
            # print "params: {}".format(params)
            # print "data: {}".format(data)
            response = requests.request(method,
                                        request_url,
                                        params=params,
                                        headers=headers,
                                        data=data,
                                        files=files,
                                        timeout=timeout)
        except requests.exceptions.ConnectionError:
            sys.exit("Cannot connect to the Russell server. Check your internet connection.")

        try:
            russell_logger.debug("Response Content: {}, Headers: {}".format(response.json(), response.headers))
        except Exception:
            russell_logger.debug("Request failed. Response: {}".format(response.content))

        self.check_response_status(response)
        # print "response: {}".format(json.dumps(response.json()))
        return response.json()["data"]

    def check_response_status(self, response):
        """
        Check if response is successful. Else raise Exception.
        """
        if not (200 <= response.status_code  < 300 and response.json().get("code") != None):
            if response.status_code == 401:
                raise AuthenticationException()
            else:
                raise InvalidResponseException()

        code = response.json()["code"]
        if not (200 <= code < 300):
            try:
                message = response.json()["data"]
            except Exception:
                message = None
            russell_logger.debug("Error received : status_code: {}, message: {}".format(code,
                                                                                      message or response.content))
            if code == 517:
                raise NotFoundException()
            elif code == 512:
                raise AuthenticationException()
            elif code == 519:
                raise BadRequestException()
            elif code == 518:
                raise NoRequestException()
            elif code == 520:
                raise OverLimitException()
            else:
                response.raise_for_status()
