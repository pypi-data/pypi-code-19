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
Module with disk related functionality.
"""

from requests import codes

from fcoclient.resources.base import BaseClient, Resource, ResourceType
from fcoclient.resources.job import Job


class Disk(Resource):
    """
    Class representing disk resource."
    """

    resource_type = ResourceType.disk

    @staticmethod
    def skeleton():
        """
        Create disk skeleton.
        """
        return Disk("{DISK PRODUCT OFFER UUID}", "{DISK NAME}",
                    "{SIZE (int, in GB)}", "{VDC UUID}")

    def __init__(self, productOfferUUID, resourceName, size, vdcUUID, **rest):
        """
        Create new disk resource.

        Detailed description of available fields can be found at Disk_ docs.

        .. _DISK: http://docs.flexiant.com/display/DOCS/REST+Disk

        Args:
            productOfferUUID: UUID of the offer
            resourceName: Name of new disk
            size (int): Disk size (in GB)
            vdcUUID: UUID of the VDC where disk will reside
            **rest: Additional skeleton fields
        """
        super(Disk, self).__init__({
            "productOfferUUID": productOfferUUID,
            "resourceName": resourceName,
            "size": size,
            "storageCapabilities": [
                "CLONE",
                "CHILDREN_PERSIST_ON_DELETE",
                "CHILDREN_PERSIST_ON_REVERT"
            ],
            "vdcUUID": vdcUUID,
        }, **rest)


class DiskClient(BaseClient):
    """
    Client that provides access to disk-specific functionality.
    """

    klass = Disk

    def create(self, skeleton):
        """
        Create new disk.

        Disk creation is asynchronous operation and needs to be tracked using
        job object that is returned.

        Args:
            skeleton (:obj:`Disk`): Disk skeleton.

        Returns:
           :obj:`Job`: New job, describing creation progress.
        """
        data = {"skeletonDisk": skeleton}
        return Job(self.client.post(self.endpoint, data, codes.accepted))
