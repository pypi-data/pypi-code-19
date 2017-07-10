# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

class File (object):
    """
    File model
    """

    def __init__(self, id, filename, filetype):
        assert type(id) == int
        assert type(filename) == str
        assert type(filetype) == str
        assert filetype in ['F1', 'Q1', 'F5D', 'Q5D'], "File type '{}' is not valid ['F1', 'Q1', 'F5D', 'Q5D']".format(filetype)

        self.name = filename
        self.type = filetype
        self.id_message = id
