#!/usr/bin/python3

def add_common_args(parser):
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
      "-r", "--tries", type=int,
      help="Chromecast connection tries. Default is infinite.")
  parser.add_argument(
      "-t", "--timeout", type=int, default=30,
      help="Chromecast socket timeout seconds. Default is 30.");
  parser.add_argument(
      "-w", "--retry_wait", type=int, default=5,
      help="Seconds to wait between Chromecast retries. Default is 5.");

  return parser
