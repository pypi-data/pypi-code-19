import json
import logging
import unittest
from unittest.mock import patch

from sdc.rabbit import AsyncConsumer, MessageConsumer


class DotDict(dict):

    __getattr__ = dict.get


class TestConsumer(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        self.consumer = AsyncConsumer(True, '/', 'test', 'test', ['http://test/test'])
        self.message_consumer = MessageConsumer(self.consumer, lambda x: True)

        self.props = DotDict({'headers': {'tx_id': 'test',
                                          'x-delivery-count': 0}})
        self.props_no_tx_id = DotDict({'headers': {'x-delivery-count': 0}})
        self.props_no_x_delivery_count = DotDict({'headers': {'tx_id': 'test'}})
        self.basic_deliver = DotDict({'delivery_tag': 'test'})
        self.body = json.loads('"{test message}"')

    def test_queue_attributes(self):

        self.assertEqual(self.message_consumer._consumer._exchange, '/')
        self.assertEqual(self.message_consumer._consumer._exchange_type, 'test')
        self.assertEqual(self.message_consumer._consumer._queue, 'test')
        self.assertEqual(self.message_consumer._consumer._rabbit_urls, ['http://test/test'])
        self.assertEqual(self.message_consumer._consumer._durable_queue, True)

        self.assertEqual(self.message_consumer._quarantine_publisher._queue,
                         'async_consumer_quarantine')
        self.assertEqual(self.message_consumer._quarantine_publisher._urls,
                         ['http://test/test'])

    def test_tx_id(self):
        self.assertEqual('test', self.message_consumer.tx_id(self.props))

        with self.assertRaises(KeyError):
            self.message_consumer.tx_id(self.props_no_tx_id)

    def test_delivery_count(self):
        count = self.message_consumer.delivery_count(self.props)
        self.assertEqual(count, 1)

    def test_delivery_count_no_header(self):
        with self.assertRaises(KeyError):
            self.message_consumer.delivery_count(
                self.props_no_x_delivery_count)

    @patch.object(AsyncConsumer, 'nack_message')
    def test_on_message_retryable_error(self, mock_consumer):
        with self.assertLogs(logger=__name__, level='ERROR') as cm:
            r = self.message_consumer.on_message(self.basic_deliver,
                                                 self.props,
                                                 self.body.encode())
            self.assertEqual(r, None)

        msg = "'Failed to process"
        self.assertIn(msg, cm.output[0])

    @patch.object(AsyncConsumer, 'reject_message')
    def test_on_message_decrypt_error(self, mock_consumer):
        with self.assertLogs(logger=__name__, level='ERROR') as cm:
            r = self.message_consumer.on_message(self.basic_deliver,
                                                 self.props,
                                                 self.body.encode())
            self.assertEqual(r, None)

        msg = "'Bad decrypt"
        self.assertNotEqual(msg, cm.output[0])

    @patch.object(AsyncConsumer, 'reject_message')
    def test_on_message_badmessage_error(self, mock_consumer):
        with self.assertLogs(logger=__name__, level='ERROR') as cm:
            r = self.message_consumer.on_message(self.basic_deliver,
                                                 self.props,
                                                 self.body.encode())
            self.assertEqual(r, None)

        msg = "'Bad message'"
        self.assertNotEqual(msg, cm.output[0])
