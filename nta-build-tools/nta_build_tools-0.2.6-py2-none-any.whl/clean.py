# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2017, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""Tool for cleaning up previous Numenta builds and Python installs.

This tool attempts to uninstall a package and remove the build directory.
Python packages may not be fully uninstalled if they were previously
installed with a different repo or Python package name.

This tool will not modify your local git repository aside from removing
the build directory. You may need to do a `git clean` in the repo as well
to avoid improper installs from old files.
"""

import argparse
import os
import sys

from ntabuildtools.repos import (
    DEFAULT_REPOS, DEFAULT_REPOS_CPP, PACKAGE_NAMES, SRC_PATH, IMPORT_TEST)
from ntabuildtools.utils import pipUninstall, subprocessCall

SITE_PACKAGES = os.path.expanduser(
    "~/Library/Python/2.7/lib/python/site-packages")



def rmBuild(repo, dryrun):
  buildDir = os.path.expanduser("~/nta/{}/build".format(repo))
  command = ["rm", "-rf", buildDir]
  subprocessCall(command, dryrun)



def pipRemove(repo, dryrun):
  """Repeatedly call 'pip uninstall' until it fails."""
  assert repo in DEFAULT_REPOS
  package = PACKAGE_NAMES[repo]
  uninstallAttempts = 0
  while True:
    try:
      pipUninstall([package], dryrun)

    except:
      print "Uninstall failed... continuing."
      break
    uninstallAttempts += 1
    if dryrun or uninstallAttempts == 5:
      break



def manualUninstall(repo, dryrun):
  """Delete package-specific .pth/.egg-link files."""
  assert repo in DEFAULT_REPOS
  package = PACKAGE_NAMES[repo]
  potentialFiles = [
    os.path.join(SITE_PACKAGES, "{}-nspkg.pth".format(package)),
    os.path.join(SITE_PACKAGES, "{}.egg-link".format(package)),
  ]
  for path in potentialFiles:
    if os.path.exists(path):
      subprocessCall(["rm", path], dryrun)

  # Remove package from generic .pth file
  easyPth = os.path.join(SITE_PACKAGES, "easy-install.pth")
  shouldWrite = False
  outputLines = []
  try:
    with open(easyPth) as f:
      inputLines = f.readlines()
    importPaths = SRC_PATH[repo]
    for line in inputLines:
      if line.strip() in importPaths:
        shouldWrite = True
      else:
        outputLines.append(line)

    if shouldWrite:
      with open(easyPth, "w") as f:
        for line in outputLines:
          f.write(line)
  except:
    print "Error while checking easy-install.pth, ignoring."



def checkUninstalled(repo, dryrun):
  """Make sure the package can no longer be imported."""
  testImports = IMPORT_TEST[repo]
  for testImport in testImports:
    returnCode = subprocessCall(
        ["python", "-c", "'import {}'".format(testImport)], dryrun)
    if returnCode == 0:
      raise RuntimeError(
          "ERROR: '{}' can still be imported. Please seek "
          "assistance in uninstalling the package and updating this "
          "tool to better handle this situation.".format(testImport))



def uninstall(repo, dryrun):
  pipRemove(repo, dryrun)
  manualUninstall(repo, dryrun)
  checkUninstalled(repo, dryrun)



def fullUninstall(repo, dryrun):
  uninstall(repo, dryrun)
  if repo in DEFAULT_REPOS_CPP:
    rmBuild(repo, dryrun)



def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "repo", nargs="+",
      help="One or more of: {}. Or 'all' to clean them all".format(
          ",".join(DEFAULT_REPOS)))
  parser.add_argument("--dryrun", action="store_true", default=False,
                      help="print commands without executing them")
  args = parser.parse_args()

  if "all" in args.repo:
    repos = DEFAULT_REPOS
  else:
    repos = args.repo

  for repo in repos:
    if repo not in DEFAULT_REPOS:
      print "Unknown repo: '{}'. Specify one of: {}".format(
          repo, ", ".join(DEFAULT_REPOS + ["all"]))
      sys.exit(-1)

  for repo in repos:
    fullUninstall(repo, args.dryrun)
