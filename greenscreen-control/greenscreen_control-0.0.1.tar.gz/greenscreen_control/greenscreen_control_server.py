#!/usr/bin/python3

import argparse
import logging

from greenscreen_control import chromecast_controller
from greenscreen_control import greenscreen_client
from greenscreen_control import server

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument("-g", "--greenscreen_server",
                      default="http://localhost:4994",
                      help="GreenScreen server:port")
  parser.add_argument("appid",
                      help="Chromecast Greenscreen App ID")
  parser.add_argument("-p", "--port", type=int, default=4995,
                      help="TCP server port number")
  parser.add_argument(
      "-l", "--loglevel", default="INFO", help="Logging level",
      choices=["ERROR", "WARNING", "INFO", "DEBUG"])
  args = parser.parse_args()

  logging.basicConfig(
      level=logging.getLevelName(args.loglevel),
      format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s",
      datefmt="%F %H:%M:%S")
  logging.info("Starting ...")
  logging.info("... Greenscreen server: %s" % args.greenscreen_server)
  logging.info("... Greenscreen App ID: %s" % args.appid)
  logging.info("... Control Server port: %u" % args.port)

  controller = chromecast_controller.CachedChromecastController()

  logging.info("Discovering Chromecasts ...")
  controller.discover_chromecasts()

  server.Serve(
      args.port,
      greenscreen_client.GreenScreenClient(args.greenscreen_server),
      controller,
      args.appid)


if __name__ == "__main__":
  main()
