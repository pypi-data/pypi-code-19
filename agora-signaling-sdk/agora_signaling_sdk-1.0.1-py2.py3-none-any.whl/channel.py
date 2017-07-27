# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


from __future__ import absolute_import

from agorasigsdk.signal_consts import (LEAVECHANNEL_E_BYUSER,
                                       JOINCHANNEL_E_OTHER)

import logging
import json


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


class Channel(object):
    """A Channel class for user communication such as user call,
    live broadcasting.
    """

    def __init__(self, session, name=None, cb=None):
        """
        Args:
            session: A LoginSession instance.
            name (str): The channel name.
            cb: A callback class.
        """
        self.session = session
        self.channel_name = name

        # Channel's callback is default to be Channel.ChannelCallback.
        self.cb = cb if cb else Channel.ChannelCallback()

        def on_result(error, ret_data, cb, channel, session):
            if error == '' and ret_data['result'] == 'ok':
                attrs = ret_data['attrs']
                l = ret_data['list']

                users, uids = [], []
                for user in l:
                    account = user[0]
                    uid = int(user[1])
                    users.append(account)
                    uids.append(uid)

                logger.info('APICB  {0}  Calling on_channel_joined.'
                            .format(session.account))

                cb.on_channel_joined(session, channel)

                logger.info('APICB  {0}  Calling on_channel_user_list.'
                            .format(session.account))

                cb.on_channel_user_list(session, channel, users, uids)

                for k in attrs:
                    logger.info('APICB  {0}  Calling on_channel_attr_updated.'
                                .format(session.account))

                    cb.on_channel_attr_updated(session, channel, k,
                                               attrs[k], u'update')
            else:
                logger.info('APICB  {0}  Calling on_channel_join_failed.'
                            .format(session.account))

                cb.on_channel_join_failed(session, channel,
                                          JOINCHANNEL_E_OTHER)

        params = [self.cb, self, session]

        args = {u'line': session.line, u'name': name}

        session.call2(u'channel_join', args, (on_result, params))

    def channel_leave(self):
        logger.info('API    {0}  Calliing channel_leave.'
                    .format(self.session.account))
        args = {u'line': self.session.line, u'name': self.channel_name}

        self.session.call2(u'channel_leave', args)

        logger.info('APICB  {0}  Calling on_channel_left.'
                    .format(self.session.account))

        self.cb.on_channel_left(self.session, self, LEAVECHANNEL_E_BYUSER)

    def channel_set_attr(self, name, value):
        """Update a channel attribute.

        Args:
            name (str): The attribute name to be updated.
            value (str): New attribute value.
        """
        logger.info('API    {0}  Calliing channel_set_attr.'
                    .format(self.session.account))
        args = {
            u'line': self.session.line,
            u'channel': self.channel_name,
            u'name': name,
            u'value': value
        }

        self.session.call2(u'channel_set_attr', args)

    def channel_del_attr(self, name):
        logger.info('API    {0}  Calliing channel_del_attr.'
                    .format(self.session.account))
        args = {
            u'line': self.session.line,
            u'channel': self.channel_name,
            u'name': name
        }

        self.session.call2(u'channel_del_attr', args)

    def channel_clear_attr(self):
        logger.info('API    {0}  Calliing channel_clear_attr.'
                    .format(self.session.account))
        args = {u'line': self.session.line, u'channel': self.channel_name}

        self.session.call2(u'channel_clear_attr', args)

    def msg_channel_send(self, msg, cb_pack=None):
        """Send a message in a channel.

        Args:
            msg (str): The message content.
            cb_pack (func): A callback function to respond to the result.
        """
        logger.info('API    {0}  Calliing msg_channel_send.'
                    .format(self.session.account))
        args = {
            u'line': self.session.line,
            u'name': self.channel_name,
            u'msg': msg
        }

        self.session.call2(u'channel_sendmsg', args, cb_pack)

    class ChannelCallback(object):
        """Wrap channel related functions to be overriden."""

        def on_channel_joined(self, login_session, channel):
            """Response when joining a channel.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
            """
            pass

        def on_channel_join_failed(self, login_session, channel, err_code):
            """Response when failing to join a channel.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
                err_code: Error code returned by the server.
            """
            pass

        def on_channel_left(self, login_session, channel, err_code):
            """Response when leaving a channel.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
                err_code: Error code returned by the server.
            """
            pass

        def on_channel_user_joined(self, login_session, channel, account, uid):
            """Response when a user joins a channel.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
                account (str): The user name.
                uid (int): An integer received after loginng into the server.
            """
            pass

        def on_channel_user_left(self, login_session, channel, account, uid):
            """Response when a user leaves a channel.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
                account (str): The user name.
                uid (int): An integer received after loginng into the server.
            """
            pass

        def on_channel_user_list(self, login_session, channel, users, uids):
            """Response after having a list of users in a channel.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
                users (list): A list of users.
                uids (list): A list of int uids.
            """
            pass

        def on_channel_attr_updated(self, login_session, channel,
                                    name, value, ch_type):
            """Response when updating a channel's attributes.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
                name (str): The attribute name.
                value (str): The attribute value.
                type (str): The update behavior, could be
                            `update`, `del` or `clear` etc.
            """
            pass

        def on_msg_channel_received(self, login_session, channel,
                                        account, uid, msg):
            """Response when receiving a message in a channel.

            Args:
                login_session: A LoginSession instance.
                channel: A Channel instance.
                account (str): The user name.
                uid (int): An integer received after loginng into the server.
                msg (str): The received message.
            """
            pass
