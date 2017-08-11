# -*- coding: utf-8 -*-
import kombu

from .call import Call, TimeoutException
from .response import Response

__all__ = ['Client', 'TimeoutException']


class Client(object):
    def __init__(self, connection, service_name, default_timeout=60*1000):
        '''
        Creates a RPC client. Arguments:
            - connection: string (amqp connection url) or an object of kombu.Connection.
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

        self.producer = self.connection.Producer(routing_key=service_name, auto_declare=True)
        self.consumer = self.connection.Consumer(kombu.Queue(exclusive=True), callbacks=[self._on_response], auto_declare=True)
        self.response_queue = self.consumer.queues[0]

        self.consumer.consume()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _get_connection(self, amqp_url):
	   return kombu.Connection(amqp_url)

    def _on_response(self, content, message):
        if self.current_call:
            c_corr_id = self.current_call.corr_id
            m_corr_id = message.properties.get('correlation_id')

            self.current_call.correlation_match = c_corr_id == m_corr_id

            if self.current_call.correlation_match:
                message.ack()

                self.current_call.response = Response(message.content_type, content, message.headers)
                return

        message.requeue()

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
    	if self.external_connection:
    	    self.connection.close()

