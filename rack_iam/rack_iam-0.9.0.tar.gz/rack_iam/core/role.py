#!/bin/env python
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
"""The Rack IAM Role module.

This is the high level role module. In most cases of integration, another object
is possibly used (troposphere for example). This module primarily integrates
with the policy module.
"""
from rack_iam.core.helpers import generate_arn


class Role(object):
    """A class for dealing with IAM roles."""

    def __init__(self, name, path="/"):
        """Initialize the role object with name and path.

        This sets the name and path, then initializes assume role policy
        document, managed policy arns, and policies for use later.

        Args:
            name (str): The name of the role
            path (str): This is a friendly way of declaring an IAM role based on
                some form of structural needs. More information on this can be
                found at the IAM user guide.
        """
        self.name = name
        self.path = path
        self.assume_role_policy_document = None
        self.managed_policy_arns = []
        self.policies = []

    def add_policy(self, policy):
        """Add a policy to the role.

        Args:
            policy (InlinePolicy): An inline policy to add to the role
        Returns:
            Role: the class instance for function chaining

        """
        self.policies.append(policy)
        return self

    def set_assume_policy(self, policy):
        """Set the assume role policy document to the role.

        Args:
            policy (PolicyDocument): A policy document which declares assumed
                role permission information.
        Returns:
            Role: the class instance for function chaining

        """
        self.assume_role_policy_document = policy
        return self

    def set_managed_policy_arns(self, policy_arns):
        """Set the managed policy ARNS.

        Args:
            policy_arns ([]str): A list of managed policy arns
        Returns:
            Role: the class instance for function chaining

        """
        self.managed_policy_arns = policy_arns
        return self

    def get_arn(self, region='', account_id=''):
        """Generate an ARN for the Role resource.

        Returns:
            str: The ARN for the role

        """
        return generate_arn('aws', 'iam', region=region, account_id=account_id,
                            resource='role/{}'.format(self.name))


class InstanceProfile(object):
    """Class for dealing with Instance profiles."""

    def __init__(self, name, rolename, path='/'):
        """Initialize the Instance Profile with name, role, and path.

        This sets the name, role to be associated, and the path.

        Args:
            name (str): The name of the instance profile
            rolename (str): Name of the role to associate with this profile
            path (str): This is a friendly way of declaring an IAM role based on
                some form of structural needs. More information on this can be
                found at the IAM user guide.
        """
        self.name = name
        self.rolename = rolename
        self.path = path

    def get_arn(self, region='', account_id=''):
        """Generate an ARN for the Instance Profile resource.

        Returns:
            str: The ARN for the instance profile

        """
        return generate_arn('aws', 'iam', region=region, account_id=account_id,
                            resource='instance-profile/{}'.format(self.name))
