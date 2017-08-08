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
from azure.servicemanagement import (
    ConfigurationSetInputEndpoint,
    ConfigurationSetInputEndpoints
)

# project
from azurectl.defaults import Defaults
from azurectl.azurectl_exceptions import (
    AzureEndpointCreateError,
    AzureEndpointDeleteError,
    AzureEndpointListError,
    AzureEndpointShowError,
    AzureEndpointUpdateError
)


class Endpoint(object):
    """
        Implements Azure endpoint management:
        handle port forwards from the cloud service to a VM instance, which
        are part of the instance role's network configuration
    """
    def __init__(self, account):
        self.account = account
        self.service = account.get_management_service()

    def set_instance(self, cloud_service_name, instance_name):
        self.cloud_service_name = cloud_service_name
        self.instance_name = instance_name

    def list(self):
        try:
            config = self.__get_network_config_for_role()
        except Exception as e:
            raise AzureEndpointListError(
                '%s: %s' % (type(e).__name__, format(e))
            )

        if config.input_endpoints:
            results = config.input_endpoints
        else:
            results = []
        return [self.__decorate(result) for result in results]

    def show(self, name):
        try:
            config = self.__get_network_config_for_role()
        except Exception as e:
            raise AzureEndpointShowError(
                '%s: %s' % (type(e).__name__, format(e))
            )

        # If there are no endpoints the input_endpoints
        # attribute is None.
        if config.input_endpoints:
            for endpoint in config.input_endpoints:
                if endpoint.name.upper() == name.upper():
                    return self.__decorate(endpoint)

        # Endpoint not found
        raise AzureEndpointShowError(
            "No endpoint named '%s' was found." % name
        )

    def create(
        self,
        name,
        external_port,
        internal_port,
        protocol,
        idle_timeout
    ):
        try:
            role = self.__get_role()
            config = self.__get_network_config_for_role(role)
            new_endpoint = ConfigurationSetInputEndpoint(
                name=name,
                protocol=protocol,
                port=external_port,
                local_port=internal_port,
                idle_timeout_in_minutes=idle_timeout,
                enable_direct_server_return=False,
            )

            # If there are no endpoints the input_endpoints
            # attribute is None. Thus create and set new instance.
            if not config.input_endpoints:
                config.input_endpoints = ConfigurationSetInputEndpoints()

            config.input_endpoints.input_endpoints.append(new_endpoint)

            result = self.service.update_role(
                self.cloud_service_name,
                self.cloud_service_name,
                role.role_name,
                os_virtual_hard_disk=role.os_virtual_hard_disk,
                network_config=config,
                availability_set_name=role.availability_set_name,
                data_virtual_hard_disks=role.data_virtual_hard_disks
            )
        except Exception as e:
            raise AzureEndpointCreateError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return Defaults.unify_id(result.request_id)

    def update(
        self,
        name,
        external_port=None,
        internal_port=None,
        protocol=None,
        idle_timeout=None
    ):
        try:
            role = self.__get_role()
            config = self.__get_network_config_for_role(role)

            if not config.input_endpoints:
                raise AzureEndpointUpdateError(
                    "No endpoints found."
                )

            for index, endpoint in \
                    enumerate(config.input_endpoints.input_endpoints):
                if endpoint.name.upper() == name.upper():
                    endpoint_index = index
                    break
            else:
                # If for loop finishes normally no endpoint
                # exists that matches the name.
                raise AzureEndpointUpdateError(
                    "No endpoint named %s was found." % name
                )

            endpoint = config.input_endpoints.input_endpoints[endpoint_index]

            if external_port:
                endpoint.port = external_port

            if internal_port:
                endpoint.local_port = internal_port

            if protocol:
                endpoint.protocol = protocol

            if idle_timeout:
                endpoint.idle_timeout_in_minutes = idle_timeout

            result = self.service.update_role(
                self.cloud_service_name,
                self.cloud_service_name,
                role.role_name,
                os_virtual_hard_disk=role.os_virtual_hard_disk,
                network_config=config,
                availability_set_name=role.availability_set_name,
                data_virtual_hard_disks=role.data_virtual_hard_disks
            )
        except Exception as e:
            raise AzureEndpointUpdateError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return Defaults.unify_id(result.request_id)

    def delete(self, name):
        try:
            role = self.__get_role()
            config = self.__get_network_config_for_role(role)

            if not config.input_endpoints:
                raise AzureEndpointDeleteError(
                    "No endpoints found."
                )

            for index, endpoint in \
                    enumerate(config.input_endpoints.input_endpoints):
                if endpoint.name.upper() == name.upper():
                    del config.input_endpoints.input_endpoints[index]
                    break
            else:
                # If for loop finishes normally no endpoint
                # exists that matches the name.
                raise AzureEndpointDeleteError(
                    "No endpoint named %s was found." % name
                )

            result = self.service.update_role(
                self.cloud_service_name,
                self.cloud_service_name,
                role.role_name,
                os_virtual_hard_disk=role.os_virtual_hard_disk,
                network_config=config,
                availability_set_name=role.availability_set_name,
                data_virtual_hard_disks=role.data_virtual_hard_disks
            )
        except AzureEndpointDeleteError:
            raise  # re-raise
        except Exception as e:
            raise AzureEndpointDeleteError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return Defaults.unify_id(result.request_id)

    def __get_role(self):
        return self.service.get_role(
            self.cloud_service_name,
            self.cloud_service_name,
            self.instance_name
        )

    def __get_network_config_for_role(self, role=None):
        role = role or self.__get_role()
        for config in role.configuration_sets:
            if config.configuration_set_type == 'NetworkConfiguration':
                return config

    def __decorate(self, endpoint):
        return {
            'name': endpoint.name,
            'port': endpoint.port,
            'instance-port': endpoint.local_port,
            'protocol': endpoint.protocol,
            'idle-timeout': '%d minutes' % endpoint.idle_timeout_in_minutes
        }
