# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

class Worker (object):
    """
    Generic Worker model
    """

    __slots__ = ('incomingMessage', 'incomingConfig')

    def __init__(self, params):
        """
        Do generic validations about the format of the message
        """
        assert isinstance(params, tuple), "Incoming Params must be a tuple"

        self.incomingMessage = params[0]
        self.incomingConfig = params[1]

        assert isinstance(self.incomingMessage, list), "Message in Params must be a list of dicts"
        assert isinstance(self.incomingMessage[0], dict), "A Message from the list must be a dict"

        assert isinstance(self.incomingConfig, dict), "Config in Params must be a dict"
