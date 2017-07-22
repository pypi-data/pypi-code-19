#!/usr/bin/python3

import argparse
import logging
import sys

from greenscreen_control import chromecast_controller
from greenscreen_control import greenscreen_client
from greenscreen_control import server

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument("-g", "--greenscreen_server",
                      default="http://localhost:4994",
                      help="GreenScreen server:port")
  parser.add_argument("-a", "--appid",
                      help="Chromecast Greenscreen App ID")
  parser.add_argument("-c", "--channel",
                      help="GreenScreen channel to set")
  parser.add_argument(
      "-l", "--loglevel", default="ERROR", help="Logging level",
      choices=["ERROR", "WARNING", "INFO", "DEBUG"])
  parser.add_argument(
      "command", help="Command",
      choices=["set-channel", "cast", "stop-cast"])
  parser.add_argument(
      "chromecast", help="Chromecast name")

  args = parser.parse_args()

  logging.basicConfig(
      level=logging.getLevelName(args.loglevel),
      format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s",
      datefmt="%F %H:%M:%S")

  if args.command == "set-channel":
    if args.channel is None:
      logging.error("set-channel command needs a channel to set (-c)")
      sys.exit(1)

    gsc = greenscreen_client.GreenScreenClient(args.greenscreen_server)
    gsc.set_channel_for_chromecast(args.chromecast, args.channel)
  else:
    controller = chromecast_controller.CachedChromecastController()

    if args.command == "cast":
      if args.appid is None:
        logging.error("cast command needs an appid to cast (-a)")
        sys.exit(1)
      controller.discover_chromecasts()
      controller.start_chromecast_app(args.chromecast, args.appid)
    elif args.command == "stop-cast":
      controller.discover_chromecasts()
      controller.stop_chromecast_app(args.chromecast)

if __name__ == "__main__":
  main()
