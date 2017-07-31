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
"""The core RackIAM module.

This file acts as a pull in for the various core objects, making for shorter
imports.
"""
from core.policy import Policy, PolicyDocument, InlinePolicy, ManagedPolicy
from core.group import Group
from core.user import User
from core.role import Role, InstanceProfile
from core.statement import Statement
from core.helpers import generate_aws_account_arn, generate_arn

__all__ = [
    'Policy', 'PolicyDocument', 'InlinePolicy', 'generate_aws_account_arn',
    'generate_arn', 'Role', 'Statement', 'ManagedPolicy', 'User', 'Group',
    'InstanceProfile'
]
