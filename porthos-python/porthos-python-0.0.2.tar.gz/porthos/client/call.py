# -*- coding: utf-8 -*-
import json
import uuid

import pika


class TimeoutException(Exception):
    pass


class Call(object):
    def __init__(self, client, method_name, default_timeout):
        self.client = client
        self.corr_id = str(uuid.uuid4())
        self.method_name = method_name
        self.timeout = default_timeout
        self.body = None
        self.response = None
        self.content_type = 'application/octet-stream'

    def with_timeout(self, timeout):
        '''
        Sets a timeout for this call. In milliseconds.
        '''
    	self.timeout = timeout
    	return self

    def with_body(self, body):
        '''
        Sets the body of the request. The body argument should be a string or unicode.
        '''
        self.body = body
        self.content_type = 'application/octet-stream'
        return self

    def with_args(self, *args):
        '''
        Sets the body with the given args. The content-type will be application/json.
        '''
        self.body = json.dumps(args)
        self.content_type = 'application/json'
        return self

    def with_dict(self, d):
        '''
        Sets the body with the given dict. The content-type will be application/json.
        '''
        self.body = json.dumps(d)
        self.content_type = 'application/json'
        return self

    def sync(self):
        '''
        Performs a sync call to the remote service.
        Returns a Response object.
        '''
        self.client.channel.basic_publish(exchange='',
                                          routing_key=self.client.service_name,
                                          properties=pika.BasicProperties(
                                                content_type=self.content_type,
                                                headers={
                                                    "X-Method": self.method_name
                                                },
                                                reply_to = self.client.response_queue,
                                                correlation_id = self.corr_id,
                                                expiration=str(self.timeout)
                                                ),
                                          body=self.body)

        timeout_in_secods = self.timeout / 1000.0
        self.client.connection.process_data_events(time_limit=timeout_in_secods)

        if self.response is None:
            raise TimeoutException()

        return self.response

