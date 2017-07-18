##
# @file packager.py
# @brief The top-level Packager class for orchestrating the package builds.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-07-03

import shutil
import os
import traceback

from .docker import Docker
from .pkgbuild import PkgBuild
from .dpkg import DebianPackage
from .rpm import RPM
from .distributions import DATA as BUILDS
from .scriptfile import generateScript 
from .configparser import ConfigParser


class UnknownPackageTypeError(Exception):
  pass


class PackageNotFoundError(Exception):
  pass


class Packager(object):
  ##
  # @brief Create a packager object.
  #
  # @param conf The configuration to use.
  # @param outputDir The directory to output packages into.
  # @param srcDir The directory containing the projects source.
  # @param version The version of packages to generate.
  # @param release The release number.
  # @param distribution The distribution to build a package for.
  #
  # @return The new Packager.
  def __init__(self, conf, srcDir, outputDir, version, release,
      distribution=None):
    self._outputDir = outputDir
    self._srcDir = srcDir

    if not os.path.exists(self._outputDir):
      os.makedirs(self._outputDir)

    parser = ConfigParser()
    builds = parser.parse(conf=conf, version=version, release=release)
    
    if not distribution is None:
      soloBuild = None
      for b in builds:
        if b.os == distribution:
          soloBuild = b
          break
        else:
          # skip this package
          print("Skipping '%s'." % b.os)
      if soloBuild is None:
        raise PackageNotFoundError("No '%s' listed in configuration." % \
            distribution)
      self._queue = [soloBuild]
    else:
      self._queue = builds


  ##
  # @brief Build each package.
  #
  # @return None 
  def run(self):
    success = True 
    docker = Docker()
    if len(self._queue) == 0:
      print("No packages to build.")
      success = False
    for job in self._queue:
      build = BUILDS[job.os]
      nameFormat = build["formatString"]
      pkgType = build["packageType"]
      if pkgType == "pkgbuild":
        recipe = PkgBuild(job)
      elif pkgType == "debian":
        recipe = DebianPackage(job)
      elif pkgType == "rpm":
        recipe = RPM(job, useYum=False)
      elif pkgType == "rpm-yum":
        recipe = RPM(job, useYum=True)
      else:
        raise UnknownPackageTypeError("Unknown packaging type: %s" % pkgType) 

      # remove package if it exists
      outfile = os.path.join(self._outputDir, \
          nameFormat.format(name=job.name, version=job.version,
          release=job.releaseNum, arch=recipe.getArch()))
      try:
        print("Building package for %s: %s" % (job.os, str(job)))
        tmpfile = os.path.join("/tmp", recipe.getName())

        # build the package
        container = docker.start(build["dockerImage"])

        print("Using shared directory '%s' and source directory '%s'." %
            (container.getSharedDir(), container.getSourceDir()))

        try:
          # copy in source -- we must be in the source directory
          container.copySource(self._srcDir)

          # run the 'pre' commands in the container
          preCmdFile = os.path.join(container.getSharedDir(), ".preCmds")
          generateScript(preCmdFile, job.preCompileCommands)

          recipe.prep(container)
          recipe.build(container)

          # copy out finished package
          shutil.copy(
              os.path.join(container.getSharedDir(), recipe.getName()), \
              tmpfile)
        finally:
          container.stop()

        # spawn a new docker container
        container = docker.start(build["dockerImage"])
        try:
          # copy in the package for installation
          shutil.copy(tmpfile, container.getSharedDir())
          recipe.install(container)

          container.executeScript(job.testInstallCommands)
        finally:
          container.stop()

        # move the package to the current directory
        shutil.move(tmpfile, outfile)

        print()
        print("###########################################################")
        print("# Successfully built package for '%s'." % \
            job.os)
        print("###########################################################")
        print()
      except:
        print()
        print("###########################################################")
        print("# Failed to build package for '%s'." % \
            job.os)
        print("###########################################################")
        print(traceback.format_exc())
        print("###########################################################")
        print()
        success = False
    return success 
        
        


