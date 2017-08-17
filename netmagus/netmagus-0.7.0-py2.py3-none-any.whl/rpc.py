# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import time

import autobahn_sync

import netmagus.form

"""
NetMagus Python Library
Copyright (C) 2016 Intelligent Visbility, Inc. - Richard Collins
<richardc@intelligentvisibility.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Normally a Form (as defined in the netmagus.form module) is used to
represent individual NetMagus UI screens
and does data exchange with formula code via file exchange.

Within a given formula, a user may choose to have multiple real-time data
exchanges between the NetMagus UI and the formula itself.  To do this,
the below RPC methods and data object classes can be used to do WAMP based
RPC calls to pass messages to/from the UI instead of using file-based JSON
exchanges.

A sample usage pattern to send a new screen would be:
- usernameinput = netmagus.form.TextInput(label='username')
- message_to_user = netmagus.rpc.Form(name="Username Input",
description="Enter your user name below",
form=[usernameinput])
- netmagus.rpc.rpc_connect('ws://nmhostaddress:8080/ws', 'netmagus')
- username = netmagus.rpc.rpc_form_query(token, myformobject, poll=.5,
timeout=60)
    - here the UI will update and show the form, and wait for user to enter
    the data and press submit
    - once user presses submit the response will be waitig for rcp_receive to
    pick it up
    - rpc_form_query polls the RPC looking for a reponse from the user at
    'poll' interval and stop at 'timeout' if no repsonse received
- use normal try logic to determine if timeout occurred by catching the
RpcCallTimeout exception and handling it

A user can write these as a series of synchronous interactions with the UI to
allow a single formula step to gather numerous pieces of information,
make branched execution decisions, or collapse many formula steps into one.

This allows formula writers to avoid having to adopt async programming
constructs to interact with the NetMagus UI since the typical NetMagus user
experience is a step-by-step "wizard" like approach with code blocks executed
between each interaction.

To display simple HTML updates to a user, use pattern such as:
mymessage = netmagus.rpc.Html(append=True, title='Important User Update!',
data="<p>Processing your input now...</p>")
netmagus.rpc.rpc_send(token, mymessage)

This will fire a RPC message to the UI which will then display the data
within the user's screen
"""


class Message(object):
    """
    RPC Message Envelope

    Example:
        {
         'messageType': 'html',
         'message': {}
         }

    messageType: property inferred by data type sent in the message arg
        possible values:
            html: used for html content
            form: used for asking user a question
    message: object containing actual message of type netmagus.rpc.Form or
    netmagus.rpc.Html
    """

    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return str(self.as_dict)

    @property
    def as_dict(self):
        """
        return a dictionary representation of the Message() with proper values
        for message type and proper dictionary version of the message payload
        """
        return {
            'messageType': self.messageType, 'message': self.message.as_dict
        }

    @property
    def messageType(self):
        """
        Returns proper message type based upon the data type inside the message
        """
        if isinstance(self.message, netmagus.form.Form):
            return 'netop'
        elif isinstance(self.message, Html):
            return 'html'


class Html(object):
    """
    HTML object used for sending rich content back to the user
     {
          'printToUser': True,
          'append': True,
          'outputType': 'html',
          'title': 'Just an RPC Call',
          'data': "<b>Executing command please wait</b> <i title='Executing
          Operation' class='glyph-icon  fa
          fa-spinner icon-spin'></i>"
     }
    :param printToUser: boolean flag controls if this is sdisplayed (this may
    not be
    needed anymore)
    :param append: controls if the data should be appended to exsiting html output
    or replace what is already there
    outputType: type of data to be displayed (this may not be needed anymore)
    :param title: displayed in the header section
    :param data: actual html code
    """

    def __init__(self, printToUser=True, append=True, title="", data=""):
        self.printToUser = printToUser
        self.append = append
        self.title = title
        self.data = data
        self.outputType = 'html'

    def __repr__(self):
        return str(self.as_dict)

    @property
    def as_dict(self):
        """
        Return a dictionary representation of self
        :return: dictionary of self
        """
        return self.__dict__


def rpc_connect(url="ws://127.0.0.1:8088/ws", realm="netmagus"):
    """
    Utilizes autobahn_sync to create Twisted thread in the background to
    handle async WAMP messaging and connect to a given WAMP URL and realm.
    WAMP is used by NetMagus for real-time data exchange between the UI and
    any wizards/formulas to update a UI screen or retrive data entered by a
    user.

    :param url: WAMP URL to connet to (ex - Crossbar.io instance @
    ws://localhost:8088/ws)
    :param realm: the crossbar realm to use for this connection (ex - netmagus)
    """
    return autobahn_sync.run(url=url, realm=realm)


def rpc_disconnect():
    """
    Stop the autobahn_sync Twisted thread
    """
    return autobahn_sync.app.stop()


def rpc_send(token, message, retry_count=10, retry_delay=.2):
    """
    This method is used to send data to NetMagus for a given wizard/formula
    execution.  Each execution has its own RPC methods created upon execution
    to allow RTC between the UI and the formula/wizard code.  After using
    rpc_send, rpc_receive can be used to fetch results once the operation is
    complete.
    This method by default will retry sending the data for 2 seconds it in
    cases were target method is not registered yet or in cases where the
    back-end does not acknowledge our receipt.  After time-out, it then will
    raise an RpcCallTimeout exception.

    :param token: random/unique token supplied by NetMagus for each execution
    of a formula/wizard.  It is used to associate messages with individual
    formula execution instances.
    :param message: the payload to be sent to
    :param retry_delay:  How long in seconds to wait between retry_count
    :param retry_count: How many times to retry the send operation until a
                        valid ACK is received or until no exception is raised
    :return: None - to receive response, use rpc_receive with same token
    """
    if isinstance(message, netmagus.form.Form):
        rpc_target = "com.intelligentvisibility." + token + ".browser.sendform"
    elif isinstance(message, Html):
        rpc_target = "com.intelligentvisibility." + token + \
                     ".browser.displaymessage"
    else:
        raise TypeError(
            'invalid rpc_send Message payload, must be of type '
            'netmagus.rpc.Form or netmagus.rpc.Html')
    while retry_count >= 0:
        try:
            response = autobahn_sync.call(rpc_target, Message(message).as_dict)
            if response == "ok":
                return response
            retry_count -= 1
            time.sleep(retry_delay)
        except autobahn_sync.ApplicationError as exc:
            if "com.intelligentvisibility" + token + ".ui." in \
                    exc.error_message():
                # TODO: remove once NM stops passing these from browser ui
                return "ok"
            if retry_count <= 0:
                raise
            retry_count -= 1
            time.sleep(retry_delay)
    raise RpcCallTimeout


def rpc_receive(token, retry_count=10, retry_delay=.2):
    """
    Since NetMagus RPC calls may have an indeterminite amount of time before
    a user completes an interaction and submits the response data,
    rpc_receive is used as a polling mechanism to allow formula writers to
    avoid having to write async code to handle responses. This method will
    :param token: random/unique token supplied by NetMagus for each execution
    of a formula/wizard.  It is used to associate messages with individual
    formula execution instances.
    :param retry_count: the # of times we should try to retrieve data via the
    WAMP RPC call at the RPC target
    :param retry_delay: the amount of time in seconds between retries
    :return: None if no data ready, else whatever JSON response data is
    available from the the UI
    """
    while retry_count >= 0:
        try:
            return autobahn_sync.call(
                "com.intelligentvisibility." + token +
                ".browser.getformresponse")
        except autobahn_sync.ApplicationError:
            if retry_count <= 0:
                raise
            retry_count -= 1
            time.sleep(retry_delay)
    raise RpcCallTimeout


class RpcCallTimeout(Exception):
    """
    Exception for timeouts when waiting for poll-based synchronous WAMP RPC
    calls to return
    """
    pass


def rpc_form_query(token, message, poll=1, timeout=-1):
    """
    Send a Form to the Netmagus UI, then poll the response target looking for
    the return value from a user. This method blocks indefinitely unless a
    timeout value is provided.  Poll frequency dictates how often additional
    WAMP RPC calls are made looking for the response data from the NetMagus UI.
    :param token: session token passed down from NetMagus UI when it runs a
    formula
    :param message:
    :param poll: poll interval in seconds to look for response data
    :param timeout: timeout in seconds to block waiting for a response,
    0 disables block, -1 blocks indefinitely
    :return:
    """
    if isinstance(message, netmagus.form.Form):
        rpc_send(token, message)
        start_time = time.time()
        response = rpc_receive(token)
        while not response and timeout > 0:
            time.sleep(poll)
            response = rpc_receive(token)
            if time.time() > (start_time + timeout):
                raise RpcCallTimeout(
                    'Exceeded timeout of {}s waiting for response to call '
                    'for '
                    'token {}.  '
                    'Message was: {}'.format(timeout, token, message))
        while not response and timeout < 0:
            time.sleep(poll)
            response = rpc_receive(token)
        return response
    else:
        raise TypeError(
            'invalid Message payload, must be of type netmagus.rpc.Form')
