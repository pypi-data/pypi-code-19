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
"""Transformation of user related objects."""
from .policy import transform_inline_policy


def transform_user(user_obj):
    """Transform a User object to a CF structured python dictionary.

    Args:
        user_obj (User): The Rack IAM User object to convert to a CloudFormation
            dictionary.

    Returns:
        dict: The CloudFormation structured python dictionary.

    """
    user_dictionary = {
        user_obj.username: {
            "Type": "AWS::IAM::User"
        }
    }

    user_properties = {
        "Path": user_obj.path,
        "UserName": user_obj.username
    }

    if user_obj.managed_policy_arns:
        user_properties["ManagedPolicyArns"] = \
            user_obj.managed_policy_arns

    if user_obj.groups:
        user_properties["Groups"] = \
            user_obj.groups

    if len(user_obj.policies) > 0:
        user_properties["Policies"] = [
            transform_inline_policy(policy)
            for policy in user_obj.policies
        ]

    if user_obj.login_profile:
        user_properties["LoginProfile"] = {
            "Password": user_obj.login_profile[0],
            "PasswordResetRequired": user_obj.login_profile[1]
        }

    user_dictionary[user_obj.username]["Properties"] = user_properties
    return user_dictionary
