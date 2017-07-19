###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from ..serverlib import DataServer

import logging
import argh
import os

FMTSTR = "%(asctime)-15s %(levelname)-10s %(message)s"


###############################################################################
class FormatterWithoutTraceback(logging.Formatter):
    # -------------------------------------------------------------------------
    def formatException(self, exc_info):
        # --- the exc_info gets here already formatted and wrapped in a
        #     tuple to comply with how logging expects it
        return exc_info[0]


# -----------------------------------------------------------------------------
def run(logfile, address=None, mc_server=None):

    logging.getLogger().setLevel(logging.DEBUG)

    fh = logging.FileHandler(logfile, mode="w")
    fh.setFormatter(FormatterWithoutTraceback(FMTSTR))
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setFormatter(FormatterWithoutTraceback(FMTSTR))
    ch.setLevel(logging.INFO)

    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(ch)

    srv = DataServer(address, mc_server=mc_server)
    srv.start()


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run)


# -----------------------------------------------------------------------------
#  for interactive use
if __name__ == "__main__":
    root = os.getenv("TEMP", os.getenv("HOME", os.getenv("USERPROFILE")))
    logfile = os.path.join(root, "datafeed.log")
    run(logfile)
