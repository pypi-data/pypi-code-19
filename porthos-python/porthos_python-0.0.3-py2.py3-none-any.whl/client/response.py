# -*- coding: utf-8 -*-
import json


class Response(object):
    '''
    Response of a client RPC call.
    '''
    def __init__(self, content_type, content, headers):
        self.content_type = content_type
        self.content = content
        self.headers = headers

    def as_dict(self):
        '''
        Checks if the content type is 'application/json' then returns a dict based on the content.
        '''
        if self.content_type == 'application/json':
            return json.loads(self.content)
        else:
            raise ValueError('Content-Type is not application/json: %s' % (self.content_type,))

    @property
    def status_code(self):
        if 'statusCode' in self.headers:
            return int(self.headers.get('statusCode'))

        raise InvalidResponseException('statusCode not present in response headers.')