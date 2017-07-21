# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" rest interface. """

from .object import Object

import botlib
import http
import http.server
import os
import logging
import time

def init(*args, **kwargs):
    """ initialise the REST server. """
    from .space import cfg, launcher
    try:
        serv = REST(("localhost", int(cfg.port) or 10102), RESTHandler)
    except OSError as ex:
        logging.error("rest error: %s" % str(ex))
        return
    launcher.launch(serv.start)
    return serv

def shutdown(event):
    """ stop the REST server. """
    from .space import runtime
    rest = runtime.get("REST", [])
    for obj in rest:
        obj.exit()

class REST(http.server.HTTPServer, Object):

    """
        This REST server serves JSON string from a path into the workdir.
        This makes all data objects accessible through the HTTP server.

    """

    allow_reuse_address = True
    daemon_thread = True
    path = os.path.join("runtime", "rest")

    def __init__(self, *args, **kwargs):
        http.server.HTTPServer.__init__(self, *args, **kwargs)
        Object.__init__(self)
        self.host = args[0]
        self._last = time.time()
        self._starttime = time.time()
        self._stopped = False

    def exit(self):
        """ stop the server. """
        self._status = ""

    def server(self):
        """ blocking loop of the server. """
        self.serve_forever()

    def start(self):
        """ start the server. """
        from .space import launcher, runtime
        logging.info("! rest http://%s:%s" % self.host)
        self._state.status = "running"
        runtime.register("REST", self)
        self.ready()
        launcher.launch(self.serve_forever)

    def request(self):
        """ called upon receiving a request. """
        self._last = time.time()

    def error(self, request, addr):
        """ log an error. """
        logging.info('! error rest %s %s' % (request, addr))

class RESTHandler(http.server.BaseHTTPRequestHandler):

    """ REST request handler, serves response to REST requests. """

    def setup(self):
        """ setup the handler upon receiving a request. """
        http.server.BaseHTTPRequestHandler.setup(self)
        self._ip = self.client_address[0]
        self._size = 0

    def write_header(self, typestr='text/plain'):
        """ write the standard header before sending data. """
        self.send_response(200)
        self.send_header('Content-type', '%s; charset=%s ' % (typestr, "utf-8"))
        self.send_header('Server', botlib.__version__)
        self.end_headers()

    def do_GET(self):
        """ serve a GET request. """
        from .space import cfg
        fn = cfg.workdir + os.sep + self.path
        try:
            f = open(fn, "r")
            txt = f.read()
            f.close()
        except (TypeError, FileNotFoundError, IsADirectoryError):
            self.send_response(404)
            self.end_headers()
            return
        txt = txt.replace("\\n", "\n")
        txt = txt.replace("\\t", "\t")
        self.write_header()
        self.wfile.write(bytes(txt, "utf-8"))
        self.wfile.flush()

    def log(self, code):
        """ log a request. """
        logging.info('! rest %s code %s path %s' % (self.address_string(), code, self.path))
