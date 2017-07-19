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

from onyx.core import Date, load_system_configuration
from .exceptions import DatafeedFatal

# from .bloomberg import com_api as bbg_api
from .bloomberg import blp_api as bbg_api

from collections import namedtuple

import logging
import zmq
import threading
import multiprocessing
import time
import traceback
import memcache
import hashlib

__all__ = ["DataServer"]

NPROCS = 4  # number of worker processes
LOCK_TIMEOUT = 10  # in seconds
RT_TIMEOUT = 120  # in seconds

SORTED_KEYS = ["securities", "security", "fields",
               "start", "end", "adj", "overrides", "type", "RT"]

# --- define a convenience namedtuple that represents log messages
logmsg = namedtuple("logmsg", "level wid msg exc_info extra")


###############################################################################
class CacheLocked(object):
    __slots__ = ()


###############################################################################
class logmsg_pusher(object):
    # -------------------------------------------------------------------------
    def __init__(self, url):
        self.socket = zmq.Context().socket(zmq.PUSH)
        self.socket.connect(url)

    # -------------------------------------------------------------------------
    def info(self, wid, msg, exc_info=None, extra=None):
        if exc_info is not None:
            # --- send the exception/traceback printout rather than the objects
            #     themselves
            exc_info = (traceback.format_exc(), )
        self.socket.send_pyobj(logmsg("info", wid, msg, exc_info, extra))

    # -------------------------------------------------------------------------
    def debug(self, wid, msg, exc_info=None, extra=None):
        if exc_info is not None:
            # --- send the exception/traceback printout rather than the objects
            #     themselves
            exc_info = (traceback.format_exc(), )
        self.socket.send_pyobj(logmsg("debug", wid, msg, exc_info, extra))

    # -------------------------------------------------------------------------
    def warning(self, wid, msg, exc_info=None, extra=None):
        if exc_info is not None:
            # --- send the exception/traceback printout rather than the objects
            #     themselves
            exc_info = (traceback.format_exc(), )
        self.socket.send_pyobj(logmsg("warning", wid, msg, exc_info, extra))

    # -------------------------------------------------------------------------
    def critical(self, wid, msg, exc_info=None, extra=None):
        if exc_info is not None:
            # --- send the exception/traceback printout rather than the objects
            #     themselves
            exc_info = (traceback.format_exc(), )
        self.socket.send_pyobj(logmsg("critical", wid, msg, exc_info, extra))


# -----------------------------------------------------------------------------
def listen_forever(wid, socket, cache, timeout, logger):
    logger.info(wid, "listening for incoming requests")

    while True:
        request = socket.recv_pyobj()

        logger.debug(wid, "request {0!r} "
                     "received from client".format(request))

        # --- serialize request making sure we always get the same key for the
        #     same request (NB: the request is a dictionary which means
        #     ordering is not guaranteed).
        req_key = "".join(["({0!s},{1!s})".format(k, request.get(k, None))
                           for k in SORTED_KEYS])
        req_key = hashlib.sha1(req_key.encode("utf-8")).hexdigest()
        req_args = [request.get(key, None) for key in SORTED_KEYS
                    if request.get(key, None) is not None]
        log_format_string = "{{0:>8s}} {0!r}:".format(req_args)

        while True:
            resp = cache.get(req_key)
            if not isinstance(resp, CacheLocked):
                break
            time.sleep(0.25)

        if resp is None:
            logger.info(wid, log_format_string.format("missing"))
            logger.debug(wid, "key '{0:s}' "
                         "not found in memcache".format(req_key))

            cache.set(req_key, CacheLocked(), LOCK_TIMEOUT)
            req_type = request.pop("type")
            real_time = request.pop("RT", False)

            # --- here we choose the proper handler based on the request type
            if req_type == "BDP":
                fetch_result = bbg_api.BbgBDP
            elif req_type == "BDH":
                fetch_result = bbg_api.BbgBDH
            else:
                raise ValueError("Unrecognized "
                                 "request type {0:s}".format(req_type))

            # --- to avoid memory leaks it is important to call
            #     traceback.clear_frames whenever we break the exception chain
            #     by returning exceptions. traceback.clear_frames will remove
            #     local variables and will clear reference cycles.
            try:
                # --- run a maximum of 5 attempts increasing timeout by a
                #     factor 2 each time
                t = timeout
                for k in range(5):
                    try:
                        resp = fetch_result(timeout=t, **request)
                        break
                    except TimeoutError:
                        t *= 2
                else:
                    raise TimeoutError("request timed out after "
                                       "5 attempts with a final timeout "
                                       "of {0:d} milliseconds".format(t))

            except DatafeedFatal:
                # --- in case of a Bloomberg critical error (i.e. cannot
                #     connect to bloomberg service) log exception and return
                logger.critical(wid, "skipping request "
                                "on DatafeedFatal", exc_info=True)
                return

            except Exception as err:
                err.exc_info = traceback.format_exc()
                resp = err
                traceback.clear_frames(err.__traceback__)

            else:
                # --- we only cache if there were no errors
                logger.debug(wid, "query to bloomberg completed successfully")

                if real_time:
                    expiry = RT_TIMEOUT
                else:
                    expiry = Date.today().eod().timestamp()

                cache.set(req_key, resp, expiry)

        else:
            logger.info(wid, log_format_string.format("cached"))

        try:
            socket.send_pyobj(resp, flags=zmq.NOBLOCK)
            logger.debug(wid, "response sent to client")
        except:
            logger.critical(wid, "failed to send "
                            "response to client", exc_info=True)


# -----------------------------------------------------------------------------
def worker(wid, conn_str, mc_servers, timeout):
    # --- connect to master logger
    logger = logmsg_pusher("tcp://127.0.0.1:10001")
    logger.info(wid, "booting up...")

    # --- initialize memcached client
    cache = memcache.Client(mc_servers)

    while True:
        # --- make sure bloomberg service is available
        active = bbg_api.test_bbg_data_service()
        if not active:
            logger.info(wid, "bloomberg service unavailable, sleeping...")
            time.sleep(120)
            continue

        # --- connect to bloomberg data queue
        socket = zmq.Context().socket(zmq.REP)
        socket.connect(conn_str)

        # --- listen for requests
        try:
            listen_forever(wid, socket, cache, timeout, logger)
        finally:
            # --- always close the socket so that datafeed router is aware that
            #     the worker is no longer available.
            socket.close()


###############################################################################
class DataServer(object):
    # -------------------------------------------------------------------------
    def __init__(self, address=None, port=None, mc_server=None, timeout=None):

        config = load_system_configuration()

        address = address or config.get("datafeed", "queue_address")
        port = port or config.getint("datafeed", "dealer_port")

        if mc_server is None:
            self.mc_servers = [config.get("memcache", "url")]
        else:
            self.mc_servers = [mc_server]

        self.conn_str = "tcp://{0:s}:{1:d}".format(address, port)
        self.timeout = timeout or config.getint("datafeed", "timeout")

    # -------------------------------------------------------------------------
    def master_logger(self):
        logger = logging.getLogger(__name__)
        logger.info("starting master logger")

        socket = zmq.Context().socket(zmq.PULL)
        socket.bind("tcp://127.0.0.1:10001")

        while True:
            loginfo = socket.recv_pyobj()
            try:
                log_method = getattr(logger, loginfo.level)
            except AttributeError:
                # FIXME: do something better here
                raise
            else:
                msg = "worker {0:2d} - {1!s}".format(loginfo.wid, loginfo.msg)
                try:
                    log_method(msg,
                               exc_info=loginfo.exc_info, extra=loginfo.extra)
                except:
                    # FIXME: do something better here too
                    print(traceback.print_exc())
                    pass

    # -------------------------------------------------------------------------
    def start(self):
        logger = logging.getLogger(__name__)
        logger.info("DataServer started, "
                    "listening on {0:s}".format(self.conn_str))

        # --- start master-logger in a dedicated thread
        thread = threading.Thread(target=self.master_logger)
        thread.daemon = True
        thread.start()

        while True:
            # --- launch pool of worker processes
            procs = []
            for k in range(NPROCS):
                args = (k, self.conn_str, self.mc_servers, self.timeout)
                proc = multiprocessing.Process(target=worker, args=args)
                proc.daemon = True
                proc.start()
                procs.append(thread)

            for proc in procs:
                proc.join()

            logger.info("DataServer: all workers have been stopped...")

        logger.info("DataServer stopped")
