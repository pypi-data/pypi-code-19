# Copyright (c) 2017 XLAB d.o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module with http and wrapper clients for FCO.
"""

import requests

from fcoclient import exceptions

from fcoclient.resources.disk import DiskClient
from fcoclient.resources.firewalltemplate import FirewallTemplateClient
from fcoclient.resources.image import ImageClient
from fcoclient.resources.job import JobClient
from fcoclient.resources.nic import NicClient
from fcoclient.resources.network import NetworkClient
from fcoclient.resources.productoffer import ProductOfferClient
from fcoclient.resources.server import ServerClient
from fcoclient.resources.sshkey import SshKeyClient
from fcoclient.resources.vdc import VdcClient


class APIClient(object):
    """
    Internal FCO client that should be used to communicate with FCO server.

    This client's task is to hold user credentials and provide some helper
    methods that make calling REST API a bit more user friendly.

    Note that this client should not be used directly, use Client in this
    package that provides higher level abstraction over available
    functionality.
    """

    def __init__(self, username, customer, password, url, verify):
        """
        Initialize http client.

        Args:
            username (str): FCO username.
            customer (str): FCO customer.
            password (str): FCO password.
            url (str): FCO REST API base address.
            verify: Parameter for SSL certificate validation. Use ``False`` to
                disable validation, ``True`` to validate certificates against
                system trusted certificates or path to certificate file to
                validate against custom server certificate (even self-signed).
        """
        self.auth = ("{}/{}".format(username, customer), password)
        url = url if url[-1] == "/" else (url + "/")
        self.url = url + "rest/user/5.0/"
        self.verify = verify

    def _query(self, method, endpoint, data, status_code):
        url = self.url + endpoint
        response = method(url, auth=self.auth, json=data, verify=self.verify,
                          headers={"Content-Type": "application/json"})
        if response.status_code != status_code:
            raise exceptions.APICallError(response)
        return response.json()

    def get(self, endpoint, status_code):
        """
        Send GET request to FCO API.

        Args:
            endpoint (str): Relative resource path.
            status_code (int): Expected status code

        Returns:
            Dictionary representing returned json document.

        Raises:
            APICallError: If ``status_code`` does not match response's status.
        """
        return self._query(requests.get, endpoint, None, status_code)

    def post(self, endpoint, data, status_code):
        """
        Send POST request to FCO API.

        Args:
            endpoint (str): Relative resource path.
            status_code (int): Expected status code

        Returns:
            Dictionary representing returned json document.

        Raises:
            APICallError: If ``status_code`` does not match response's status.
        """
        return self._query(requests.post, endpoint, data, status_code)

    def put(self, endpoint, data, status_code):
        """
        Send PUT request to FCO API.

        Args:
            endpoint (str): Relative resource path.
            status_code (int): Expected status code

        Returns:
            Dictionary representing returned json document.

        Raises:
            APICallError: If ``status_code`` does not match response's status.
        """
        return self._query(requests.put, endpoint, data, status_code)

    def delete(self, endpoint, data, status_code):
        """
        Send DELETE request to FCO API.

        Args:
            endpoint (str): Relative resource path.
            status_code (int): Expected status code

        Returns:
            Dictionary representing returned json document.

        Raises:
            APICallError: If ``status_code`` does not match response's status.
        """
        return self._query(requests.delete, endpoint, data, status_code)


class Client(object):
    """
    Main interface to the FCO REST API.
    """

    def __init__(self, username, customer, password, url, verify=True):
        """
        Construct main FCO client.

        Args:
            username (str): FCO username.
            customer (str): FCO customer.
            password (str): FCO password.
            url (str): FCO REST API base address.
            verify: Parameter for SSL certificate validation. Use ``False`` to
                disable validation, ``True`` to validate certificates against
                system trusted certificates or path to certificate file to
                validate against custom server certificate (even self-signed).
        """
        client = APIClient(username, customer, password, url, verify)

        self.disk = DiskClient(client)
        self.firewalltemplate = FirewallTemplateClient(client)
        self.image = ImageClient(client)
        self.job = JobClient(client)
        self.nic = NicClient(client)
        self.network = NetworkClient(client)
        self.productoffer = ProductOfferClient(client)
        self.server = ServerClient(client)
        self.sshkey = SshKeyClient(client)
        self.vdc = VdcClient(client)
