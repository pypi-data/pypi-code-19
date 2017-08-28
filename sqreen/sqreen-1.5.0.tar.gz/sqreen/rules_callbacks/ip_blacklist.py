import logging

from ..rules import RuleCallback
from ..runtime_infos import runtime
from ..utils import IPNetworkMatcher


LOGGER = logging.getLogger(__name__)


class IPBlacklistCB(RuleCallback):

    def __init__(self, *args, **kwargs):
        super(IPBlacklistCB, self).__init__(*args, **kwargs)
        self.networks = IPNetworkMatcher(self.data['values'])
        LOGGER.debug('Blacklisted IP networks: %s', self.networks)

    def pre(self, original, *args, **kwargs):
        request = runtime.get_current_request()
        if request is None:
            return
        try:
            network = self.networks.match(request.client_ip)
        except ValueError:
            LOGGER.debug("Invalid IP address %r, skipping", request.client_ip)
            return
        if network is None:
            LOGGER.debug("IP %s is not blacklisted", request.client_ip)
            return
        LOGGER.debug("IP %s belongs to blacklisted network %s",
                     request.client_ip, network)
        self.record_observation('blacklisted', network, 1)
        return {
            'status': 'raise',
            'data': network,
            'rule_name': self.rule_name,
        }
