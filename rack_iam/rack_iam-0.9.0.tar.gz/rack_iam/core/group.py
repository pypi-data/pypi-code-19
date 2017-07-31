# -*- coding: utf-8 -*-
# Copyright 2017 Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Rack IAM Group module.

This module is used to handle IAM groups.
"""
from rack_iam.core.helpers import generate_arn


class Group(object):
    """A class for dealing with IAM groups."""

    def __init__(self, groupname, users=[], path='/'):
        """Create a group object.

        This sets the name of the group, as well as optionally setting a list of
        usernames and a resource path.

        Args:
            groupname (str): The name of the group
            users ([]str): A list of users to add to the group
            path (str): The path of the IAM group
        """
        self.path = path
        self.groupname = groupname
        self.managed_policy_arns = []
        self.policies = []
        self.users = set(users)

    def set_managed_policy_arns(self, arns):
        """Set the managed policy ARNs for a group.

        Args:
            arns ([]str): The managed policy ARNs
        Returns:
            Group: the class instance for function chaining

        """
        self.managed_policy_arns = arns
        return self

    def add_policy(self, policy):
        """Add a policy to the group.

        Args:
            policy (InlinePolicy): An inline policy to add to the group
        Returns:
            Group: the class instance for function chaining

        """
        self.policies.append(policy)
        return self

    def add_users(self, users):
        """Add user(s) to the group.

        Args:
            users ([]str): Names of IAM users to add to the group
        Returns:
            Group: the class instance for function chaining

        """
        self.users.update(users)
        return self

    def get_arn(self, region='', account_id=''):
        """Generate an ARN for the Group resource.

        Returns:
            str: The ARN for the group

        """
        return generate_arn('aws', 'iam', region=region, account_id=account_id,
                            resource='group/{}'.format(self.groupname))
