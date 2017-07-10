# -*- coding: utf-8 -*-
import datetime

import mock
from mock import MagicMock, Mock, patch
from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientFactory
from twisted.test import proto_helpers
from twisted.trial import unittest

from maranet.constructs.structs import MaraFrame
from maranet.protocols.client import MaraClientProtocol, MaraPorotocolFactory

from .mocks import COMasterMock

class BaseTestProtocol(unittest.TestCase):

    def setUp(self):
        self.comaster = COMasterMock()

def getStopPollInlineCalllback(stopping_action):
    """
    Utility function to stop client mainLoop
    """
    @defer.inlineCallbacks
    def stopPolling(*args, **kwargs):
        '''Generic inlineCallback that stop reactor'''
        stopping_action()
        yield ''
    return stopPolling

class TestProtocolPeh(BaseTestProtocol):
    @defer.inlineCallbacks
    def test_send_peh_upon_connection(self):
        '''To test client protocol we isloate it from the ClientFactory'''
        with patch.object(datetime, 'datetime', Mock(wraps=datetime.datetime)) as patched:
            fixed_date = datetime.datetime(2014, 1, 1, 12, 0, 0)
            patched.now.return_value = fixed_date

            factory = ClientFactory()
            factory.comaster = self.comaster

            factory.protocol = MaraClientProtocol
            proto = factory.buildProtocol(('127.0.0.1', 0))
            proto.construct = MaraFrame

            transport = proto_helpers.StringTransport()
            proto.makeConnection(transport)
            proto.doPoll = getStopPollInlineCalllback(transport.loseConnection)

            yield proto.mainLoop()
            bytes_sent_to_device = transport.value()
            assert len(bytes_sent_to_device)
            result = MaraFrame.parse(bytes_sent_to_device)
            self.assertEqual(result.dest, 0xFF)
            self.assertEqual(result.source, 2)

            # We don't need to check BCC since it's already coded into MaraFrame
            assert result.peh == fixed_date

class TestPrtocolFactory(unittest.TestCase):
    def setUp(self):
        self.comaster = COMasterMock()
        self.factory = MaraPorotocolFactory(self.comaster)

    # @mock.patch('maranet.mara.client.base.get_settings')
    def test_protocol_holds_reference_to_factory(self):
        protocol = self.factory.buildProtocol(('127.0.0.1', 0))
        self.assertEqual(protocol.factory, self.factory)

    def test_protocol_holds_reference_to_comaster(self):
        protocol = self.factory.buildProtocol(('127.0.0.1', 0))
        self.assertEqual(protocol.comaster, self.comaster)
