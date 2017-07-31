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
"""The Rack IAM Policy module.

This module is meant to work with policies, determining what permissions are
allowed in a role. Ties in very closely with the statement module.
"""
from rack_iam.core.helpers import generate_arn


class PolicyDocument(object):
    """Handles statements within policies."""

    POLICY_VERSION = "2012-10-17"

    def __init__(self, policy_id=None):
        """Initialize the PolicyDocument object with a blank statements list.

        Args:
            policy_id (str): The ID of the policy
        """
        self.statements = []
        self.policy_id = policy_id

    def set_policy_id(self, policy_id):
        """Set the id of the policy.

        Args:
            policy_id (str): The ID to set for the policy
        Returns:
            PolicyDocument: The class instance for function chaining

        """
        self.policy_id = policy_id
        return self

    def add_statement(self, statement):
        """Add a statement to a policy document.

        Args:
            statement (Statement): The statement to add to the policy doc
        Returns:
            PolicyDocument: the class instance for function chaining

        """
        self.statements.append(statement)
        return self

    def add_statements(self, statements):
        """Add multiple statements to a policy document.

        Args:
            statements([]Statement): The statements to add to the policy doc
        Returns:
            PolicyDocument: The class instance for function chaining

        """
        self.statements.extend(statements)
        return self


class PolicyBase(object):
    """The base class for Policy related top-level objects.

    The parent class for both inline policies and policy resources. This is done
    as both slightly differ in structure.
    """

    def __init__(self, name):
        """Create a PolicyBase object.

        This sets the name of the policy, as well as setting up a blank
        policy_document value

        Args:
            name (str): The name of the policy
        """
        self.name = name
        self.policy_document = None

    def set_policy_document(self, policy_document):
        """Add a policy document to the policy.

        Args:
            policy_document (PolicyDocument): The policy document to add to
                the policy.
        Returns:
            PolicyBase: the class instance for function chaining

        """
        self.policy_document = policy_document
        return self


class InlinePolicy(PolicyBase):
    """A class for dealing with inline policy objects.

    The most used class for integration with other parts of AWS outside of IAM
    roles, such as S3 bucket permissions. Also what is used for policies within
    a role.
    """

    def __init__(self, name):
        """Initialize an InlinePolicy object."""
        super(InlinePolicy, self).__init__(name)


class Policy(PolicyBase):
    """A class for dealing with policy objects."""

    def __init__(self, name, groups=[], roles=[], users=[]):
        """Create a policy object.

        This sets the name of the policy, as well as setting up a blank
        policy_document value.

        Args:
            name (str): The name of the policy
            groups ([]str): A list of IAM groups the policy applies to
            roles ([]str): A list of IAM roles the policy applies to
            users ([]str): A list of IAM users the policy applies to
        """
        self.groups = set(groups)
        self.roles = set(roles)
        self.users = set(users)
        super(Policy, self).__init__(name)

    def add_users(self, users):
        """Add users to policy.

        This adds a list of users to the policy. Ignores duplicate entries as
        well.

        Args:
            users ([]str): The users to add to the policy
        Returns:
            Policy: the class instance for function chaining

        """
        self.users.update(users)
        return self

    def add_roles(self, roles):
        """Add roles to policy.

        This adds a list of roles to the policy. Ignores duplicate entries as
        well.

        Args:
            roles ([]str): The roles to add to the policy
        Returns:
            Policy: the class instance for function chaining

        """
        self.roles.update(roles)
        return self

    def add_groups(self, groups):
        """Add groups to policy.

        This adds a list of groups to the policy. Ignores duplicate entries as
        well.

        Args:
            groups ([]str): The groups to add to the policy
        Returns:
            Policy: the class instance for function chaining

        """
        self.groups.update(groups)


class ManagedPolicy(Policy):
    """A class for dealing with managed policy objects."""

    def __init__(self, name, desc, groups=[], roles=[], users=[]):
        """Create a managed object.

        This sets the name of the managed policy, as well as which users,
        groups, or roles to apply it to.

        Args:
            name (str): The name of the managed policy
            desc (str): The description of the managed policy
            groups ([]str): A list of IAM groups the managed policy applies to
            roles ([]str): A list of IAM roles the managed policy applies to
            users ([]str): A list of IAM users the managed policy applies to
        """
        self.description = desc
        super(ManagedPolicy, self).__init__(name, groups, roles, users)

    def get_arn(self, region='', account_id=''):
        """Generate an ARN for the Managed Policy resource.

        Returns:
            str: The ARN for the managed policy

        """
        return generate_arn('aws', 'iam', region=region, account_id=account_id,
                            resource='policy/{}'.format(self.name))
