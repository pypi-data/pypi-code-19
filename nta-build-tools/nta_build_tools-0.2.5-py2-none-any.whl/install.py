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

"""Tool for installing Numenta Python packages.

This tool will attempt to uninstall existing packages and, by default,
perform a developer install from the local repository. Alternatively,
`--version` can be specified to install a versioned release.
"""

import argparse
import os
import sys

from ntabuildtools.clean import uninstall
from ntabuildtools.repos import PACKAGE_NAMES, DEFAULT_REPOS
from ntabuildtools.utils import filterRequirementsFile, pipInstall



def executeInstall(repo, version, dryrun):
  repoDir = os.path.expanduser("~/nta/{}".format(repo))
  package = PACKAGE_NAMES[repo]

  # Clean uninstall any currently installed version
  uninstall(repo, dryrun)

  # Install requirements
  pipInstall(filterRequirementsFile(repo), dryrun)

  env = {"ARCHFLAGS": "-arch x86_64"}

  # Install the package
  if version == "latest":
    pipInstall([package], dryrun, env=env)
  elif version is not None:
    pipInstall(["{}=={}".format(package, version)], dryrun, env=env)
  else:
    os.chdir(repoDir)
    pipInstall(["-e", "."], dryrun, env=env)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "repos", metavar="repo", nargs="+", default=None,
      help="One or more of: {}. Or specify 'all' to install them all".format(
          ",".join(DEFAULT_REPOS)))
  parser.add_argument("--version", dest="version", default=None,
                      help="optional released version to install, or 'latest' "
                           "for the most recent release")
  parser.add_argument("--dryrun", action="store_true", default=False,
                      help="print the commands but don't execute them")

  args = parser.parse_args()

  if "all" in args.repos:
    repos = DEFAULT_REPOS
  else:
    repos = args.repos

  for repo in repos:
    if repo not in PACKAGE_NAMES.keys():
      print "Unknown repo: '{}'. Specify one of: {}".format(
          repo, ", ".join(PACKAGE_NAMES.keys() + ["all"]))
      sys.exit(-1)

  for repo in repos:
    executeInstall(repo, args.version, args.dryrun)
