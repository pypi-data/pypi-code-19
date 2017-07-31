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
"""Transformation of statement related objects."""


def transform_statement(statement_object):
    """Transform a Role object to a CF structured python dictionary.

    Args:
        statement_object (Statement): The Rack IAM Statement object to convert
        to a CloudFormation dictionary.

    Returns:
        dict: The CloudFormation structured python dictionary.

    """
    statement_dict = {
        "Effect": statement_object.effect,
        "Action": statement_object.action,
    }

    if statement_object.sid:
        statement_dict["Sid"] = statement_object.sid

    if statement_object.resource:
        statement_dict["Resource"] = statement_object.resource

    if statement_object.principal:
        statement_dict["Principal"] = statement_object.principal

    if statement_object.condition:
        statement_dict["Condition"] = statement_object.condition

    return statement_dict
