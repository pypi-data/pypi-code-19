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

from onyx.core import load_system_configuration

import logging
import zmq
import argh

fmtstr = "%(asctime)-15s %(levelname)-8s %(message)s"

logging.basicConfig(level=logging.DEBUG, format=fmtstr)


# -----------------------------------------------------------------------------
def DataQueueDevice(router_addr="*", dealer_addr="*",
                    router_port=None, dealer_port=None):
    """
    Description:
        A queue device used to connect clients and servers.
    """
    logger = logging.getLogger(__name__)
    config = load_system_configuration()

    router_port = router_port or config.getint("datafeed", "router_port")
    dealer_port = dealer_port or config.getint("datafeed", "dealer_port")

    context = zmq.Context()

    try:
        # --- client-facing socket
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("tcp://{0:s}:{1:d}".format(router_addr, router_port))
    except:
        logger.critical("error establishing "
                        "client-facing connection", exc_info=True)
        raise

    try:
        # --- services-facing socket
        backend = context.socket(zmq.DEALER)
        backend.bind("tcp://{0:s}:{1:d}".format(dealer_addr, dealer_port))
    except:
        logger.critical("error establishing "
                        "services-facing connection", exc_info=True)
        raise

    logger.info("DataQueueDevice started")

    try:
        zmq.device(zmq.QUEUE, frontend, backend)
    except:
        logger.critical("top level exception", exc_info=True)
    finally:
        logger.info("DataQueueDevice shutting down")
        frontend.close()
        backend.close()
        context.term()


# -----------------------------------------------------------------------------
def run(router_addr="*", dealer_addr="*"):
    DataQueueDevice(router_addr, dealer_addr)


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run)


# -----------------------------------------------------------------------------
#  for interactive use
if __name__ == "__main__":
    run()
