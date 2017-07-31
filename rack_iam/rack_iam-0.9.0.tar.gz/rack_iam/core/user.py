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
"""The Rack IAM User module.

This module is used to handle IAM users.
"""
from rack_iam.core.helpers import generate_arn


class User(object):
    """A class for dealing with IAM users."""

    def __init__(self, username, groups=[], path='/'):
        """Create a user object.

        This sets the name of the user, as well as optionally setting group
        membership and resource path

        Args:
            username (str): The name of the user
            groups ([]str): A list of IAM groups the user will be a member of
            path (str): The path of the IAM user
        """
        self.groups = set(groups)
        self.path = path
        self.username = username
        self.managed_policy_arns = []
        self.login_profile = None
        self.policies = []

    def set_managed_policy_arns(self, arns):
        """Set the managed policy ARNs for a user.

        Args:
            arns ([]str): The managed policy ARNs
        Returns:
            User: the class instance for function chaining

        """
        self.managed_policy_arns = arns
        return self

    def set_login_profile(self, password, password_reset=True):
        """Create a user object.

        This sets the name of the user, as well as optionally setting group
        membership and resource path

        Args:
            password (str): The password to set for the user
            password_reset (bool): Whether or not to force the user to reset
                their password upon login
        Returns:
            User: the class instance for function chaining

        """
        self.login_profile = (password, password_reset)
        return self

    def add_to_group(self, group_name):
        """Add a user to a group.

        If the group_name exists no action will be taken. In the event it
        doesn't exist the group list will be updated.

        Args:
            group_name (str): The name of the group to add the user to
        Returns:
            User: the class instance for function chaining

        """
        self.groups.add(group_name)
        return self

    def add_policy(self, policy):
        """Add a policy to the user.

        Args:
            policy (InlinePolicy): An inline policy to add to the user
        Returns:
            User: the class instance for function chaining

        """
        self.policies.append(policy)
        return self

    def get_arn(self, region='', account_id=''):
        """Generate an ARN for the User resource.

        Returns:
            str: The ARN for the user

        """
        return generate_arn('aws', 'iam', region=region, account_id=account_id,
                            resource='user/{}'.format(self.username))
