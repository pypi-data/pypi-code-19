#!/usr/bin/python

import logging
import re
import pychromecast

from twisted.internet import protocol, reactor, endpoints
from twisted.protocols.basic import LineReceiver

import chromecast_controller
import greenscreen_client

# Protocol: Simple line based TCP protocol
#
# chromecast=Name Of Chromecast,channel=Foo,cast=1
#  - Set the channel to 'Foo' on the specified Chromecast and start casting.
# chromecast=Name Of Chromecast,cast=0
#  - Stop casting on the specified Chromecast.
# chromecast=Name Of Chromecast,channel=Foo
#  - Set the channel on the specified Chromecast but don't cast.

class GSCLineHandler(LineReceiver):
  RE_CHROMECAST = re.compile("^chromecast=(?P<chromecast>.*)")
  RE_CHANNEL = re.compile("^channel=(?P<channel>.*)")
  RE_CAST = re.compile("^cast=(?P<cast>[01])$")

  delimiter = b"\n"

  def __init__(self, greenscreen_client, chromecast_controller, app_id):
    self._greenscreen_client = greenscreen_client
    self._chromecast_controller = chromecast_controller
    self._app_id = app_id

  def connectionMade(self):
    logging.info("Connection from: %s" % str(self.transport.getPeer()))
 
  def lineReceived(self, line):
    chromecast = channel = cast = None
    line = line.decode('utf-8')
    line = line.strip()

    for piece in line.split(","):
      chromecast_result = self.RE_CHROMECAST.search(piece) 
      if chromecast_result:
        chromecast = chromecast_result.group('chromecast')
        continue
      channel_result = self.RE_CHANNEL.search(piece) 
      if channel_result:
        channel = channel_result.group('channel')
        continue
      cast_result = self.RE_CAST.search(piece)
      if cast_result:
        cast = bool(int(cast_result.group('cast')))
        continue

    if chromecast is None:
      logging.warning("Received command without chromecast name from: %s" % (
          str(self.transport.getPeer())))
      return
    elif channel is None and cast is None:
      logging.warning("Received incomplete command for '%s' from: %s" % (         
          chromecast, str(self.transport.getPeer())))
      return

    if channel is not None:
      self._greenscreen_client.set_channel_for_chromecast(
          chromecast, channel)
    if cast is not None:
      if cast:
        self._chromecast_controller.start_chromecast_app(chromecast, self._app_id)
      else:
        self._chromecast_controller.stop_chromecast_app(chromecast)


class GSCLineHandlerFactory(protocol.Factory):
  protocol = GSCLineHandler
  def __init__(self, greenscreen_client, chromecast_controller, app_id):
    self._greenscreen_client = greenscreen_client
    self._chromecast_controller = chromecast_controller
    self._app_id = app_id

  def buildProtocol(self, addr):
    return GSCLineHandler(
        self._greenscreen_client, self._chromecast_controller, self._app_id)

def Serve(port, greenscreen_client, chromecast_controller, app_id):
  logging.info("Starting TCP server on port: %i" % port)
  reactor.listenTCP(port, GSCLineHandlerFactory(
      greenscreen_client, chromecast_controller, app_id))
  reactor.run()
