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
"""Transformation of policy related objects."""
from .statement import transform_statement


def transform_policy_properties(policy_obj):
    """Generate shared properties for ManagedPolicy and Policy.

    Args:
        policy_obj (Policy): The Rack IAM Policy object to generate the policy
           properties for

    Returns:
        dict: The CloudFormation structured properties

    """
    policy_properties = {}

    if policy_obj.policy_document:
        policy_properties["PolicyDocument"] = \
            transform_policy_document(
                policy_obj.policy_document
            )

    if len(policy_obj.groups) > 0:
        policy_properties["Groups"] = policy_obj.groups

    if len(policy_obj.users) > 0:
        policy_properties["Users"] = policy_obj.users

    if len(policy_obj.roles) > 0:
        policy_properties["Roles"] = policy_obj.roles

    return policy_properties


def transform_policy(policy_obj):
    """Transform a Policy object to a CF structured python dictionary.

    Args:
        policy_obj (Policy): The Rack IAM Policy object to convert to a Cloud
            Formation dictionary

    Returns:
        dict: The CloudFormation structured python dictionary

    """
    policy_properties = transform_policy_properties(policy_obj)
    policy_properties["PolicyName"] = policy_obj.name
    policy_dict = {
        policy_obj.name: {
            "Type": "AWS::IAM::Policy",
            "Properties": policy_properties
        }
    }

    return policy_dict


def transform_managed_policy(policy_obj):
    """Transform a ManagedPolicy object to a CF structured python dictionary.

    Args:
        policy_obj (Policy): The Rack IAM Managed Policy object to convert to a
            Cloud Formation dictionary

    Returns:
        dict: The CloudFormation structured python dictionary

    """
    policy_properties = transform_policy_properties(policy_obj)
    policy_properties["ManagedPolicyName"] = policy_obj.name
    policy_properties["Description"] = policy_obj.description
    policy_dict = {
        policy_obj.name: {
            "Type": "AWS::IAM::ManagedPolicy",
            "Properties": policy_properties
        }
    }

    return policy_dict


def transform_inline_policy(policy_obj):
    """Transform an InlinePolicy object to a CF structured python dictionary.

    Args:
        policy_obj (InlinePolicy): The Rack IAM InlinePolicy object to convert
        to a CloudFormation dictionary

    Returns:
        dict: The CloudFormation structured python dictionary

    """
    policy_dict = {
        "PolicyName": policy_obj.name
    }

    if policy_obj.policy_document:
        policy_dict["PolicyDocument"] = \
            transform_policy_document(
                policy_obj.policy_document
            )

    return policy_dict


def transform_policy_document(document_obj):
    """Transform a PolicyDocument object to a CF structured python dictionary.

    Args:
        document_obj (PolicyDocument): The Rack IAM PolicyDocument object to
        convert to a CloudFormation dictionary

    Returns:
        dict: The CloudFormation structured python dictionary

    """
    document_dict = {
        "Version": document_obj.POLICY_VERSION,
        "Statement": [
            transform_statement(statement)
            for statement in document_obj.statements
        ]
    }

    if document_obj.policy_id:
        document_dict["Id"] = document_obj.policy_id

    return document_dict
