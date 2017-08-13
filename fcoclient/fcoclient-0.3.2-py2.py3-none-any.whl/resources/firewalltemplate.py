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
Module with firewall templates related functionality.
"""

from requests import codes

from fcoclient.resources.base import BaseClient, Resource, ResourceType
from fcoclient.resources.job import Job


class FirewallTemplate(Resource):
    """
    Class representing firewall template.
    """

    resource_type = ResourceType.firewalltemplate

    @staticmethod
    def skeleton():
        return FirewallTemplate(
            "{TEMPLATE NAME}", "{IP TYPE (most likely IPV4, IPV6)}",
            defaultInAction="REJECT", defaultOutAction="ALLOW",
            firewallInRuleList=[{
                "action": "ALLOW",
                "connState": "ALL",
                "direction": "IN",
                "icmpParam": "ECHO_REPLY_IPv4",
                "ipAddress": "{REMOTE ADDRESS (for example 0.0.0.0)}",
                "ipCIDRMask": "{CIDR MASK SIZE (for example 16 or 24)}",
                "localPort": "{LOCAL PORT}",
                "name": "{RULE NAME}",
                "protocol": "{PROTOCOL (most likely TCP or UDP)}",
                "remotePort": "{REMOTE PORT}",
            }],
        )

    def __init__(self, resourceName, type, **rest):
        """
        Create new firewall template.

        Description of all available fields can be found at _template docs.

        .. _template:
            http://docs.flexiant.com/display/DOCS/REST+FirewallTemplate

        Args:
            resourceName: Name of the firewall template
        """
        super(FirewallTemplate, self).__init__({
            "resourceName": resourceName, "type": type
        }, **rest)


class FirewallTemplateClient(BaseClient):
    """
    Client providing access to firewall templates.
    """

    klass = FirewallTemplate

    def create(self, skeleton):
        """
        Create new firewall template.

        Template creation is asynchronous operation and needs to be tracked
        using job object that is returned.

        Args:
            skeleton (:obj:`FirewallTemplate`): Firewall template skeleton.

        Returns:
           :obj:`Job`: New job, describing creation progress.
        """
        data = dict(skeletonFirewallTemplate=skeleton)
        return Job(self.client.post(self.endpoint, data, codes.accepted))

    def apply(self, uuid, address):
        """
        Apply firewall template to selected address.

        Args:
            uuid: Firewall template UUID
            address: IP address that template is applied to

        Returns:
            :obj:`Job`: New job, tracking application progress.
        """
        data = dict(ipAddress=address)
        endpoint = "{}/{}/apply".format(self.endpoint, uuid)
        return Job(self.client.put(endpoint, data, codes.accepted))
