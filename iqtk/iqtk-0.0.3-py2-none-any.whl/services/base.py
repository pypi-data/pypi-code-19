#!/usr/bin/env bash
# Copyright 2017 The Regents of the University of California
#
# Licensed under the BSD-3-clause license (the "License"); you may not
# use this file except in compliance with the License.
# You are provided a copy of the license in LICENSE.md at the root of
# this project.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Inquiry toolkit workflows API service."""

import logging


class Service(object):
    """Base class for iqtk services."""

    def __init__(self):
        """Initialize a service wrapper object.

        In this context, a service is simply something with a run() method and
        inheriting from a base Service class allows the base to configure
        additional things related to logging, configs, ...

        Todo:
            * Implement it.
        """
        pass

    def run(self):
        logging.error('Service subclass misconfigured, must override .run()')


class ServiceRegistry(object):
    """A simple registry of services by name limiting props. of registrants."""

    def __init__(self, services={}):
        """Initialize the service registry.

        Args:
            services: A dictionary of service_name, base.Service pairs

        Example:
            sr = ServiceRegistry({
                'flow_runner': WorkflowService,
                'iot_handler': IOTHandlerService,
                'api_service': APIService
                })
            if sr.recognizes_name('iot_handler'):
                sr.get_service('iot_handler').run()

        """
        self._validate_services_definition(services)
        self.services = services

    def _validate_services_definition(self, services):
        if not isinstance(services, dict):
            msg = ("services must be defined in a dictionary, "
                   "saw %s" % services)
            raise TypeError(msg)
        for k, v in services.items():
            if not hasattr(v, 'run'):
                msg = ('objects must define a run() method to be used as '
                       'services with ServiceRegistry')
                raise TypeError(msg)

    def recognizes_name(self, service_name):
        """Returns true if a service name is the name of a known service."""
        if not isinstance(service_name, str):
            raise ValueError('sr.recognizes(s_name) expects str s_name')
        return (service_name in self.services)

    def get_service(self, service_name, fail_on_unknown=True):
        """Returns a service from the registry given a valid service name."""
        if self.recognizes_name(service_name):
            return self.services[service_name]
        else:
            msg = ('The requested service, %s was not found in the set of '
                   'known services.') % service_name
            logging.error(msg)
            raise ValueError(msg)

    def run_service(self, service_name):
        """Start a service from the registry by name."""
        s = self.get_service(service_name)
        s().run()
