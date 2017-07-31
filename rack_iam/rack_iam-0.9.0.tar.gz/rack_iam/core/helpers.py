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
"""Helper functions for modules.

Primarily functions that are shared across other modules. Currently it has
ARN related functions for use with the Statement module in declaring
principals.
"""


def generate_arn(partition='', service='', region='',
                 account_id='', resource=''):
    """Generate an ARN value.

    Args:
        partition (str): The partition that the resource is in. For standard
            AWS regions, the partition is aws. If you have resources in other
            partitions, the partition is aws-partitionname. For example, the
            partition for resources in the China (Beijing) region is aws-cn

        service (str): The service namespace that identifies the AWS product
            (for example, Amazon S3, IAM, or Amazon RDS)

        region (str): The region the resource resides in. Note that the ARNs
            for some resources do not require a region, so this component might
            be omitted

        account_id (str): The ID of the AWS account that owns the resource,
            without the hyphens. For example, 123456789012

        resource (str): The content of this part of the ARN varies by service.
            It often includes an indicator of the type of resource for example,
            an IAM user or Amazon RDS database followed by a slash (/) or a
            colon (:), followed by the resource name itself.

    Returns:
        str: The generated ARN

    """
    return "arn:{}:{}:{}:{}:{}".format(
        partition, service, region, account_id, resource
    )


def generate_aws_account_arn(account_id, resource='root'):
    """Generate an account ID arn.

    This helper function is primarily used in declaring principles in
    assume role policy documents. Using resource allows for defining
    entries such as cross account roles, or specific users.

    Args:
        account_id (str): The ID of the account
        resource (str): Defaults to root. When this argument is used it's
            generally for indicating a user that is not root.

    Returns:
        str: The account ID ARN

    """
    return generate_arn(
        partition='aws',
        service='iam',
        account_id=account_id,
        resource=resource)
