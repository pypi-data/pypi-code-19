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
Module with network interface related functionality.
"""

from requests import codes

from fcoclient.resources.base import BaseClient, Resource, ResourceType
from fcoclient.resources.job import Job


class Nic(Resource):
    """
    Class representing network interface.
    """

    resource_type = ResourceType.nic

    @staticmethod
    def skeleton():
        return Nic("{NETWORK UUID}", "{NIC NAME}")

    def __init__(self, networkUUID, resourceName, **rest):
        """
        Create new network interface.

        Description of all available fields can be found at _nic docs.

        .. _nic: http://docs.flexiant.com/display/DOCS/REST+Nic

        Args:
            networkUUID: UUID of the network this interface is attached to
            resourceName: Name of the network interface
        """
        super(Nic, self).__init__({
            "networkUUID": networkUUID,
            "resourceName": resourceName,
        }, **rest)


class NicClient(BaseClient):
    """
    Client providing access to network interfaces.
    """

    klass = Nic

    def create(self, skeleton):
        """
        Create new network interface.

        Nic creation is asynchronous operation and needs to be tracked
        using job object that is returned.

        Args:
            skeleton (:obj:`Nic`): Network interface skeleton.

        Returns:
           :obj:`Job`: New job, describing creation progress.
        """
        data = dict(skeletonNIC=skeleton)
        return Job(self.client.post(self.endpoint, data, codes.accepted))
