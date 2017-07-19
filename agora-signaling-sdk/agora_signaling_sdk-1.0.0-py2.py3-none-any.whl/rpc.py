# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


from __future__ import absolute_import

from agorasigsdk.web2_lbs import (format_websocket_url, query_lbs,
                                  get_web2_addresses)
from autobahn.twisted.websocket import (WebSocketClientFactory,
                                        WebSocketClientProtocol)
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory

import logging
import json
import os


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


# Indicate if do logging.
DO_LOG = False


class RPC(object):
    """Support Signalling Remote Procedure Call behaviors."""

    def __init__(self, appid, token, **kwargs):
        self.appid = appid
        self.token = token

        self.onCall = kwargs.get('onCall', None)
        self.onConnected = kwargs.get('onConnected', None)
        self.onEnd = kwargs.get('onEnd', None)
        self.onStart = kwargs.get('onStart', None)

        # Class variables.
        self.state = 'connecting'
        self.websocket = None


        # Connect to the websocket server.

        # Check if in debugging mode.
        is_debugging = os.getenv('AGORASDKDBG')
        if is_debugging:
            ap_url = os.getenv('AOGRAAP')
            lbs_url = os.getenv('AGORALBS')
            if ap_url:
                ip, port = ap_url.split(':')
                ws_url = format_websocket_url(ip, port)
                port = int(port)
                result = self.connect(ws_url, ip, port)
                if result == 'failure':
                    # In debugging mode, the program assumes both test server
                    # and network are working, developers should deal with
                    # any connection problems before proceeding further.
                    exit(1)
            elif lbs_url:
                lbs_access_points = query_lbs(self.appid, lbs_url)
                web2_servers = get_web2_addresses(lbs_access_points)
                result = self.call_connect(web2_servers)
                if result == 'failure':
                    # No meaning to keep running until troubleshooting is done.
                    exit(1)
            else:
                logger.error('Debugging mode env not set up properly.')
                exit(0)
        else:
            lbs_access_points = query_lbs(self.appid)
            web2_servers = get_web2_addresses(lbs_access_points)
            self.call_connect(web2_servers)

    def build_rpc_connection(self):
        data = {'appid': self.appid, 'token': self.token}
        self.send_message('connect', data)

    def call_connect(self, servers):
        """Call self.connect() until successful or servers are iterated."""
        if not servers:
            logger.error('No server provided.')
            return 'failure'

        servers = random.shuffle(servers)
        for server in servers:
            host = format_websocket_url(server.ip, server.port)
            result = self.connect(host, server.ip, server.port)
            if result == 'success':
                break
        else:
            logger.error('NET    No web2 websocket server is available.')

        return result

    def connect(self, url, ip, port):
        """Make a TCP connection to a server.
        Args:
            url (str): The web2 websocket server url.
            ip (str)
            port (int)

        Returns:
            result (str): Either 'success' or 'failure'.
        """
        result = 'success'

        try:
            factory = RPCClientFactory(rpc=self, url=url)
            #reactor.connectTCP('125.88.159.176', 8003, factory)
            reactor.connectTCP(ip, port , factory)
        except Exception as e:
            logger.exception('NET    Exception when connecting to server {0}'
                             .format(e))
            result = 'failure'
        finally:
            return result

    def close(self, error=''):
        if DO_LOG:
            logger.info('API    Closing a rpc session.')
        if self.state != 'closed':
            self.websocket.sendClose(code=1000)
            self.onEnd(error)

    def register(self, onCall, onStart=None, onFailed=None, onEnd=None,
                 **kwargs):
        """Register a RPC method."""
        self.onCall = onCall
        self.send_message('rpc_register', kwargs)

    def send_message(self, command, message):
        """
        Args:
            command (str): This string tells the server what to do.
            message: All kinds of types of messages to be sent.

        Returns:
            result (str): either `success` or `failure`.
        """
        result = 'failure'

        data = json.dumps([command, message]).encode('utf8')

        if DO_LOG:
            logger.info('NET    Sending message {0}'.format(data))

        try:
            self.websocket.sendMessage(data)
            result = 'success'
        except IOError:
            logger.exception('NET    Network error!')
        finally:
            return result

    def stop(self):
        """Stop RPC service while not closing the session."""
        result = self.send_message('rpc_stop', {})
        return result


class RPCClientProtocol(WebSocketClientProtocol):

    def __init__(self, rpc):
        """
        Args:
            rpc (RPC): A rpc session.
        """
        super(self.__class__, self).__init__()

        self.rpc = rpc

    def onConnect(self, response):
        if DO_LOG:
            logger.info('NET    Server connected: {0}'.format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        if DO_LOG:
            logger.info('NET    WebSocket connection open')
        self.rpc.websocket = self
        self.rpc.state = 'connected'

        self.rpc.build_rpc_connection()

    def onMessage(self, payload, isBinary=None):
        if DO_LOG:
            logger.info('NET    Received message {0}'
                    .format(payload.decode('utf8')))
        message = json.loads(payload.decode('utf8'))

        result, content = message[0], message[1]

        if result == 'connect_result':
            if content == '' and self.rpc.onConnected:
                self.rpc.onConnected(self.rpc)
        if result == 'rpc_register_result':
            if self.rpc.onStart:
                self.rpc.onStart(self.rpc)
        if result == 'rpc_invoke':
            if self.rpc.onCall:
                result = self.rpc.onCall(self.rpc, content)
                data = {'callid': content['callid'], 'ret': result}
                self.rpc.send_message('rpc_invoke_result', data)

    def onClose(self, wasClean, code, reason):
        if DO_LOG:
            logger.warning('NET    WebSocket connection closed: {0}, '
                           'wasClean? {1}; code is : {2}'
                           .format(reason, wasClean, code))
        self.rpc.state = 'closed'

        if DO_LOG:
            logger.info('NET    connection state: {0}'.format(self.rpc.state))


class RPCClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    def __init__(self, rpc, url):
        super(self.__class__, self).__init__(url)

        self.rpc = rpc

    def buildProtocol(self, addr):
        proto = RPCClientProtocol(self.rpc)
        proto.factory = self
        return proto

    def clientConnectionFailed(self, connector, reason):
        logger.error('NET     RPC session conenction failed .. retrying ..')
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        """Override the clientConnectionLost from ReconnectingClientFactory.
        We currently does not require reconnecting while losing connection.
        """
        pass
