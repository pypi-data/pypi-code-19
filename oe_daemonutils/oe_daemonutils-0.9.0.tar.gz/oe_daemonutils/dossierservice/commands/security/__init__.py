# -*- coding: utf-8 -*-
from oe_daemonutils.circuit import DaemonCircuitBreaker
from oe_daemonutils.dossierservice.commands import BasicCommand
from requests import RequestException


class RetrieveSystemTokenCommand(BasicCommand):
    def __init__(self, logger, oauth_helper, failure_threshold=5, timeout_default=60,
                 max_timeout=300,
                 invocation_timeout=60):
        """
        Get a oeauth system token

        :param logger: logger for the operation
        :param oauth_helper: an oauth_helper instance
        :param failure_threshold: the couples of times the operation should fail before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.logger = logger
        self.oauth_helper = oauth_helper
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout

    def execute(self):
        self.logger.debug('retrieving system token')
        circuit = DaemonCircuitBreaker(self.oauth_helper.get_system_token, self.logger,
                                       (IOError, RequestException),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        response = circuit.call()
        self.logger.debug('retrieved system token')
        return response
