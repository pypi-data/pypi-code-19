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
"""Transformation of group related objects."""
from .policy import transform_inline_policy


def transform_group(group_obj):
    """Transform a Group object into a CloudFormation formatted dictionary.

    Args:
        group_obj (Group): The Rack IAM Group object to generate the
            CloudFormation formatted dictionary

    Returns:
        dict: The CloudFormation structured dictionary

    """
    group_dictionary = {
        group_obj.groupname: {
            "Type": "AWS::IAM::Group"
        }
    }

    group_properties = {
        "Path": group_obj.path,
        "GroupName": group_obj.groupname
    }

    if len(group_obj.managed_policy_arns) > 0:
        group_properties["ManagedPolicyArns"] = group_obj.managed_policy_arns

    if len(group_obj.policies) > 0:
        group_properties["Users"] = group_obj.users

    if len(group_obj.policies) > 0:
        group_properties["Policies"] = [
            transform_inline_policy(policy)
            for policy in group_obj.policies
        ]

    group_dictionary[group_obj.groupname]["Properties"] = group_properties
    return group_dictionary


def transform_group_users(group_obj):
    """Transform a Group object's users into a UserToGroupAddition.

    Args:
        group_obj (Group): The Rack IAM Group to get the users for association

    Returns:
        dict: The CloudFormation structured diction for UserToGroupAddition

    """
    return {
        '{}UserAssociation'.format(group_obj.groupname): {
            "Type": "AWS::IAM::UserToGroupAddition",
            "Properties": {
                "GroupName": group_obj.groupname,
                "Users": group_obj.users
            }
        }
    }
