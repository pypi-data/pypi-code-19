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
import random


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


# Indicate if do logging.
DO_LOG = False


class Channel2(object):
    """Channel class version 2 which supports anonymous login, topics, states,
    and more message types.
    """

    def __init__(self, appid, channelName, channelAttrs={},
                 failWhenExists=False, needState=False, simpleHost={},
                 topicsToSubscribe=[], userId='', userInfo={}, onJoin=None,
                 onJoinFailed=None, onLeave=None, onMessage=None):
        if userId == '':
            # userId is default to be 13-digit string.
            userId = str(random.randint(1000000000000, 1999999999999))


        # Necessary parameters for a channel.
        self.appid = appid
        self.channelName = channelName
        self.channelAttrs = channelAttrs
        self.failWhenExists = failWhenExists
        self.needState = needState
        self.simpleHost = simpleHost
        self.topicsToSubscribe = topicsToSubscribe
        self.userId = userId
        self.userInfo = userInfo
        self.onMessage = onMessage
        self.onJoin = onJoin
        self.onJoinFailed = onJoinFailed
        self.onLeave = onLeave


        # Class variables.
        self.n_ping = 0
        self.ping_interval = 10000
        self.ping_timeout = 10000
        self.n_pong = 0
        self.q_sending = {}
        self.msgid = 0
        self.q_calling = {}
        self.callid = 0
        self.state = 'connecting'
        self.websocket = None


        # Topic subscription indicators.
        self.is_joined = False
        self.is_left = False


        # Connect to the websocket server.

        # Check if in debugging mode.
        is_debugging = os.getenv('AGORASDKDBG')
        if is_debugging == 'True':
            ap_url = os.getenv('AGORAAP')
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
                    logger.error('Debugging mode env not set up properly.')
                    exit(1)
            elif lbs_url:
                lbs_access_points = query_lbs(self.appid, lbs_url)
                web2_servers = get_web2_addresses(lbs_access_points)
                result = self.call_connect(web2_servers)
                if result == 'failure':
                    # No meaning to keep running until troubleshooting is done.
                    logger.error('Debugging mode env not set up properly.')
                    exit(1)
            else:
                logger.error('Debugging mode env not set up properly.')
                exit(0)
        else:
            lbs_access_points = query_lbs(self.appid)
            web2_servers = get_web2_addresses(lbs_access_points)
            self.call_connect(web2_servers)

    def call(self, name, args, onSuccess=None, onFailed=None):
        """
        Args:
            name (str): The remote procedure name.
            args (dict): Arguments to be passed to the remote procedure.
            onSuccess (func): A callback function.
            onFailed (func): A callback function.
        """
        self.callid += 1
        data = {
            'functionName': name,
            'args': args,
            'callid': self.callid
        }

        send_msg_result = self.send_msg('rpc_call', data)

        self.q_calling[self.callid] = {
            'functionName': name,
            'args': args,
            'callid': self.callid,
            'onSuccess': onSuccess,
            'onFailed': onFailed
        }

        return send_msg_result

    def send(self, t, msg, topic, onSuccess=None, onFailed=None, noack=None):
        """
        Args:
            t (str): The message type.
            msg (str / dict / list): The message content.
            topic (str): The topic in this channel.
            onSuccess (func): A callback function.
            onFailed (func): A callback function.
            noack (bool): Indicate if there should be an acknowledgement.
        """
        self.msgid += 1
        args = {
            't': t,
            'msg': msg,
            'to': topic,
            'msgid': self.msgid
        }

        if noack is None:
            # noack is False if neither successful result nor
            # failed result needed.
            noack = (onSuccess == None and onFailed == None)

        args['noack'] = noack

        send_msg_result = self.send_msg('send', args)

        self.q_sending[self.msgid] = {'t': t, 'msg': msg,
                                      'onSuccess': onSuccess,
                                      'onFailed': onFailed}

        return send_msg_result

    def send_msg(self, command, message):
        """
        Args:
            command (str): Such as `sub`, `unsub`, `send` etc.
            message (str / dict / list): The message content.

        Returns:
            result (str): Either `success` or `failure`.
        """
        result = 'success'

        data = json.dumps([command, message]).encode('utf8')

        if DO_LOG:
            logger.info('NET    {0}  Sending message {1}'.format(self.userId, data))

        try:
            self.websocket.sendMessage(data)
        except IOError:
            logger.exception('NET    {0}  Network error!'.format(self.userId))
            result = 'failure'
        finally:
            return result

    def sub(self, topics):
        """Subscribe a topic in a channel.

        Args:
            topics (list of str): A list of topic(s) in the channel.
        """
        if DO_LOG:
            logger.info('API    {0}  Subscribing to topics {1}'
                        .format(self.userId, topics))

        if not isinstance(topics, list):
            raise TypeError('topics should be a list of strings')

        args = {
            'topics': topics,
            'userId': self.userId,
        }
        send_msg_result = self.send_msg('sub', args)

        return send_msg_result

    def unsub(self, topics):
        """Unsubscribe from a topic.

        Args:
            topic (list of str): A list of topic(s) in the channel.
        """
        if DO_LOG:
            logger.info('API    {0}  Subscribing from topic {1}'
                        .format(self.userId, topics))

        if not isinstance(topics, list):
            raise TypeError('topics should be a list of strings')

        args = {
            'topics': topics,
            'userId': self.userId,
        }
        send_msg_result = self.send_msg('unsub', args)

        return send_msg_result

    def leave(self, error=''):
        if DO_LOG:
            logger.info('API    {0}  Leaving the channel2 {1}'
                    .format(self.userId, self.channelName))
        if not self.is_left:
            self.is_left = True
            if self.onLeave:
                if DO_LOG:
                    logger.info('APICB  {0} Calling channel2.onLeave()'
                                .format(self.userId))
                self.onLeave(error)
            if self.state != 'closed':
                self.websocket.sendClose(code=1000)

    def call_connect(self, servers):
        """Call self.connect() until successful or servers are iterated."""
        if not servers:
            logger.error('No server provided.')
            return 'failure'

        random.shuffle(servers)
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
            factory = Channel2ClientFactory(channel2=self, url=url)
            #reactor.connectTCP('125.88.159.176', 8003, factory)
            reactor.connectTCP(ip, port, factory)
        except Exception as e:
            logger.exception('NET    Exception when connecting to server {0}'
                             .format(e))
            result = 'failure'
        finally:
            return result


class Channel2ClientProtocol(WebSocketClientProtocol):

    def __init__(self, channel2):
        """
        Args:
            channel2 (Channel2): A Channel2 instance.
        """
        super(self.__class__, self).__init__()

        self.channel2 = channel2

    def onConnect(self, response):
        if DO_LOG:
            logger.info('NET    {0}  Server connected: {1}'
                        .format(self.channel2.userId, response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        if DO_LOG:
            logger.info('NET    {0}  WebSocket connection open'
                        .format(self.channel2.userId))
        self.channel2.websocket = self

        data = {
            'channelName': self.channel2.channelName,
            'userId': self.channel2.userId,
            'userInfo': self.channel2.userInfo,
            'topicsToSubscribe': self.channel2.topicsToSubscribe,
            'simpleHost': self.channel2.simpleHost,
            'channelAttrs': self.channel2.channelAttrs
        }

        self.channel2.send_msg('join', data)
        self.channel2.state = 'connected'

    def onMessage(self, payload, isBinary=None):
        if DO_LOG:
            logger.info('NET    {0}  Received message {1}'
                        .format(self.channel2.userId, payload.decode('utf8')))
        message = payload.decode('utf8')
        x = json.loads(message)
        name = x[0]

        if name == 'joined':
            self.channel2.is_joined = True
            if self.channel2.onJoin:
                if DO_LOG:
                    logger.info('APICB  {0}  Calling channel2.onJoin().'
                                .format(self.channel2.userId))
                self.channel2.onJoin(self.channel2)
        elif name == 'join_failed':
            if self.channel2.onJoinFailed:
                if DO_LOG:
                    logger.info('APICB  {0} Calling channel2.onJoinFailed().'
                                .format(self.channel2.userId))
                self.channel2.onJoinFailed(self.channel2, 0, x[1])
        elif name == 'send_ret':
            msgid = x[1]['msgid']
            err = x[1]['err']

            if msgid in self.channel2.q_sending:
                m = self.channel2.q_sending[msgid]

                if err:
                    if m['onFailed']:
                        if DO_LOG:
                            logger.info('APICB  {0}  Calling '
                                        'channel2.onFailed()'
                                        .format(self.channel2.userId))
                        m['onFailed'](err)
                else:
                    if m['onSuccess']:
                        if DO_LOG:
                            logger.info('APICB  {0}  Calling '
                                        'channel2.onSuccess()'
                                        .format(self.channel2.userId))
                        m['onSuccess']

                del self.channel2.q_sending[msgid]
        elif name == 'call_ret':
            callid = x[1]['callid']
            err = x[1]['err']

            if callid in self.channel2.q_calling:
                m = self.channel2.q_calling[callid]

                if err:
                    if m['onFailed']:
                        if DO_LOG:
                            logger.info('APICB  {0}  Calling '
                                        'channel2.onFailed()'
                                        .format(self.channel2.userId))
                        m['onFailed'](err)
                else:
                    if m['onSuccess']:
                        if DO_LOG:
                            logger.info('APICB  {0}  Calling '
                                        'channel2.onSuccess()'
                                        .format(self.channel2.userId))
                        m['onSuccess'](x[1]['ret'])

                del self.channel2.q_calling[callid]
        elif name == 'rpc_call_result':
            callid = x[1]['callid']
            ret = x[1]['ret']
            message = self.channel2.q_calling.get(callid, None)
            if message:
                if message['onSuccess']:
                    if DO_LOG:
                        logger.info('APICB  {0}  Calling rpc_call_result '
                                    'onSuccess()'.format(self.channel2.userId))
                    message['onSuccess'](self.channel2, ret, x[1]['callid'])
                elif message['onFailed']:
                    if DO_LOG:
                        logger.info('APICB  {0}  Calling rpc_call_result '
                                    'onFailed()'.format(self.channel2.userId))
                    message['onFailed'](self.channel2, ret)
        elif name == 'on_msg':
            if self.channel2.onMessage:
                # Parameters are channel2, message type, and message.
                if DO_LOG:
                    logger.info('APICB  {0}  Calliing channel2.onMessage'
                                .format(self.channel2.userId))
                self.channel2.onMessage(self.channel2, x[1][0], x[1][1])
        elif name == 'pong':
            self.channel2.n_pong = x[1]['n']

    def onClose(self, wasClean, code, reason):
        if DO_LOG:
            logger.warning('NET    {3}  WebSocket connection closed: {0}, '
                           'wasClean? {1}; code is : {2}'
                           .format(reason, wasClean, code,
                                   self.channel2.userId))
        self.channel2.state = 'closed'

        if DO_LOG:
            logger.info('NET    {0}  connection state: {1}'
                        .format(self.channel2.userId, self.channel2.state))


class Channel2ClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    def __init__(self, channel2, url):
        super(self.__class__, self).__init__(url)

        self.channel2 = channel2

    def buildProtocol(self, addr):
        proto = Channel2ClientProtocol(self.channel2)
        proto.factory = self
        return proto

    def clientConnectionFailed(self, connector, reason):
        logger.error('NET     {0}  Channel2 conenction failed with reason {1} '
                     '.. retrying ..'.format(self.channel2.userId, reason))
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        """Override the clientConnectionLost from ReconnectingClientFactory.
        We currently does not require reconnecting while losing connection.
        """
        pass
