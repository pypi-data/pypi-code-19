# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from ..importer import ImporterF5D
from ..input import Message
from .worker import Worker

class WorkerF5D (Worker):
    """
    Worker model for F5D import
    """

    __slots__ = ()

    def __init__(self, params):
        super().__init__(params=params)

        messages = []
        # Prepare messages from incoming params
        for element in self.incomingMessage:
            assert type(element) == dict, "A params element must be a dict"
            message = Message(definition=element)
            messages.append(message)

        importer = ImporterF5D(messages=messages, config=self.incomingConfig)
        importer.process_measures()

def ImportF5D(params):
    Importer = WorkerF5D(params=params)
