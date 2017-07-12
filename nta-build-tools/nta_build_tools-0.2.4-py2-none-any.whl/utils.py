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

"""Utility functions."""

import collections
import os
import subprocess
from ntabuildtools.repos import REQUIREMENTS



def subprocessCall(command, dryrun, checkCall=False, shell=True, env=None):
  """Execute command in a subprocess.

  :param command: the command to execute. E.g. `["ls", "-l"]`
  :param dryrun: Boolean. If true, print command without executing it.
  :param checkCall: if true, raise exception on non-zero exit code
  :param shell: boolean whether to run command in a shell
  """
  assert (not isinstance(command, str) and
          isinstance(command, collections.Sequence))

  if env:
    envPrefix = " ".join("=".join((key, value)) for key, value in env.items()) + " "
    env = dict(os.environ.items() + env.items())
  else:
    envPrefix = ""
    env = os.environ.copy()

  if dryrun:
    print "Would execute: {}{}".format(envPrefix, " ".join(command))
  else:
    print "Executing: {}{}".format(envPrefix, " ".join(command))
    command = " ".join(command)
    if checkCall:
      return subprocess.check_call(command, shell=shell, env=env)
    else:
      return subprocess.call(command, shell=shell, env=env)



def pipInstall(args, dryrun, env=None):
  subprocessCall(["pip", "install", "--user"] + list(args),  dryrun,
                 checkCall=True, env=env)



def pipUninstall(args, dryrun):
  subprocessCall(["pip", "uninstall", "-y"] + list(args), dryrun, checkCall=True)



def filterRequirementsFile(repo):
  with open(REQUIREMENTS[repo]) as inp:
    return [
      line.strip() for line in inp
      if not line.startswith("#") and
         "nupic" not in line and
         "htmresearch" not in line
    ]
