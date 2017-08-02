# -*- coding: utf-8 -*-
import logging
import pika

LOG_FORMAT = '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s'
LOGGER = logging.getLogger(__name__)


def on_message(channel, method_frame, header_frame, body):
    """
    Contains actions performed once the message is received from RabbitMQ
    :param channel: 
    :param method_frame: 
    :param header_frame: 
    :param body: 
    :return: 
    """
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


class RabbitMQConsumer(object):
    """
    This is a consumer class that will handle interactions
    with RabbitMQ.

    """

    def __init__(self, host, queue, f):
        self.host = host
        self.queue = queue
        self.channel = None
        self.connection = None
        self.function = f

    def run(self):
        """
        Runs the class with logging
        :return: 
        """
        logging.disable(30)
        self.connect_to_queue()
        self.consume_messages()

    def connect_to_queue(self):
        """
        Establishes a connection with RabbitMQ server, declares the queue where we will consume messages,
        runs a loop that listens for data and runs the callback functions whenever necessary
        :return: 
        """
        self.connection = pika.BlockingConnection(pika.URLParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=10)

    def consume_messages(self):
        """
        Consumes messages given by RabbitMQ
        :return: 
        """
        self.channel.basic_consume(self.function, self.queue)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        self.connection.close()


# Remote
host = 'amqp://er:er101@rabbit-mq.scraping-cloud.joberate.com:5672/entityresolution'
# Local
host = 'amqp://er:er101@localhost:5672/entityresolution'
queue = 'er_in'


if __name__ == '__main__':
    consumer = RabbitMQConsumer(host, queue, on_message)
    consumer.run()
