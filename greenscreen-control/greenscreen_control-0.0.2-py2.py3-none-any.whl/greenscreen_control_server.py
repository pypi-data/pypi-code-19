#!/usr/bin/python3

import argparse
import logging
import sys

from greenscreen_control import chromecast_controller
from greenscreen_control import common_args
from greenscreen_control import greenscreen_client
from greenscreen_control import server

def main():
  parser = common_args.add_common_args(argparse.ArgumentParser())

  parser.add_argument("-p", "--port", type=int, default=4995,
                      help="TCP server port number")
  args = parser.parse_args()

  if not args.appid:
    logging.error("AppID needs to be set (-a) for server mode.")
    sys.exit(1)

  logging.basicConfig(
      level=logging.getLevelName(args.loglevel),
      format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s",
      datefmt="%F %H:%M:%S")
  logging.info("Starting ...")
  logging.info("... Greenscreen server: %s" % args.greenscreen_server)
  logging.info("... Greenscreen App ID: %s" % args.appid)
  logging.info("... Control Server port: %u" % args.port)

  controller = chromecast_controller.CachedChromecastController(
      tries=args.tries,
      timeout=args.timeout,
      retry_wait=args.retry_wait)


  logging.info("Discovering Chromecasts ...")
  controller.discover_chromecasts()

  server.Serve(
      args.port,
      greenscreen_client.GreenScreenClient(args.greenscreen_server),
      controller,
      args.appid)


if __name__ == "__main__":
  main()
