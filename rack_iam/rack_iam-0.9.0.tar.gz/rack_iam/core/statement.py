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
"""The Rack IAM Statement module.

The lowest level module of core and the main location where permissions are
defined. Given this it's also the most complex module. Used by the policy
module.
"""
from .helpers import generate_aws_account_arn


class Statement(object):
    """Statement class that handles basic permissions."""

    def __init__(self, effect, action, resource=None, sid=None):
        """Initialize a statement with various permissions.

        Args:
            effect (str): One of "Allow" or "Deny", indicating whether the
                actions declared will be allowed or denied.

            action ([]str or "*"): The permissions that will be affected by
                effect. Use "*" if all permissions are to be granted.

            resource (str): The resource to apply the permission to within the
                service.

            sid (str): The statement ID for the statement
        """
        self.effect = effect
        # If you're doing an all action specification than
        # the action doesn't need to be a list anymore
        if action == ["*"]:
            self.action = "*"
        else:
            self.action = action
        self.principal = None
        self.condition = None
        self.resource = resource
        self.sid = sid

    def set_statement_id(self, sid):
        """Set the ID for the statement.

        Args:
            sid (str): The statement ID to set
        Returns:
            Statement: The class instance for function chaining

        """
        self.sid = sid
        return self

    # Principal related functionality
    def set_principal(self, name, value):
        """Set the principal of the statement.

        Args:
            name (str): The name of the principal, such as "AWS", "Service", or
                "Federated".

            value (str): This can be a number of things. For multiple values a
                list is given with the values declared. Single values will just
                be a string value. Classes can also be used, for example
                troposphere related functions such as Join() and Ref().
        Returns:
            Statement: the class instance for function chaining

        """
        self.principal = {name: value}
        return self

    # AWS account related principles
    def set_account_principal(self, account_id, resource='root',
                              external_id=None):
        """Set an AWS account as a principal.

        This is a boilerplate function as account principals are fairly common.
        External ID is used as a conditional which allows the principal to be
        restricted even further for cases where the delegate could be handling
        more than one customer.

        Args:
            account_id (str): The ID of the AWS account

            resource (str): Using root will give access to the entire account
                in question. To restrict to specific users, cases such as
                `user/Dave` can be used instead.

            external_id (str): The external ID to use for further principal
                access conditions.
        Returns:
            Statement: the class instance for function chaining

        """
        # This is a special case for libraries such as troposphere
        # which may have parameters passed in as Join/Ref and will cause
        # ugly results when passed to format(), used by
        # generate_*_arn type functions
        if isinstance(account_id, basestring):
            self.set_principal("AWS", generate_aws_account_arn(
                account_id, resource))
        else:
            self.set_principal("AWS", account_id)

        if external_id:
            self.set_external_id(external_id)
        return self

    def set_multi_account_principal(self, account_resource_map,
                                    external_id=None):
        """Set multiple AWS accounts as a principal.

        Mainly a wrapper around set_account_principal. It's used to indicate
        that a permission will be available to multiple AWS account identifiers.

        Args:
            account_resource_map (dict): A dictionary in the form:
                { account_id: resource } where account ID is a string with
                the account ID, and resource is either root or a path to say a
                specific user. external_id (str): The external ID to use for
                further principal access conditions. Note that since external ID
                is a condition, it will apply to all IDs and resources given.
        Returns:
            Statement: the class instance for function chaining

        """
        principals = []

        for account_id, resource in account_resource_map:
            if isinstance(account_id, basestring):
                principals.append(generate_aws_account_arn(
                    account_id, resource
                ))
            else:
                principals.append(account_id)

        self.set_principal("AWS", principals)

        if external_id:
            self.set_external_id(external_id)
        return self

    def set_user_principal(self, account_id, user_path, external_id=None):
        """Set an AWS account IAM user as a principle.

        This is a wrapper around set_account_principal for setting a principal
        to be a specific user on an AWS account.

        Args:
            account_id (str): The ID of the AWS account
            user_path (str): The path to the user on the AWS account
            external_id (str): The external ID to use for further principal
                access conditions.
        Returns:
            Statement: the class instance for function chaining

        """
        self.set_account_principal(account_id, resource=user_path,
                                   external_id=external_id)
        return self

    # AWS Service Principal
    def set_service_principal(self, services):
        """Set an AWS service as a resource.

        This is mainly used for the assume role policy document, for letting
        services assume a role.

        Args:
            services ([]str): A list of services, such as "ec2.amazonaws.com"
                which are allowed to take on permissions
        Returns:
            Statement: the class instance for function chaining

        """
        self.set_principal("Service", services)
        return self

    # AWS Federated Principal
    def set_federated_principal(self, host):
        """Set a federated login service as a principle.

        This is mainly used for the assume role policy document, for letting
        federated users assume a role.

        Args:
            host (str): The federated login host
        Returns:
            Statement: the class instance for function chaining

        """
        self.set_principal("Federated", host)
        return self

    # Condition related functionality
    def set_condition(self, operator, condition):
        """Set the condition for the statement.

        Args:
            operator (str): The operator used to test against the condition
            condition (dict): A dictionary that explains the condition. An
                example would be {"sts:ExternalId": "foobar"}
        Returns:
            Statement: the class instance for function chaining

        """
        self.condition = {operator: condition}
        return self

    def set_external_id(self, external_id):
        """Set the external ID condition for the statement.

        A wrapper around set_condition for specifically working with external
        IDs

        Args:
            external_id (str): The external ID to further lock down the
                statement in cases where the delegate may also be working with
                other AWS users.
        Returns:
            Statement: the class instance for function chaining

        """
        self.set_condition("StringEquals", {"sts:ExternalId", external_id})
        return self
