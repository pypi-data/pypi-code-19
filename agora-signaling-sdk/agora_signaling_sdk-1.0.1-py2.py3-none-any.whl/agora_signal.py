# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


from agorasigsdk.channel2 import Channel2
from agorasigsdk.login_session import LoginSession
from agorasigsdk.rpc import RPC

import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


class AgoraSignal(object):
    """The signal api class that creates a signal before logging in."""

    def __init__(self, appid):
        """
        Args:
            appid (str): The unique credential.
        """
        if not appid:
            raise ValueError('Appid is not valid.')
        else:
            self.appid = appid

    def create_rpc_session(self, token, **kwargs):
        rpc_session = RPC(self.appid, token, **kwargs)
        return rpc_session

    def join_channel2(
                self, channelName, channelAttrs={}, failWhenExists=False,
                needState=False, simpleHost={}, topicsToSubscribe=[],
                userId='', userInfo={}, onJoin=None, onJoinFailed=None,
                onLeave=None, onMessage=None):
        """
        Returns:
            channel2 (Channel2): A Channel2 instance.
        """
        # channelName must be a valid string.
        if not channelName:
            raise ValueError('channelName can not be empty.')

        channel2 = Channel2(
                self.appid, channelName, channelAttrs, failWhenExists,
                needState, simpleHost, topicsToSubscribe,
                userId, userInfo, onJoin, onJoinFailed,
                onLeave, onMessage)
        return channel2

    def login(self, account, token, cb=None,
              is_debugging=False, debug_params=[]):
        """
        Args:
            account (str): The user account name.
            token (str): The default is '_no_need_token'.
            cb: A callback functions wrapper class.
        """
        logger.info('API  {0}  login() is called, creating a LoginSession.'
                    .format(account))

        # Exception handlers.
        if not account:
            raise ValueError('account can not be empty.')
        if not token:
            raise ValueError('token can not be empty.')

        if not cb:
            cb = LoginSession.LoginCallback()

        return LoginSession(
                account=account, appid=self.appid, token=token, cb=cb,
                is_debugging=is_debugging, debug_params=debug_params)
