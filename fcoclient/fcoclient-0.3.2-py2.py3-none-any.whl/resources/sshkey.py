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
Module with ssh key related functionality.
"""

from requests import codes

from fcoclient.resources.base import BaseClient, Resource, ResourceType
from fcoclient.resources.job import Job


class SshKey(Resource):
    """
    Class representing ssh key.
    """

    resource_type = ResourceType.sshkey

    @staticmethod
    def skeleton():
        return SshKey(False, "ssh-rsa {YOUR KEY HERE}", "{KEY NAME}")

    def __init__(self, globalKey, publicKey, resourceName, **rest):
        """
        Create new SSH key resource.

        Detailed description of available fields can be found at key_ docs.

        .. _key: http://docs.flexiant.com/display/DOCS/REST+SSHKey

        Args:
            globalKey (bool): Makes this SSH key global
            publicKey (string): SSH public key (in authorized_keys format)
            resourceName: Name of new SSH key
            **rest: Additional skeleton fields
        """
        super(SshKey, self).__init__({
            "globalKey": globalKey,
            "publicKey": publicKey,
            "resourceName": resourceName,
        }, **rest)


class SshKeyClient(BaseClient):
    """
    Client providing access to ssh keys.
    """

    klass = SshKey

    def create(self, skeleton):
        """
        Create new SSH key.

        Key creation is asynchronous operation and needs to be tracked using
        job object that is returned.

        Args:
            skeleton (:obj:`SshKey`): Key skeleton.

        Returns:
           :obj:`Job`: New job, describing creation progress.
        """
        data = dict(skeletonSSHKey=skeleton)
        return Job(self.client.post(self.endpoint, data, codes.accepted))
