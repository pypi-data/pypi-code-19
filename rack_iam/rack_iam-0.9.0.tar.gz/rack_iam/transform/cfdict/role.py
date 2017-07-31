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
"""Transformation of role related objects."""
from .policy import transform_policy_document
from .policy import transform_inline_policy


def transform_role(role_obj):
    """Transform a Role object to a CF structured python dictionary.

    Args:
        role_obj (Role): The Rack IAM Role object to convert to a CloudFormation
            dictionary.

    Returns:
        dict: The CloudFormation structured python dictionary.

    """
    role_dictionary = {
        role_obj.name: {
            "Type": "AWS::IAM::Role"
        }
    }

    role_properties = {
        "Path": role_obj.path,
        "RoleName": role_obj.name
    }

    if role_obj.assume_role_policy_document:
        role_properties["AssumeRolePolicyDocument"] = \
            transform_policy_document(
                role_obj.assume_role_policy_document
            )

    if role_obj.managed_policy_arns:
        role_properties["ManagedPolicyArns"] = \
            role_obj.managed_policy_arns

    if len(role_obj.policies) > 0:
        role_properties["Policies"] = [
            transform_inline_policy(policy)
            for policy in role_obj.policies
        ]

    role_dictionary[role_obj.name]["Properties"] = role_properties
    return role_dictionary
