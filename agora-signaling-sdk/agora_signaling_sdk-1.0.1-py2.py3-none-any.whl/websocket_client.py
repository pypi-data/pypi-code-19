# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


from __future__ import absolute_import

from agorasigsdk.login_session_state import LoginSessionState
from agorasigsdk.message_details import MessageDetails
from agorasigsdk.signal_consts import LOGOUT_E_PACKET

from autobahn.twisted.websocket import (WebSocketClientFactory,
                                        WebSocketClientProtocol)
from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.protocol import ReconnectingClientFactory

import json
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


class ClientProtocol(WebSocketClientProtocol):

    def __init__(self, session=None):
        super(self.__class__, self).__init__()

        # callid is supposed to be a scheduled ping.
        self.callid = None

        self.session = session

        self.ping_interval = 10 # seconds
        self.ping_num = 0

        # The maximum pong back time from the server.
        # The time is ping_num_diff * ping_interval.
        self.ping_num_diff = 3

    def onConnect(self, response):
        logger.info('NET    {0}  Server connected: {1}'
                    .format(self.session.account, response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        if self.session.state != LoginSessionState.CONNECTING:
            return

        self.session.current_session = self

        def login():
            if self.session.state == LoginSessionState.CONNECTING:
                logger.info('NET    {0}  WebSocket connection open.'
                            .format(self.session.account))

                data = [
                    u'login',
                    {
                        u'account': self.session.account,
                        u'token': self.session.token,
                        u'vid': self.session.appid,
                        u'device': u'javasdk',
                        u'ip': u'',
                        u'uid': 0,
                        u'ver': 1010002000
                    }
                ]
                self.sendMessage(json.dumps(data).encode('utf8'))

                self.callid = self.factory.reactor.callLater(
                        self.ping_interval, self.ping)
                self.session.callid = self.callid

        login()

    def sleep(self, delay):
        d = Deferred()
        if self.session.state == LoginSessionState.LOGINED:
            self.callid = reactor.callLater(delay, d.callback, None)
            self.session.callid = self.callid
        return d

    @inlineCallbacks
    def ping(self):
        while True:
            if self.session.state == LoginSessionState.LOGINED:
                logger.info('NET    {0} Send a ping to server.'
                             .format(self.session.account))

                data = json.dumps([u'ping', self.ping_num]).encode('utf8')
                self.sendMessage(data)
                self.ping_num += 1
                yield self.sleep(self.ping_interval)
            else:
                break


    def onMessage(self, payload, isBinary=None):
        logger.info('NET    {0}  Received message {1}'
                    .format(self.session.account, payload.decode('utf8')))

        message, cmd = None, None
        try:
            message = json.loads(payload.decode('utf8'))
            cmd = message[0]
        except Exception as e:
            logger.exception('NET    {0}  {1}'.format(self.session.account, e))
            return

        if cmd == u'close':
            logger.warning('NET    {0}  Recieved close message from the server.'
                           .format(self.session.account))

            self.transport.loseConnection()

        if cmd == u'pong' and (self.ping_num - message[1]) > self.ping_num_diff:
            self.session.logout()

        if self.session.state == LoginSessionState.CONNECTING:
            args = message[1]
            error = args[0]
            try:
                ret_data = json.loads(args[1])
            except Exception as e:
                logger.exception('NET    {0}  {1}'
                                 .format(self.session.account, e))
                return

            if cmd != 'login_ret':
                # Unexpected result.
                return

            if error != '':
                # With error message.
                return

            if ret_data['result'] != 'ok':
                # TODO: handle error reults.
                pass

            line = ret_data['line']
            uid = ret_data['uid']
            self.session.fire_login_success(line, uid)
        elif self.session.state == LoginSessionState.LOGINED:
            # Only respond to some messages when the user loggeg in.
            if cmd == 'call2-ret':
                args = message[1]
                call_id = args[0]
                error = args[1]

                try:
                    ret_data = json.loads(args[2])
                except Exception as e:
                    logger.exception('NET    {0}  {1}'
                                     .format(self.session.account, e))
                    self.session.fire_logout(LOGOUT_E_PACKET)
                    return

                self.session.on_call_ret(call_id, error, ret_data)
            elif cmd == 'notify':
                if isinstance(message[1], list):
                    args = message[1]
                    msg_type = args[0]
                    if msg_type == 'channel2':
                        msg_id = args[2]
                        msg_details = MessageDetails(args[3])
                        msg_content = {}

                        try:
                            msg_content = json.loads(msg_details.msg_content)
                        except Exception as e:
                            logger.exception('NET    {0}  {1}'
                                             .format(self.session.account, e))
                            self.session.fire_logout(LOGOUT_E_PACKET)
                            return

                        # Basic properties for a channel interaction
                        channel = msg_content['channel']
                        account = msg_content['account']
                        uid = msg_content['uid']

                        if msg_details.msg_type == 'channel_msg':
                            msg = msg_content['msg']

                            logger.info('APICB  {0}  Calling '\
                                        'on_msg_channel_received.'
                                        .format(self.session.account))

                            self.session.last_channel.cb \
                                .on_msg_channel_received(
                                    self.session, self.session.last_channel,
                                    account, uid, msg)
                        elif msg_details.msg_type == 'channel_user_join':

                            logger.info('APICB  {0}  Calling '\
                                        'on_channel_user_joined.'
                                        .format(self.session.account))

                            self.session.last_channel.cb \
                                .on_channel_user_joined(
                                    self.session, self.session.last_channel,
                                    account, uid)
                        elif msg_details.msg_type == 'channel_user_leave':

                            logger.info('APICB  {0}  Calling '\
                                        'on_channel_user_left.'
                                        .format(self.session.account))

                            self.session.last_channel.cb \
                                .on_channel_user_left(
                                    self.session, self.session.last_channel,
                                    account, uid)
                        elif msg_details.msg_type == 'channel_attr_update':
                            name = msg_content['name']
                            t = msg_content['type']
                            value = msg_content['value']

                            logger.info('APICB  {0}  Calling '\
                                        'on_channel_user_list.'
                                        .format(self.session.account))

                            self.session.last_channel.cb \
                                .on_channel_attr_updated(
                                    self.session, self.session.last_channel,
                                    name, value, t)

                    elif msg_type == 'msg':
                        # Get the msessage version number and pull messages.
                        self.session.m_ver_notify = args[1]
                        self.session.schedule_poll()
                else:
                    body = message[1].split(' ', 3)
                    if body[1] == 'recvmsg':
                        try:
                            details_json = json.dumps(body[2]).encode('utf8')
                        except Exception as e:
                            logger.exception('NET    {0}  {1}'
                                             .format(self.session.account, e))
                            self.session.fire_logout(LOGOUT_E_PACKET)
                            return

                        version = details_json[0]
                        if version == self.session.m_ver_clear + 1:
                            self.session.inst_msgs.append(
                                MessageDetails(details_json[1]))
                            self.session.m_ver_clear = version
                            self.session.schedule_poll_tail()
                        else:
                            self.session.m_ver_notify = version
                            self.session.schedule_poll()

                        self.session.process_inst_msgs()

    def onClose(self, wasClean, code, reason):
        logger.warning('NET    {0}  WebSocket connection closed: {1}, \
                        wasClean? {2}; code is : {3}'
                        .format(self.session.account, reason, wasClean, code))

        if self.session.state != LoginSessionState.LOGOUT:
            self.session.state = LoginSessionState.LOGOUT


class ClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    def __init__(self, session, url):
        """
        Args:
            session: A LoginSession instance.
            url: The server url.
        """
        super(self.__class__, self).__init__(url)
        self.session = session

    def buildProtocol(self, addr):
        """Override the WebSocketClientFactory's buildProtocol to customize
        a client protocol.
        """
        proto = ClientProtocol(self.session)
        proto.factory = self
        return proto

    def clientConnectionFailed(self, connector, reason):
        if self.session.state == LoginSessionState.CONNECTING or \
            self.session.state == LoginSessionState.LOGINED:
            logger.error('{0}  Client connection failed .. retrying ..'
                         .format(self.session.account))
            self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        if self.session.state == LoginSessionState.CONNECTING or \
            self.session.state == LoginSessionState.LOGINED:
            #logger.info('{0}  Client connection lost .. retrying ..'
            #            .format(self.session.account))
            pass
            #self.retry(connector)
