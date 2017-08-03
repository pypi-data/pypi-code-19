# -*- coding: utf-8 -*-
import pika

from .call import Call, TimeoutException
from .response import Response

__all__ = ['Client', 'TimeoutException']


class Client(object):
    def __init__(self, connection, service_name, default_timeout=60*1000):
        '''
        Creates a RPC client. Arguments:
            - connection: string (amqp connection url) or an object ofpika.BlockingConnection.
            - service_name: the name of the service that holds the methods will intend to call.
            - default_timeout: default timeout of the remote calls.
        '''
        self.service_name = service_name
        self.default_timeout = default_timeout
        self.current_call = None

        if type(connection) == str:
            self.external_connection = False
            self.connection = self._get_connection(connection)
        else:
            self.external_connection = True
            self.connection = connection

        self.channel = self.connection.channel()
        self.response_queue = self.channel.queue_declare(exclusive=True).method.queue
        self.channel.basic_consume(self._on_response, no_ack=True, queue=self.response_queue)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _get_connection(self, amqp_url):
	return pika.BlockingConnection(pika.URLParameters(amqp_url))

    def _on_response(self, ch, method, props, content):
        if self.current_call and self.current_call.corr_id == props.correlation_id:
            self.current_call.response = Response(props.content_type, content)

    def call(self, method_name):
        '''
        Bulds the remote call with the given method_name.
        '''
    	self.current_call = Call(self, method_name, self.default_timeout)
    	return self.current_call

    def close(self):
        '''
        Close the resources allocated by this client.
        '''
    	self.channel.close()

    	if self.external_connection:
    	    self.connection.close()

