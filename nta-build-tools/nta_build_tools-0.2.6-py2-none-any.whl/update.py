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

"""Tool for auto-updating Orthodoxy.

Execute `nta-update` to install the latest version of Orthodoxy.
"""

import argparse

from ntabuildtools.utils import subprocessCall



def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--dryrun", action="store_true", default=False,
                      help="print the commands but don't execute them")
  args = parser.parse_args()
  subprocessCall(
      ["curl", "-L",
       "http://releases.numenta.org/orthodoxy/latest/bootstrap.sh", "|",
       "bash"],
      dryrun=args.dryrun, checkCall=True)
