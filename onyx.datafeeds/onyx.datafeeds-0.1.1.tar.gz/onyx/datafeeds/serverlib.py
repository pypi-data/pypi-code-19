###############################################################################
#
#   Copyright: (c) 2017 Carlo Sbraccia
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
from onyx.core import Curve, CurveField
from onyx.core import HlocvCurve, HlocvCurveField
from onyx.core import GCurve, GCurveField

from .utils import encode_message, decode_message

from .exceptions import DatafeedError, SecurityError, FieldError
from .bloomberg import blp_api as bbg_api

from concurrent import futures

import tornado.ioloop
import tornado.tcpserver
import tornado.httpclient
import tornado.gen
import tornado.netutil

import json
import datetime
import socket
import urllib
import logging

__all__ = ["DataServer"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-15s %(levelname)-8s %(name)-32s %(message)s"
)
logger = logging.getLogger(__name__)

API_ERRORS = DatafeedError, SecurityError, FieldError, NotImplementedError
REREGISTER = 60000*2  # check registration every 2 minutes


# -----------------------------------------------------------------------------
def process_request(timeout, request, request_type):
    """
    This function processes requests based on the request type. Currently it
    only support BDP and BDH bloomberg requests.
    """
    # --- decode overrides which are sent by clients as json strings
    if request["overrides"] is not None:
        request["overrides"] = json.loads(request["overrides"])

    try:
        if request_type == "BDP":
            data = bbg_api.BbgBDP(timeout=timeout, **request)
        elif request_type == "BDH":
            data = bbg_api.BbgBDH(timeout=timeout, **request)
    except API_ERRORS as err:
        data = err
        del err

    if isinstance(data, Curve):
        data_type = "Curve"
        data = CurveField.to_json(None, data)
    elif isinstance(data, HlocvCurve):
        data_type = "HlocvCurve"
        data = HlocvCurveField.to_json(None, data)
    elif isinstance(data, GCurve):
        data_type = "GCurve"
        data = GCurveField.to_json(None, data)
    elif isinstance(data, Exception):
        data_type = type(data).__name__
        data = str(data)
    else:
        data_type = type(data).__name__

    return {
        "type": data_type,
        "payload": data,
    }


###############################################################################
class DataServer(tornado.tcpserver.TCPServer):
    # -------------------------------------------------------------------------
    def __init__(self, nthreads=5, timeout=1):
        super().__init__()
        self.executor = futures.ThreadPoolExecutor(max_workers=nthreads)
        self.timeout = datetime.timedelta(seconds=timeout)

    # -------------------------------------------------------------------------
    def start(self, router_addr=None, router_port=None):
        config = load_system_configuration()
        router_addr = router_addr or config.get("datafeed", "router_address")
        router_port = router_port or config.getint("datafeed", "router_port")

        # --- connect to a random port from the available pool
        sockets = tornado.netutil.bind_sockets(0, address="")
        self.add_sockets(sockets)

        # --- get the port and add a callback to notify periodically that
        #     this server is available
        port = sockets[0].getsockname()[1]

        # --- create the request object used to notify the router that this
        #     server is available
        self.subreq = tornado.httpclient.HTTPRequest(
            "http://{0!s}:{1!s}/register/".format(router_addr, router_port),
            method="PUT",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urllib.parse.urlencode({
                "address": socket.gethostbyname(socket.gethostname()),
                "port": port}),
            request_timeout=self.timeout.seconds
        )

        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback(self.subscribe_to_router)
        tornado.ioloop.PeriodicCallback(
                          self.subscribe_to_router, REREGISTER, ioloop).start()

        try:
            ioloop.start()
        except KeyboardInterrupt:
            ioloop.stop()
        finally:
            self.cleanup()

    # -------------------------------------------------------------------------
    def cleanup(self):
        logger.info("shutting down server")

    # -------------------------------------------------------------------------
    @tornado.gen.coroutine
    def with_timeout(self, future):
        generator = yield tornado.gen.with_timeout(self.timeout, future)
        return generator

    # -------------------------------------------------------------------------
    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        logger.debug("connection received from {0!s}".format(address))

        try:
            request = yield self.with_timeout(stream.read_until(b"\n"))
        except (tornado.iostream.StreamClosedError, tornado.gen.TimeoutError):
            logger.error("couldn't read request from {0!s}".format(address))
            return

        request = decode_message(request)
        logger.info("processing request {0!s}".format(request))
        request_type = request.pop("type")

        # --- try processing the request for a maximum of 5 times using
        #     geometrically increasing timeouts
        t = self.timeout.seconds * 1000  # to milliseconds
        for k in range(5):
            logger.debug("timeout set to {0:d}".format(t))
            try:
                response = yield self.executor.submit(process_request,
                                                      t, request, request_type)
                break
            except TimeoutError:
                t *= 2
        else:
            t /= 2
            response = {
                "type": "TimeoutError",
                "payload": ("request timed out after 5 attempts with a "
                            "final timeout of {0!s} milliseconds").format(t),
            }

        response = encode_message(response)

        try:
            yield self.with_timeout(stream.write(response))
        except (tornado.gen.TimeoutError, tornado.iostream.StreamClosedError):
            logger.error("couldn't send response to {0!s}".format(address))
            return

    # -------------------------------------------------------------------------
    @tornado.gen.coroutine
    def subscribe_to_router(self):
        # --- register only if bloomberg service is available
        active = bbg_api.test_bbg_data_service()
        if not active:
            logger.info("couldn't register server with router: "
                        "bloomberg service currently unavailable")
            return

        logger.debug("trying to register with "
                     "datafeed router on {0!s}".format(self.subreq.url))

        client = tornado.httpclient.AsyncHTTPClient()
        try:
            res = yield client.fetch(self.subreq)
        except ConnectionRefusedError:
            logger.info("couldn't register with datafeed router on "
                        "{0!s}: connection refused".format(self.subreq.url))
            return
        except tornado.httpclient.HTTPError as err:
            logger.info("couldn't register with datafeed router "
                        "on {0!s}: {1!s}".format(self.subreq.url, err))
            return

        if res.code == 201:
            logger.info("router accepted subscription")
        elif res.code == 205:
            # --- server already registered with router
            pass
        else:
            raise res.error
