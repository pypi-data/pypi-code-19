# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from ..importer import ImporterF1
from ..input import Message
from .worker import Worker

class WorkerF1 (Worker):
    """
    Worker model for F1 import
    """

    __slots__ = ()

    def __init__(self, params):
        super().__init__(params=params)

        messages = []

        # Process each F1 entry inside the messages list
        for element in self.incomingMessage:
            assert type(element) == dict, "A params element must be a dict"

            message = Message(definition=element)
            print (message)
            print (self.incomingConfig)
            print ()
            print ()
            print ()

#            try:
##            message = Message(definition=element)
##            importer = ImporterF1(message=message, config=self.incomingConfig)
##            consumptions = importer.process_measures()

#            except:
#                print ("Message '{}' can't be processed".format(message))

def ImportF1(params):
    Importer = WorkerF1(params=params)

