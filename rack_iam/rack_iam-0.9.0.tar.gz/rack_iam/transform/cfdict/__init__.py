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
"""The CloudFormation dictionary transformation module.

This module is used in the transformation of various Rack IAM objects to
a python dictionary which is formatted to the structure of the respective
CloudFormation object.

"""
from .policy import (
    transform_inline_policy,
    transform_policy,
    transform_policy_document,
    transform_managed_policy,
)
from .user import transform_user
from .group import transform_group, transform_group_users
from .role import transform_role
from .statement import transform_statement

__all__ = [
    'transform_role',
    'transform_statement',
    'transform_policy_document',
    'transform_policy',
    'transform_inline_policy',
    'transform_managed_policy',
    'transform_user',
    'transform_group',
    'transform_group_users'
]
