# -*- coding: utf-8 -*-
import logging
import pika
import time

LOG_FORMAT = '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s'


class RabbitMQProducer(object):
    """
    This is a consumer class that will handle interactions
    with RabbitMQ.

    """

    def __init__(self, host, queue, exchange='input'):
        self.host = host
        self.queue = queue
        self.exchange = exchange
        self.channel = None
        self.connection = None
        self.initialize()
        self.counter = 0

    def publish_message(self, message, routing_key):
        """
        
        :param message: 
        :param routing_key:
        :return: 
        """
        self.channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=message)

    def publish_message_with_limit(self, message, routing_key, max_queue_size=100000):
        """

        :param message:
        :param routing_key:
        :param max_queue_size:
        :return:
        """
        if self.counter % 100 == 0:
            if max_queue_size <= self.check_queue_size():
                time.sleep(10)
                self.publish_message_with_limit(message, routing_key, max_queue_size)
            else:
                self.channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=message)
                self.counter += 1
        else:
            self.channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=message)
            self.counter += 1

    def initialize(self):
        """
        
        :return: 
        """
        logging.disable(30)
        self.connect_to_queue()

    def connect_to_queue(self):
        """
        Establishes a connection with RabbitMQ server, declares the queue where we will consume messages,
        runs a loop that listens for data and runs the callback functions whenever necessary
        :return: 
        """
        self.connection = pika.BlockingConnection(pika.URLParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def check_queue_size(self):
        """
        Checks the size of a queue
        :return: 
        """
        rabbit_queue = self.channel.queue_declare(queue=self.queue, durable=True, passive=True)
        return rabbit_queue.method.message_count

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                                reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)


host = 'amqp://er:er101@localhost:5672/entityresolution'
queue = 'er_out'

if __name__ == '__main__':
    consumer = RabbitMQProducer(host, queue)
    consumer.run()
