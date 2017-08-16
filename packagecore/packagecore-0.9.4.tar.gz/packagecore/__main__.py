#!/usr/bin/python3
##
# @file main.py
# @brief The main function.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-07-03


import sys
import os
import optparse

from .configfile import YAMLConfigFile
from .packager import Packager
from .distributions import DATA


BIN_NAME="packagecore"


def showDistributions():
  print("Available distributions to use as targets in the 'packages' section:")
  for distname, data in DATA.items():
    print("\t%s" % distname)


def getVersion():
  import pkg_resources
  versionBytes = pkg_resources.resource_string(__name__, "VERSION")
  version = versionBytes.decode("utf8").strip()
  return version
  print(version)


def main():
  # defaults
  release=1
  configFilename="packagecore.yaml"
  outputdir="./"

  packageCoreVersion = getVersion()

  usage = "usage: %prog [options] <version> [<release number>]"
  parser = optparse.OptionParser(usage=usage)

  # we set the default to None here, so we can check if it has been, otherwise
  # we'll just assume they're looking for the default in the -C option
  parser.add_option("-c", "--config", dest="configfile", \
      metavar="<yaml file>", \
      default=None, help="The path to the yaml configuration " \
      "file. Defaults to %s." % configFilename)

  parser.add_option("-C", "--src", dest="sourceDir", \
      metavar="<source dir>", \
      default="./", help="The source directory to build. " \
      "Defaults to '%default'.")

  parser.add_option("-p", "--package", dest="distribution", \
      metavar="<distribution name>", default=None, \
      help="Instead of building all packages in a configuration file, build "
      "a package for a specific distribution.")

  parser.add_option("-o", "--outputdir", dest="outputdir", \
      metavar="<output directory>", default=outputdir, \
      help="The directory to " \
      "put generated packages into. If the directory does not exist, it " \
      "will be created. Defaults to %default.")

  parser.add_option("-d", "--distributions", action="store_true", \
      dest="showdistributions", help="Show a list of available Linux " \
      "distributions to use as targets in the 'packages' section.")

  parser.add_option("-v", "--version", action="store_true", \
      dest="showversion", help="Display the current version.")

  (options, args) = parser.parse_args()

  if options.configfile is None:
    options.configfile = os.path.join(options.sourceDir, configFilename)

  if not options.showdistributions is None:
    showDistributions()
    return 0
  elif not options.showversion is None:
    print("%s %s" % (BIN_NAME, packageCoreVersion))
    return 0
  else:
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
    print("Building with %s %s." % (BIN_NAME, packageCoreVersion))
    print("Building version '%s' release '%d'." % (version, release))

    # if we're using the default configFilename assume we mean in the source
    # directory
    conf = YAMLConfigFile(options.configfile)

    p = Packager(conf=conf.getData(), srcDir=options.sourceDir, \
        outputDir=options.outputdir, version=version, release=release, \
        distribution=options.distribution)
    if p.run():
      return 0
    else:
      return 1


if __name__ == "__main__":
  ret = main()
  sys.exit(ret)
