# Copyright (c) 2016 SUSE.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# project
from azurectl.defaults import Defaults
from azurectl.azurectl_exceptions import (
    AzureReservedIpAssociateError,
    AzureReservedIpDisAssociateError,
    AzureReservedIpCreateError,
    AzureReservedIpDeleteError,
    AzureReservedIpListError,
    AzureReservedIpShowError
)


class ReservedIp(object):
    """
        Implements Azure reserved IP address management. This includes the
        following tasks:
        + creation and deletion of IP address reservations
        + listing reserved IP addresses
    """
    def __init__(self, account):
        self.account = account
        self.service = account.get_management_service()

    def list(self):
        result = []
        try:
            for ip in self.service.list_reserved_ip_addresses():
                result.append(self.__decorate_for_results(ip))
        except Exception as e:
            raise AzureReservedIpListError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return result

    def show(self, name):
        try:
            ip = self.service.get_reserved_ip_address(name)
        except Exception as e:
            raise AzureReservedIpShowError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return self.__decorate_for_results(ip)

    def create(self, name, region):
        try:
            result = self.service.create_reserved_ip_address(
                name,
                location=region
            )
        except Exception as e:
            raise AzureReservedIpCreateError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return Defaults.unify_id(result.request_id)

    def delete(self, name):
        try:
            result = self.service.delete_reserved_ip_address(name)
        except Exception as e:
            raise AzureReservedIpDeleteError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return Defaults.unify_id(result.request_id)

    def associate(self, name, cloud_service_name):
        try:
            result = self.service.associate_reserved_ip_address(
                name=name,
                service_name=cloud_service_name,
                deployment_name=cloud_service_name
            )
        except Exception as e:
            raise AzureReservedIpAssociateError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return Defaults.unify_id(result.request_id)

    def disassociate(self, name, cloud_service_name):
        try:
            result = self.service.disassociate_reserved_ip_address(
                name=name,
                service_name=cloud_service_name,
                deployment_name=cloud_service_name
            )
        except Exception as e:
            raise AzureReservedIpDisAssociateError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return Defaults.unify_id(result.request_id)

    def __decorate_for_results(self, ip):
        return {
            'name': ip.name,
            'address': ip.address,
            'state': ip.state,
            'in_use': ip.in_use,
            'cloud_service_name': ip.service_name,
            'instance_name': ip.deployment_name,
            'region': ip.location
        }
