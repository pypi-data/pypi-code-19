# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Look for known crawlers user-agents
"""

from logging import getLogger

from .matcher_callback import MatcherRule
from ..runtime_infos import runtime


LOGGER = getLogger(__name__)


class CrawlerUserAgentMatchesMetricsCB(MatcherRule):
    def pre(self, original, *args, **kwargs):
        """ For each request, record an observation with the user_agent without
        case modification.
        """
        request = runtime.get_current_request()

        if not request:
            LOGGER.warning("No request was recorded abort")
            return

        user_agent = request.client_user_agent

        if not user_agent:
            return

        if self.match(user_agent):
            self.record_observation('crawler', user_agent, 1)
