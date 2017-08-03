# -*- coding: utf-8 -*-
import json


class Response(object):
    '''
    Response of a client RPC call.
    '''
    def __init__(self, content_type, content):
        self.content_type = content_type
        self.content = content

    def as_dict(self):
        '''
        Checks if the content type is 'application/json' then returns a dict based on the content.
        '''
        if self.content_type == 'application/json':
            return json.loads(self.content)
        else:
            raise ValueError('Content-Type is not application/json: %s' % (self.content_type,))
