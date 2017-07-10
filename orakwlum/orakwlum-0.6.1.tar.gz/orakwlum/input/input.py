# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from .message import Message
from .file import File


class Input (object):
    """
    Input model
    """

    __slots__ = ('message', 'file')

    def __init__(self, definition):
        """
        Creates a Input object from a redis SMS definition //dictionary with
            - messageID
            - fileName
            - md5sum
            - fileType

        Uses a File and a Message objects
        """

        assert 'messageID' in definition
        assert 'fileName' in definition
        assert 'md5sum' in definition
        assert 'fileType' in definition

        self.message = Message(id=definition['messageID'])
        self.file = File(
            id=definition['messageID'],
            filename=definition['fileName'],
            filetype=definition['fileType']
            )

    @property
    def id (self):
        return self.message.id

    @property
    def filename (self):
        return self.file.name
