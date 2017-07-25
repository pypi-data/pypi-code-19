# -*- coding: utf-8 -*-
import requests
import json

from oe_daemonutils.circuit import DaemonCircuitBreaker
from oe_daemonutils.dossierservice.commands import BasicCommand
from requests import RequestException


class RetrieveEmailsActorenCommand(BasicCommand):
    def __init__(self, logger, system_token, failure_threshold=5, timeout_default=60,
                 max_timeout=300,
                 invocation_timeout=60):
        """
        Get the email addresses of the actors given the actor_uris.
        Preference is given to the work e-mail addresses.

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

    def execute(self, actors):
        circuit = DaemonCircuitBreaker(self._get_actor_email, self.logger,
                                       (IOError, ValueError, RequestException),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        emails = [circuit.call((actor["actor"])) for actor in actors]
        return [email for email in emails if email]

    def _get_actor_email(self, actor_uri):
        """
        Get the email of the actor given the actor_uri.
        Preference is given to the work e-mail address.

        :param actor_uri: uri van de actor ('http//id.erfgoed.net/actoren/1')
        :return: string email address
        """
        res = requests.get(
                actor_uri,
                headers=self.headers
        )
        res.raise_for_status()
        actor = json.loads(res.text)
        return next((email['email'] for email in actor.get('emails', []) if email.get('type', {}).get('id', None) == 2),
                    next((email['email'] for email in actor.get('emails', [])), None))
