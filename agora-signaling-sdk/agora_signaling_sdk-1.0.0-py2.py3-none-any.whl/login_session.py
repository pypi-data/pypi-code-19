# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


from __future__ import print_function, absolute_import

from agorasigsdk.call import Call
from agorasigsdk.channel import Channel
from agorasigsdk.login_session_state import LoginSessionState
from agorasigsdk.message_details import MessageDetails
from agorasigsdk.server_address import ServerAddress
from agorasigsdk.signal_consts import (LOGOUT_E_NET, LOGOUT_E_PACKET,
                                       LOGOUT_E_USER, INVITE_E_OTHER,
                                       SENDMESSAGE_E_OTHER)
from agorasigsdk.websocket_client import ClientFactory

from random import randint
from twisted.internet import reactor

import json
import logging
import requests
import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


class LoginSession(object):
    """ login session class for user to perform multiple bahaviors"""
    CFG_LBS_N_RETRY = 10

    def __init__(self, account, appid, token, cb, is_debugging=False, debug_params=[]):
        self.servers = []

        self.account = account
        self.appid = appid
        self.token = token
        self.cb = cb

        # scheduled ping callid that could be canceled when logging out.
        self.callid = None

        # Indicate if the session is in debugging mode.
        if is_debugging:
            self.__set_debug(*debug_params)
            self.is_debugging = True
        else:
            self.is_debugging = False

        self.call_id = 0
        self.call_obj_table = {}
        self.call_table = {}
        self.current_session = None

        # A list of instances of MessageDetails.
        self.inst_msgs = []

        self.line = ''

        # Indicate if we are polling messages.
        self.m_is_polling = False

        # Last poll time.
        self.m_time_poll_last = 0

        self.m_last_active_time = 0

        # The version of a message.
        self.m_ver_ack = 0
        self.m_ver_clear = 0
        self.m_ver_notify = 0
        self.state = LoginSessionState.INIT

        # One user is currently restricted to join one channel at one time,
        # last_channel is the channel that user joined.
        self.last_channel = None

        self.__connect()

    def __set_debug(self, ip):
        """Restrict loging session behaviors for debugging purposes."""
        self.servers.append(ServerAddress(ip[0], ip[1]))

    def bc_call(self, func_str, arg_str, cb):
        """For broadcast purpose."""
        if not self.line:
            raise ValueError("Login session's user line is empty.")

        args = {
            u'line': self.line,
            u'package': 'io.agora.media.bc',
            u'func': func_str,
            u'args': arg_str,
            u'callid': '',
        }

        def on_result(error, ret_data, cb):
            """
            Args:
                error (int): Error code.
                ret_data (dict): Returned data.
                cb (func): A callback function.
            """
            e = ''
            r = ''
            if error != '' or ret_data['result'] != 'ok':
                e = error or ret_data['reason']
            else:
                r = ret_data['ret']
            logger.info('APICB  {0} Calling user_ext_call.'
                        .format(self.account))
            cb(e, r)

        params = [cb]
        self.call2(u'user_ext_call', args, (on_result, params))

    def call2(self, func_str, args, cb_pack=None):
        """Send requests and do callbacks when necessary.

        Args:
            func_str (str): A function string in request.
            args (dict): All necessary values.
            cb_pack: A on_result function with parameters to be called back
                     in self.on_call_ret().
        """
        self.send_cmd(self.req_to_json(func_str, args, cb_pack))

    def channel_join(self, name, cb=None):
        """Join a channel.

        Args:
            name (str): The channel name.
            cb: A ChannelCallback class.
        """
        logger.info('API    {0}  Calling channel_join.'.format(self.account))

        # Keep the channel callback if no new channel callback passed in.
        if not cb and self.last_channel:
            cb = self.last_channel.cb

        self.last_channel = Channel(self, name, cb)
        return self.last_channel

    def channel_invite_user_2(self, channel, peer, extra, cb):
        """Invite a user to a channel.

        Args:
            channel (str): The channel name.
            peer (str): The invited peer.
            extra (str): A json body string that contains extra messages.
            cb: A Call.Callback instance.

        Returns:
            A Call instance.
        """
        logger.info('API    {0}  Inviting user {1}.'
                    .format(self.account, peer))
        last_call = Call(channel, peer, 0, extra, self)
        last_call.set_callback(cb)

        args = {
            u'line': self.line,
            u'channelName': channel,
            u'peer': peer,
            u'extra': extra
        }

        def on_result(error, ret_data, last_call, session):
            """
            Args:
                error (int): Error code.
                ret_data (dict): Returned data.
                call_cb: A CallCallback instance.
                last_call: A Call instance.
                session: A LoginSession instance.
            """
            if error != '' or ret_data['result'] != 'ok':

                logger.info('APICB  {0} Calling on_invite_failed.'
                            .format(self.account))

                last_call.cb.on_invite_failed(
                    session, last_call, INVITE_E_OTHER)
                return

        params = [last_call, self]
        self.call2(u'voip_invite', args, (on_result, params))

        return last_call

    def fire_login_success(self, line, uid):
        if self.state == LoginSessionState.CONNECTING:
            self.state = LoginSessionState.LOGINED
            logger.debug('DEBUG  {0}  logged in.'.format(self.account))
        self.line = line
        self.uid = uid

        logger.info('APICB  {0}  is calling on_login_success'
                    .format(self.account))

        self.cb.on_login_success(self, uid)
        self.schedule_poll()

    def fire_logout(self, err_code):
        logger.info('NET    {0}  is firing logout.'.format(self.account))

        # Cancel scheduled ping.
        if self.callid:
            self.callid.cancel()

        if self.state != LoginSessionState.LOGOUT:
            self.state = LoginSessionState.LOGOUT

            logger.info('APICB  {0}  is calling on_logout'
                        .format(self.account))

            self.cb.on_logout(self, err_code)
            self.current_session = None
            logger.debug('NET    {0}  logged out.'.format(self.account))
        else:
            return

    def get_server_url(self):
        """Randomly pick a server and translate it into a url.

        Return a tuple that includes the host url and a ServerAddress object.
        """
        if not self.servers:
            return (None, None)
        random_idx = randint(0, len(self.servers) - 1)
        server = self.servers[random_idx]
        host = u'ws://%s-sig-web.agora.io:%d/' % (
                        server.ip.replace('.', '-'), server.port)
        logger.info('NET  {0}  The host url is {1}'.format(self.account, host))
        return (host, server)

    def get_time_in_ms(self):
        """Return the current time in milli seconds."""
        return int(round(time.time() * 1000))

    def logout(self):
        logger.info('API    {0}  logging out.'.format(self.account))
        self.schedule_poll()

        def on_result(error, ret_data, session):
            session.fire_logout(LOGOUT_E_USER)

        args = {u'line': self.line}
        params = [self]
        self.call2(u'user_logout', args, (on_result, params))

    def msg_instant_send(self, account, msg, cb, ttl=2592000):
        logger.info('API    {0}  Calling msg_instant_send. '
                    'Sending message to {0}'.format(self.account, account))

        if not cb or not isinstance(cb, LoginSession.MessageCallback):
            cb = self.MessageCallback()

        def on_result(error, ret_data, cb, session):
            if error == u'' and ret_data[u'result'] == u'ok':
                logger.info('APICB  {0}  Calling on_msg_send_success,'
                            .format(session.account))

                cb.on_msg_send_success(self)
            else:
                logger.info('APICB  {0}  Calling on_msg_send_error, '
                            'error code {1}.'
                            .format(session.account, error))
                cb.on_msg_send_error(session, SENDMESSAGE_E_OTHER)

        args = {
            u'line': self.line,
            u'peer': account,
            u'flag': u'v1:E:{0}'.format(ttl),
            u't': u'instant',
            u'content': msg
        }

        params = [cb, self]
        self.call2(u'user_sendmsg', args, (on_result, params))

    def on_call_ret(self, call_id, error, ret_data):
        logger.debug('DEBUG  {0}  Calling on_call_ret() to consume call_table'
                    .format(self.account))
        if call_id in self.call_table:
            logger.debug('DEBUG  {0}  Consume request {1}'
                        .format(self.account, self.call_table[call_id]))
            req = self.call_table[call_id]
            del self.call_table[call_id]
            if req['cb_pack']:
                cb, args = req['cb_pack']
                cb(error, ret_data, *args)

    def process_inst_msgs(self):
        """Process a list of MessageDetails instances,
        and delete all processed messages when finished.
        """
        for msg in self.inst_msgs:
            self.process_msg(msg)

        self.inst_msgs[:] = []

    def process_msg(self, msg):
        if self.state != LoginSessionState.LOGINED:
            logger.error('ERROR  {0}  Can not process a message '\
                         'without logging in.'
                         .format(self.account))
            return
        if msg.msg_type == 'instant':
            logger.info('APICB  {0}  Calling on_msg_instant_received.'
                        .format(self.account))

            self.cb.on_msg_instant_received(self, msg.msg_src,
                                            0, msg.msg_content)
        if msg.msg_type.startswith('voip_'):
            try:
                content = json.loads(msg.msg_content)
            except Exception as e:
                logger.exception('NET    {0}  {1}'.format(self.account, e))
                self.fire_logout(LOGOUT_E_PACKET)
                return

            channel = content['channel']
            peer = content['peer']
            extra = content['extra']
            peeruid = content['peeruid']
            if msg.msg_type == 'voip_invite':
                call = Call(channel, peer, peeruid, extra, self)
                args = {
                    u'line': self.line,
                    u'channelName': channel,
                    u'extra': u'',
                    u'peer': peer
                }
                self.call2(u'voip_invite_ack', args)
            else:
                call = self.call_obj_table[channel + peer]
                if not call:
                    return
            if msg.msg_type == 'voip_invite':
                logger.info('APICB  {0}  is calling on_invite_received.'
                            .format(self.account))

                self.cb.on_invite_received(self, call)
            elif msg.msg_type == 'voip_invite_ack':
                logger.info('APICB  {0}  is calling on_invite_end_by_peer.'
                            .format(self.account))

                call.cb.on_invite_received_by_peer(self, call)
            elif msg.msg_type == 'voip_invite_accept':
                logger.info('APICB  {0}  is calling on_invite_accepted_by_peer.'
                            .format(self.account))

                call.cb.on_invite_accepted_by_peer(self, call, extra)
            elif msg.msg_type == 'voip_invite_refuse':
                logger.info('APICB  {0}  is calling on_invite_refused_by_peer.'
                            .format(self.account))

                call.cb.on_invite_refused_by_peer(self, call, extra)
            elif msg.msg_type == 'voip_invite_failed':
                logger.info('APICB  {0}  is calling on_invite_failed.'
                            .format(self.account))

                call.cb.on_invite_failed(self, call, INVITE_E_OTHER)
            elif msg.msg_type == 'voip_invite_bye':
                logger.info('APICB  {0}  is calling on_invite_end_by_peer.'
                            .format(self.account))

                call.cb.on_invite_end_by_peer(self, call, extra)
            elif msg.msg_type == 'voip_invite_msg':
                logger.info('APICB  {0}  is calling on_invite_msg.'
                            .format(self.account))

                call.cb.on_invite_msg(self, call, extra)

    def req_to_json(self, func_str, args, cb_pack=None):
        """Format data to be send to the server.

        Args:
            func_str (str): A functional string.
            args (dict): Attributes.
            cb: A callback function.

        Returns:
            str: A dumped json string encoded in utf8.
        """
        req = {
            u'func': func_str,
            u'args': args,
            u'cb_pack': cb_pack
        }
        self.call_table[self.call_id] = req
        root = [u'call2', [func_str, self.call_id, args]]
        self.call_id += 1
        return json.dumps(root).encode('utf8')

    def schedule_poll(self):
        """Pull messages"""
        logger.debug('NET    {0}  polling messages.'.format(self.account))
        if self.m_is_polling:
            # No need to call poll twice.
            return

        self.m_is_polling = True

        args = {
            u'line': self.line,
            u'ver_clear': self.m_ver_clear,
            u'max': 30
        }

        def on_result(error, ret_data):
            if error == '' and ret_data['result'] == 'ok':
                # The starting message version number in a series of messages.
                self.m_ver_clear = ret_data['ver_clear']

                self.m_ver_ack = self.m_ver_clear
                msgs = ret_data.get('msgs')

                for msg in msgs:
                    # Update m_ver_clear to the latest / biggest number.
                    self.m_ver_clear = msg[0]

                    line = msg[1]
                    self.inst_msgs.append(MessageDetails(line))

                if len(msgs) == 30 or self.m_ver_clear < self.m_ver_notify:
                    self.schedule_poll()

                self.m_last_active_time = self.get_time_in_ms()

            self.m_is_polling = False
            self.m_time_poll_last = self.get_time_in_ms()
            self.process_inst_msgs()

        self.call2(u'user_getmsg', args, (on_result, []))

    def schedule_poll_tail(self):
        """Poll messages"""
        self.m_time_poll_last = self.get_time_in_ms()

    def send_cmd(self, x):
        """Send a command string to the server.

        Args:
            x (str): A json string.
        """
        try:
            self.current_session.sendMessage(x)
            logger.info('NET    {0}  Sending request {1}'.format(self.account ,x))
        except IOError as e:
            logger.exception('NET    {0}  {1}'.format(self.account, e))
            self.fire_logout(LOGOUT_E_NET)

    def get_addresses(self):
        """Get LBS server addresses and stores them into self.servers."""
        is_ok = False
        for i in range(self.CFG_LBS_N_RETRY):
            try:
                res = requests.get(
                    'http://lbs.sig.agora.io/getaddr?vid=%s' % self.appid)
                if res:
                    root = res.json()
                    is_ok = True
                    del self.servers[:]
                    webs = root['web']
                    for web in webs:
                        addr = ServerAddress(web[0], web[1])
                        self.servers.append(addr)

            except IOError as e:
                logger.exception('NET    {0}  {1}'.format(self.account, e))
                time.sleep(2)
                continue

            if is_ok:
                break
            else:
                time.sleep(1)

        return is_ok

    def __connect(self):
        """Create a login session."""
        self.state = LoginSessionState.CONNECTING

        if self.state == LoginSessionState.CONNECTING and not self.is_debugging:
            is_ok = self.get_addresses()
        elif self.is_debugging:
            is_ok = True

        if self.state == LoginSessionState.CONNECTING and is_ok:
            current_url, server = self.get_server_url()
            if not current_url:
                return

            factory = ClientFactory(session=self, url=current_url)

            reactor.connectTCP(server.ip, server.port, factory)

    class LoginCallback(object):
        """Wrap login related methods to be overriden."""

        def on_login_success(self, session, uid):
            """Response when a user has successfully logged in.

            Args:
                session: A LoginSession instance.
                uid (int): The uid that returned by a server.
            """
            pass

        def on_logout(self, session, err_code):
            """Response when a user has successfully logged out.

            Args:
                session: A LoginSession instance.
                err_code (int): The error code.
            """
            pass

        def on_login_failed(self, session, uid):
            """Response when a user has failed to logg in.

            Args:
                session: A LoginSession instance.
                uid (int): The uid that returned by a server.
            """
            pass

        def on_msg_instant_received(self, session, account, uid, msg):
            """Response when a user has received a message.

            Args:
                session: A LoginSession instance.
                account (str): The user account name.
                uid (int): The uid that returned by a server.
                msg (str): The message content.
            """
            pass

        def on_invite_received(self, session, call):
            """Response when a user has received a invitation.

            Args:
                session: A LoginSession instance.
                call: A Call instance.
            """
            pass

        def on_error(self, session, err_code, reason):
            """Response when an error occurs.

            Args:
                session: A LoginSession instance.
                err_code (int): The error code.
                reason (str): Why the error occurs.
            """
            pass

    class MessageCallback(object):
        """Wrap message related functions to be overriden."""

        def on_msg_send_error(self, session, err_code):
            """Response when an error occurs after sending a message.

            Args:
                session: A LoginSession instance.
                err_code (int): The error code.
            """
            pass

        def on_msg_send_success(self, session):
            """Response when successfully sening a message.

            Args:
                session: A LoginSession instance.
            """
            pass
