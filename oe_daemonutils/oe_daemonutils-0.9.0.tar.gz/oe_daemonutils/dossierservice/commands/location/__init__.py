# -*- coding: utf-8 -*-
import requests
import json

from oe_daemonutils.circuit import DaemonCircuitBreaker
from oe_daemonutils.dossierservice.commands import BasicCommand
from requests import RequestException


class DetermineRegionRepsCommand(BasicCommand):
    def __init__(self, regioverantwoordelijken_url, logger, system_token, failure_threshold=5, timeout_default=60,
                 max_timeout=300,
                 invocation_timeout=60):
        """
        Bepaal de regioverantwoordelijken aan de hand van een niscode en een discipline of proces

        :param regioverantwoordelijken_url: url voor de regioverantwoordelijken service
        :param logger: logger for the operation
        :param system_token: system token
        :param failure_threshold: the couples of times the operation should fail before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.regioverantwn_url = regioverantwoordelijken_url
        self.logger = logger
        self.headers = {'OpenAmSSOID': system_token, 'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout

    def execute(self, niscodes, discipline=None, process=None):
        circuit = DaemonCircuitBreaker(self._circuit_wrapped_determine_region_reps, self.logger,
                                       (IOError, ValueError, RequestException),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        return circuit.call(niscodes, discipline=discipline, process=process)

    def _circuit_wrapped_determine_region_reps(self, niscodes, discipline=None, process=None):
        """
        Get the region reps given the area niscodes

        :param niscodes: list of niscodes
        :param discipline: discipline for the representatives
        :param process: for specific process
        :return: list of actor objects each having a "actor" attribute including the actor_uri
        """
        params = {'niscode': niscodes}
        if process:
            params["proces"] = process
        if discipline:
            params["discipline"] = discipline
        res = requests.get(
            self.regioverantwn_url,
            params=params,
            headers=self.headers
        )
        res.raise_for_status()
        return json.loads(res.text)


class DetermineNiscodesCommand(BasicCommand):
    def __init__(self, logger, admin_grenzen_client, failure_threshold=5, timeout_default=60,
                 max_timeout=300,
                 invocation_timeout=60):
        """
        Get administrative area information of the given geojson.
        If the geojson overlaps multiple administrative areas

        :param logger: logger for the operation
        :param failure_threshold: the couples of times the operation should fail before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.logger = logger
        self.admin_grenzen_client = admin_grenzen_client
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout

    def execute(self, geojson, types):
        """
        Get administrative area information of the given geojson.
        If the geojson overlaps multiple administrative areas

        :param geojson: contour geojson
        :param types: array, return types of administrative areas ['gemeente', 'provincie']
        :return: adminstative area information
        """
        circuit = DaemonCircuitBreaker(self._determine_niscodes, self.logger,
                                       (IOError, ValueError, RequestException),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        return circuit.call(geojson, types)

    def _determine_niscodes(self, geojson, types):
        results = []
        if 'gemeente' in types:
            results.append(self.admin_grenzen_client.get_gemeente(geojson))
        if 'provincie' in types:
            results.append(self.admin_grenzen_client.get_provincie(geojson))
        niscodes = [result['niscode'] for result in results]
        return niscodes
