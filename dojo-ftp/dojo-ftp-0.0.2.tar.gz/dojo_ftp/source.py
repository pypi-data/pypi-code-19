from __future__ import absolute_import, print_function, unicode_literals


from dojo.vanilla.dataset import VanillaDataset


class FTPSource(VanillaDataset):

    CONFIG = {
        'type': 'object',
        'properties': {
            'days': {'type': 'integer', 'default': 1},
            'connection': {'type': 'object', 'properties': {
                'host': {'type': 'string'},
                'user': {'type': 'string'}
            }, 'required': ['host', 'user']}
        }
    }

    SECRETS = {
        'type': 'object',
        'properties': {
            'connection': {'type': 'object', 'properties': {
                'password': {'type': 'string'}
            }}
        }
    }

    OUTPUT = {
        'type': 'object',
        'properties': {
        }
    }

    def process(self, inputs):
        return []
