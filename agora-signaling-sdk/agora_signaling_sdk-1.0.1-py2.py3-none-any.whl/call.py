# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


class Call(object):
    """A user call class"""

    def __init__(self, channel, peer, peeruid, extra, session):
        """
        Args:
            channel (str): The channel name.
            peer (str): The peer to be called.
            peeuid (str): The peer's uid.
            extra (str): A json body string that contains extra messages.
            session: A LoginSession instance.
        """
        self.channel = channel
        self.peer = peer
        self.peeruid = peeruid
        self.extra = extra
        self.session = session
        self.session.call_obj_table['{0}{1}'.format(channel, peer)] = self
        self.cb = Call.CallCallback()

    def set_callback(self, cb):
        """
        Args:
            cb: A Call.CallCallback instance.
        """
        self.cb = cb

    def accept(self, extra = u''):
        logger.info('API    {0}  Accepting an invitation.'
                    .format(self.session.account))
        args = {
            u'line': self.session.line,
            u'channelName': self.channel,
            u'peer': self.peer,
            u'extra': self.extra
        }
        self.session.call2(u'voip_invite_accept', args)

    def refuse(self, extra = u''):
        logger.info('API    {0}  Refusing an invitation.'
                    .format(self.session.account))
        args = {
            u'line': self.session.line,
            u'channelName': self.channel,
            u'peer': self.peer,
            u'extra': self.extra
        }
        self.session.call2(u'voip_invite_refuse', args)

    def end(self, extra = u''):
        logger.info('API    {0}  Ending an invitation.'
                    .format(self.session.account))
        def on_result(error, ret_data, call, session, extra):
            logger.info('APICB  {0}  is calling on_invite_end_by_myself'
                  .format(session.account))

            call.cb.on_invite_end_by_myself(session, call, extra)

        params = [self, self.session, extra]

        args = {
            u'line': self.session.line,
            u'channelName': self.channel,
            u'peer': self.peer,
            u'extra': self.extra
        }

        self.session.call2(u'voip_invite_bye', args, (on_result, params))

    class CallCallback(object):
        """Wrap call response behavior functions to be overriden."""

        def on_invite_received_by_peer(self, login_session, call):
            """Response when receiving an invitation call from a peer.

            Args:
                login_session: A LoginSession instance.
                call: A Call instance.
            """
            pass

        def on_invite_accepted_by_peer(self, login_session, call, extra):
            """Response when accepting an invitation call from a peer.

            Args:
                login_session: A LoginSession instance.
                call: A Call instance.
                extra (str): A json body string that contains extra messages.
            """
            pass

        def on_invite_refused_by_peer(self, login_session, call, extra):
            """Response when refusing an invitation call from a peer.

            Args:
                login_session: A LoginSession instance.
                call: A Call instance.
                extra (str): A json body string that contains extra messages.
            """
            pass

        def on_invite_failed(self, session, call, err_code):
            """Response when failing to invite a peer, this could be a network
            error or some other reason. The reason should be referred to the
            err_code..

            Args:
                login_session: A LoginSession instance.
                call: A Call instance.
                err_code (int): Error code returned by the server.
            """
            pass

        def on_invite_end_by_peer(self, session, call, extra):
            """Response when an invitation / channel session ended by a peer.

            Args:
                login_session: A LoginSession instance.
                call: A Call instance.
                extra (str): A json body string that contains extra messages.
            """
            pass

        def on_invite_end_by_myself(self, session, call, extra):
            """Response when an invitation / channel session ended by
            the initiator.

            Args:
                login_session: A LoginSession instance.
                call: A Call instance.
                extra (str): A json body string that contains extra messages.
            """
            pass

        def on_invite_msg(self, session, call, extra):
            """Response to the invitation message..

            Args:
                login_session: A LoginSession instance.
                call: A Call instance.
                extra (str): A json body string that contains extra messages.
            """
            pass
