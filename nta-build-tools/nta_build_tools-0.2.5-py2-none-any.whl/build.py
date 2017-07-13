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

"""Tool for building Numenta C++ projects.

This tool runs the cmake/make commands for projects but does not actually
install the Python packages. The default behavior is to do incremental builds.
To do a clean build, run `nta-clean <project>` or delete the `build` directory
in the root of the repository before rerunning this script.

The `-d` and -`r` arguments are mutually exclusive and determine whether the
debug (`-d`) or release (`-r`) build is copied into the Python project. The
`--build-both` option enables running both builds, although only the one
specified with `-d` or `-r` will be copied into the Python project. This is
useful for cases where you frequently switch back and forth between develop
and release builds.
"""

import argparse
import os
import sys

from ntabuildtools.repos import (
  CMAKE_EXTRA_OPTIONS, DEFAULT_REPOS, DEFAULT_REPOS_CPP, CPP_EXTENSIONS_PATH,
  PACKAGE_NAMES)
from ntabuildtools.utils import filterRequirementsFile, pipInstall, subprocessCall



def installRequirements(repo, dryrun):
  pipInstall(filterRequirementsFile(repo), dryrun)



def executeBuild(repo, debug, debug_command, release_command,
                 make_command, install_command, dryrun):
  repoDir = os.path.expanduser("~/nta/{}".format(repo))

  if debug_command:
    debugDir = os.path.join(repoDir, "build", "scripts_debug")
    try:
      os.makedirs(debugDir)
    except OSError:
      pass

    print "Changing dir:", debugDir
    os.chdir(debugDir)

    debug_command = list(debug_command)
    debug_command.extend(CMAKE_EXTRA_OPTIONS[repo])
    debug_command.append(
        "-DPY_EXTENSIONS_DIR={}".format(CPP_EXTENSIONS_PATH[repo]))


    # Execute the build
    subprocessCall(debug_command, dryrun, checkCall=True)
    subprocessCall(make_command, dryrun, checkCall=True)

    if debug:
      # Install debug build
      subprocessCall(install_command, dryrun, checkCall=True)

  if release_command:
    releaseDir = os.path.join(repoDir, "build", "scripts_release")
    try:
      os.makedirs(releaseDir)
    except OSError:
      pass

    print "Changing dir:", releaseDir
    os.chdir(releaseDir)

    release_command = list(release_command)
    release_command.extend(CMAKE_EXTRA_OPTIONS[repo])
    release_command.append(
        "-DPY_EXTENSIONS_DIR={}".format(CPP_EXTENSIONS_PATH[repo]))

    subprocessCall(release_command, dryrun, checkCall=True)
    subprocessCall(make_command, dryrun, checkCall=True)

    if not debug:
      # Install release build
      subprocessCall(install_command, dryrun, checkCall=True)



def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "repos", metavar="repo", nargs="+", default=None,
      help="One or more of: {}. Or specify 'all' to build them all".format(
          ",".join(DEFAULT_REPOS_CPP)))
  parser.add_argument("-d", dest="debug", action="store_true",
                      help="copy the debug build into the Python project")
  parser.add_argument("-r", dest="debug", action="store_false",
                      help="copy the release build into the Python project")
  parser.set_defaults(debug=False)
  parser.add_argument("--build-both", action="store_true", default=False,
                      help=("build both debug and release, regardless of "
                            "which is being copied to the Python project"))
  parser.add_argument("--verbose", action="store_true",
                      help="get verbose output from cmake")
  parser.add_argument("--dryrun", action="store_true", default=False,
                      help="print the commands but don't execute them")
  parser.add_argument("-j", type=int, default=6,
                      help="number of make jobs to run in parallel")

  args = parser.parse_args()

  cmake_command = []
  if args.verbose:
    cmake_command.append("VERBOSE=1")

  cmake_command.extend([
    "cmake",
    "../..",
  ])

  if "all" in args.repos:
    repos = DEFAULT_REPOS_CPP
  else:
    repos = args.repos

  for repo in repos:
    if repo not in DEFAULT_REPOS:
      print "Unknown repo: '{}'. Specify one of: {}".format(
          repo, ", ".join(DEFAULT_REPOS_CPP + ["all"]))
      sys.exit(-1)
    if repo not in DEFAULT_REPOS_CPP:
      print "Repo '{}' has no C++ extensions, can't build.".format(repo)
      sys.exit(-1)

  if args.build_both or args.debug:
    debug_command = list(cmake_command)
    debug_command.extend([
      "-DCMAKE_INSTALL_PREFIX=../debug",
      "-DCMAKE_BUILD_TYPE=Debug",
      "-DNUPIC_IWYU=OFF",
    ])
  else:
    debug_command = None

  if args.build_both or not args.debug:
    release_command = list(cmake_command)
    release_command.extend([
      "-DCMAKE_INSTALL_PREFIX=../release",
      "-DCMAKE_BUILD_TYPE=Release",
      "-DNUPIC_IWYU=OFF",
    ])
  else:
    release_command = None

  make_command = ["make", "-j" + str(args.j)]
  install_command = ["make", "install"]

  for repo in repos:
    installRequirements(repo=repo, dryrun=args.dryrun)

    executeBuild(
      repo=repo, debug=args.debug, debug_command=debug_command,
      release_command=release_command, make_command=make_command,
      install_command=install_command, dryrun=args.dryrun)
