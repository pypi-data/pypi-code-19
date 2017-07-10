# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from decimal import Decimal

class Message (object):
    """
    Message model
    """

    def __init__(self, id=-1, definition=None):
        assert type(id) == int

        self.name = "message"
        self.id = id

        if definition:
            assert type(definition) == dict, "Definition must be a dict"
            self.values = definition

    def __getitem__(self, key):
        if key in self.values:
            if key == "measure":
                if self.values[key] != None:
                    return Decimal(self.values[key])

            elif key == "invoice_id":
                if self.values[key] != None:
                    return int(self.values[key])

            return self.values[key]
        return None

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def __contains__(self, key):
        return key in self.values

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return repr(self.values)
