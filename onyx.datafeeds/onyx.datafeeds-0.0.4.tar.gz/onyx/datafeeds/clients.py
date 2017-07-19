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

from onyx.core import Curve, HlocvCurve, Date, load_system_configuration

import threading
import traceback
import zmq
import datetime

__all__ = ["DataClient"]

REQUEST_TIMEOUT = 20000  # in milliseconds
REQUEST_RETRIES = 3


###############################################################################
class DataClient(object):
    """
    This is a blocking client.
    """
    # -------------------------------------------------------------------------
    def __init__(self, address=None, port=None):
        config = load_system_configuration()

        address = address or config.get("datafeed", "queue_address")
        port = port or config.getint("datafeed", "router_port")

        self.endpoint = "tcp://{0:s}:{1:d}".format(address, port)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.endpoint)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.lock = threading.Lock()

    # -------------------------------------------------------------------------
    def query(self, request):
        # --- send request in blocking mode (required to make it thread safe)
        with self.lock:
            # --- use lazy-pirate pattern to manage unresponsive server
            resp = self.lazy_pirate(request)

        if isinstance(resp, Exception):
            err_msg = ("Request {0!s} failed.\n\nFull "
                       "traceback is:\n\n{1:s}").format(request, resp.exc_info)

            try:
                raise resp.__class__(err_msg) from resp
            finally:
                traceback.clear_frames(resp.__traceback__)

        else:
            return resp

    # -------------------------------------------------------------------------
    def lazy_pirate(self, request):
        retries_left = REQUEST_RETRIES
        while retries_left:
            self.socket.send_pyobj(request)

            sockets = dict(self.poller.poll(REQUEST_TIMEOUT))

            if sockets.get(self.socket) == zmq.POLLIN:
                return self.socket.recv_pyobj()

            else:
                self.socket.setsockopt(zmq.LINGER, 0)
                self.socket.close()
                self.poller.unregister(self.socket)

                retries_left -= 1

                self.socket = self.context.socket(zmq.REQ)
                self.socket.connect(self.endpoint)
                self.poller.register(self.socket, zmq.POLLIN)

        raise TimeoutError("server not responding...")

    # -------------------------------------------------------------------------
    def BDP(self, sec, field, overrides=None, RT=False):
        # --- make sure security and field names are upper case as the hashing
        #     is case sensitive
        sec = sec.upper()
        field = field.upper()

        # --- if overrides is specified, convert it to a tuple of tuples to
        #     make it hashable
        if overrides is not None:
            overrides = tuple([(k, v) for k, v in overrides.items()])

        resp = self.query({"securities": sec, "fields": field,
                           "overrides": overrides, "type": "BDP", "RT": RT})
        return resp[sec][field]

    # -------------------------------------------------------------------------
    def BDH(self, sec, fields, sd, ed, adj=True):
        # --- convert sd, ed to a datetime.date to facilitate caching of
        #     equivalent queries
        sd = sd.date() if isinstance(sd, datetime.datetime) else sd
        ed = ed.date() if isinstance(ed, datetime.datetime) else ed

        # --- make sure security and field names are upper case as the hashing
        #     is case sensitive
        sec = sec.upper()
        fields = (fields.upper() if isinstance(fields, str)
                  else tuple([field.upper() for field in fields]))
        today = Date.today()

        request = {
            "security": sec,
            "fields": fields,
            "start": sd,
            "end": ed,
            "adj": adj,
            "type": "BDH",
        }

        # --- two cases:
        #     1) the reqested end date is before today: only looking for
        #        historical data, we can used cached data for the whole time
        #        series.
        #     2) the reqested end date is today or in the future: we can use
        #        cached data for the time series, but need to overwrite today's
        #        value with realtime.
        if ed < today:
            # --- create request object and send request
            return self.query(request)

        else:
            # --- request the timeseries as a curve (this request gets cached
            #     for the day)
            crv = self.query(request)

            # --- if the curve is empty, return immediately
            if not len(crv):
                return crv

            if fields == "HLOCV":
                fields = ("PX_HIGH", "PX_LOW", "PX_OPEN", "PX_LAST", "VOLUME")

            # --- request current realtime value
            curr_val = self.query({"securities": sec,
                                   "fields": fields, "type": "BDP"})
            curr_val = curr_val[sec]

            if isinstance(crv, Curve):
                if isinstance(fields, str):
                    crv[today] = curr_val[fields]
                else:
                    raise ValueError("Unexpected curve type: {0!s} for "
                                     "{1!s}".format(crv.__class__, fields))
            elif isinstance(crv, HlocvCurve):
                crv[today] = [curr_val[field] for field in fields]
            else:
                raise ValueError("Unexpected curve type: "
                                 "{0!s}".format(crv.__class__))

            return crv
