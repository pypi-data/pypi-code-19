import json
import logging
import unittest
import xml.etree.cElementTree as etree

from cryptography.fernet import Fernet, InvalidToken
import responses
from requests import session  # noqa
from structlog import wrap_logger

from sdx.common.exceptions import BadMessageError, DecryptError, RetryableError
from sdx.common.queues import ResponseProcessor
from sdx.common.queues.test.test_data import test_data, test_secret
from sdx.common.logger_config import logger_initial_config


def encrypt(plain):
    f = Fernet(test_secret)
    return f.encrypt(plain.encode("utf-8"))


class MockResponse:
    def __init__(self, status):
        self.status_code = status
        self.url = ""


class TestResponseProcessor(unittest.TestCase):
    logger_initial_config(service_name=__name__,
                          log_level='DEBUG')

    logger = wrap_logger(logging.getLogger(__name__))

    invalid_processor = ResponseProcessor(logger, '', '', '', '')
    r = ResponseProcessor(logger, 'http://test', 'test', 'test', 'test')

    def test_init(self):
        self.assertEqual("", self.r.tx_id)

    def test_process_no_receipt_details(self):
        with self.assertRaises(BadMessageError):
            self.invalid_processor.process(encrypt(test_data['valid']), test_secret)

    def test_process_invalid_key(self):
        with self.assertRaises(DecryptError):
            with self.assertLogs(logger=__name__, level='ERROR') as cm:
                self.r.process(encrypt(test_data['valid']), "")

        msg = "ERROR:common.queues.test.test_response_processor:" + \
              "exception=ValueError('Fernet key must be 32 url-safe " + \
              "base64-encoded bytes.',) event='Exception decrypting message'"
        self.assertEqual(cm.output, [msg])

    @responses.activate
    def test_process_invalid_message(self):
        responses.add(responses.POST, "http://test/test", status=200)

        with self.assertRaises(DecryptError):
            with self.assertLogs(logger=__name__, level='ERROR') as cm:
                self.r.process("", test_secret)

        msg = "ERROR:common.queues.test.test_response_processor:" + \
              "exception=InvalidToken() event='Exception decrypting message'"
        self.assertEqual(cm.output, [msg])

        self.assertIs(self.r.process(encrypt(test_data['valid']), test_secret), None)

    def test_validate_invalid_data(self):
        with self.assertRaises(BadMessageError):
            self.r._validate(json.loads(test_data['invalid']))
        self.assertEqual(self.r.tx_id, "")

    def test_validate_missing_metadata(self):
        with self.assertRaises(BadMessageError):
            self.r._validate(json.loads(test_data['missing_metadata']))
            self.assertEqual(self.r.tx_id, "")

    def test_validate_missing_ru_ref(self):
        with self.assertRaises(BadMessageError):
            self.r._validate(json.loads(test_data['missing_ru_ref']))
            self.assertEqual(self.r.tx_id, "")

    def test_validate_valid_data(self):
        self.assertIs(self.r._validate(json.loads(test_data['valid'])), None)
        self.assertEqual(self.r.tx_id, "0f534ffc-9442-414c-b39f-a756b4adc6cb")

    def test_decrypt_with_bad_token(self):
        with self.assertRaises(InvalidToken):
            self.r._decrypt("xbxhsbhxbsahb", test_secret)

    def test_decrypt_with_good_token(self):
        token = encrypt(test_data['valid'])
        plain = self.r._decrypt(token, test_secret)
        self.assertEqual(json.loads(plain), json.loads(test_data['valid']))

    def test_with_invalid_metadata(self):
        with self.assertRaises(BadMessageError):
            self.r._encode({"bad": "thing"})

    def test_with_valid_data(self):
        self.r._encode(json.loads(test_data['valid']))


class TestSend(unittest.TestCase):
    logger = wrap_logger(logging.getLogger(__name__))
    processor = ResponseProcessor(logger, 'http://test', 'test', 'test', 'test')
    endpoint = processor._receipt_host + "/" + processor._receipt_path

    def setUp(self):
        self.decrypted = json.loads(test_data['valid'])
        self.xml = self.processor._encode(self.decrypted)

    @responses.activate
    def test_with_200_response(self):
        responses.add(responses.POST,
                      self.endpoint,
                      status=200)

        self.processor._send_receipt(self.decrypted, self.xml)

    @responses.activate
    def test_with_500_response(self):
        responses.add(responses.POST,
                      self.endpoint,
                      status=500)

        with self.assertRaises(RetryableError):
            self.processor._send_receipt(self.decrypted, self.xml)

    @responses.activate
    def test_with_400_response(self):
        responses.add(responses.POST,
                      self.endpoint,
                      status=400)

        with self.assertRaises(BadMessageError):
            self.processor._send_receipt(self.decrypted, self.xml)

    @responses.activate
    def test_with_404_response(self):
        """Test that a 404 response with no 1009 error in the response XMl continues
           execution assuming a transient error.
        """
        etree.register_namespace('', "http://ns.ons.gov.uk/namespaces/resources/error")
        file_path = 'sdx/common/queues/test/receipt_404.xml'
        tree = etree.parse(file_path)
        root = tree.getroot()
        tree_as_str = etree.tostring(root, encoding='utf-8')

        responses.add(responses.POST, self.endpoint,
                      body=tree_as_str, status=404,
                      content_type='application/xml')

        with self.assertRaises(RetryableError):
            resp = self.processor._send_receipt(self.decrypted, self.xml)  # noqa

    @responses.activate
    def test_with_404_1009_response(self):
        """Test that a 404 response with a 1009 error in the response XMl raises
           BadMessage error.
        """
        etree.register_namespace('', "http://ns.ons.gov.uk/namespaces/resources/error")
        file_path = 'sdx/common/queues/test/receipt_incorrect_ru_ce.xml'
        tree = etree.parse(file_path)
        root = tree.getroot()
        tree_as_str = etree.tostring(root, encoding='utf-8')

        responses.add(responses.POST,
                      self.endpoint,
                      body=tree_as_str,
                      status=404,
                      content_type='application/xml')

        with self.assertRaises(BadMessageError):
            resp = self.processor._send_receipt(self.decrypted, self.xml)  # noqa
