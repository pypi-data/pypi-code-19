# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from ..importer import ImporterStaticData
from ..input import Message
from .worker import Worker

class WorkerStaticData (Worker):
    """
    Worker model for Static Data import
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

        importer = ImporterStaticData(messages=messages, config=self.incomingConfig)
        importer.process_contracts()


def ImportStaticData(params):
    Importer = WorkerStaticData(params=params)
