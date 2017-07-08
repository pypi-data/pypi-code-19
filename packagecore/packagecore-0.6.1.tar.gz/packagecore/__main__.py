#!/usr/bin/python3
##
# @file main.py
# @brief The main function.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-07-03


import sys
import optparse


from .configfile import YAMLConfigFile
from .packager import Packager


def main():
  # defaults
  release=1
  configFilename="packagecore.yaml"

  usage = "usage: %prog [options] <version> [<release number>]"
  parser = optparse.OptionParser(usage=usage)
  parser.add_option("-c", "--config", dest="configfile", \
      metavar="<yaml file>",
      default=configFilename, help="The path to the yaml configuration " \
      "file. Defaults to %default.")
  
  (options, args) = parser.parse_args()
  if len(args) == 0:
    print("Must supply a version string." ,file=sys.stderr)
    parser.print_help(file=sys.stderr)
    return -1
  elif len(args) > 2:
    print("Too many arguments.", file=sys.stderr)
    parser.print_help(file=sys.stderr)
    return -1

  version=args[0]
  if len(args) == 2: 
    release=int(args[1])
  print("Building version '%s' release '%d'." % (version, release))

  conf = YAMLConfigFile(configFilename)
  print("Parse '%s' configuration." % configFilename)

  p = Packager(conf=conf.getData(), version=version, release=release)
  p.run()

if __name__ == "__main__":
  ret = main()
  sys.exit(ret)
