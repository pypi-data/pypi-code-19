# -*- coding: utf-8 -*-
from watson.framework import listeners
from watson.cors import utils


class Request(listeners.Base):
    def __call__(self, event):
        response = event.params['context']['response']
        request = event.params['context']['request']
        route = event.params['context']['route_match'].route
        conf = utils.generate_cors_config(
            self.container,
            route)
        utils.process_cors(
            request,
            response, **conf)
        return response
