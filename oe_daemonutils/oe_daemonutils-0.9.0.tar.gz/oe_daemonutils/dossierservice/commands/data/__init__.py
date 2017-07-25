# -*- coding: utf-8 -*-
import requests
import json

from oe_daemonutils.circuit import DaemonCircuitBreaker
from oe_daemonutils.dossierservice.commands import BasicCommand
from oe_daemonutils.dossierservice.utils import text_

from requests import RequestException


class MasterdataNotFoundException(Exception):
    def __init__(self, data_uri):
        self.data_uri = data_uri

    def __str__(self):
        return "MasterdataNotFoundException: not found for url: {0}".format(self.data_uri)


class RetrieveDataCommand(BasicCommand):
    def __init__(self, logger, system_token, failure_threshold=5, timeout_default=60,
                 max_timeout=300,
                 invocation_timeout=60):
        """
        Get the json data of the uri

        :param logger: logger for the operation
        :param system_token: system token
        :param failure_threshold: the couples of times the operation should fail before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.logger = logger
        self.headers = {'OpenAmSSOID': system_token, 'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout

    def execute(self, data_uri):
        circuit = DaemonCircuitBreaker(self._get_data, self.logger,
                                       (IOError, ValueError, RequestException),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        return circuit.call(data_uri)

    def _get_data(self, data_uri):
        """
        Get the json data of the uri

        :param data_uri: uri
        :return: json data
        """
        data_response = requests.get(data_uri, headers=self.headers)
        data_response.raise_for_status()
        return json.loads(text_(data_response.content))


class RetrieveMasterdataCommand(BasicCommand):
    def __init__(self, logger, system_token, failure_threshold=5, timeout_default=60,
                 max_timeout=300,
                 invocation_timeout=60):
        """
        Get the json data of the uri

        :param logger: logger for the operation
        :param system_token: system token
        :param failure_threshold: the couples of times the operation should fail before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.logger = logger
        self.headers = {'OpenAmSSOID': system_token, 'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout

    def execute(self, data_uri):
        circuit = DaemonCircuitBreaker(self._get_master_data, self.logger,
                                       (IOError, ValueError, RequestException),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        return circuit.call(data_uri)

    def _get_master_data(self, data_uri):
        """
        Get the json data of the uri

        :param data_uri: uri
        :return: json data
        :return: raise MasterdataNotFoundException when request raises a Not Found exception
        """
        data_response = requests.get(data_uri, headers=self.headers)
        if data_response.status_code == 404:
            raise MasterdataNotFoundException(data_uri)
        else:
            data_response.raise_for_status()
        return json.loads(text_(data_response.content))


class SaveDataCommand(BasicCommand):
    def __init__(self, logger, system_token, failure_threshold=5, timeout_default=60,
                 max_timeout=300,
                 invocation_timeout=60):
        """
        Save data to a specific uri

        :param logger: logger for the operation
        :param system_token: system token
        :param failure_threshold: the couples of times the operation should fail before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.logger = logger
        self.headers = {'OpenAmSSOID': system_token, 'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout

    def execute(self, data_uri, data, post=False):
        """
        Save data to a specific uri

        :param data_uri: uri
        :param data: the json data to save
        :param post: create data (use POST instead of PUT)
        :return: json data or None
        """
        circuit = DaemonCircuitBreaker(self._save_data, self.logger,
                                       (IOError, ValueError, RequestException),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        return circuit.call(data_uri, data, post=post)

    def _save_data(self, data_uri, data, post=False):
        """
        Save data to a specific uri

        :param data_uri: uri
        :param data: the json data to save
        :param post: create data (use POST instead of PUT)
        :return: json data or None
        """
        if post:
            data_response = requests.post(data_uri, data=json.dumps(data), headers=self.headers)
        else:
            data_response = requests.put(data_uri, data=json.dumps(data), headers=self.headers)
        data_response.raise_for_status()
        if data_response.content:
            return json.loads(text_(data_response.content))
        else:
            return None
