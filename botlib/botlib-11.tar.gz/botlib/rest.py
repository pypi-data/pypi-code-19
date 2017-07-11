# botlib/rest.py
#
# Copyright 2016,2017 Bart Thate
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# * As the creator of this piece of software, Bart Thate, i disclaim all rights on the code contained in this software package.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

""" rest interface. """

from .object import Object

import http.server
import logging
import botlib
import http
import time
import os

def init(event):
    from .space import cfg, kernel
    global server
    try:
        server = REST(("localhost", int(cfg.port) or 10102), RESTHandler)
    except OSError as ex:
        logging.error("rest error: %s" % str(ex))
        return        
    kernel.launch(server.start)
    return server

def shutdown(event):
    from .space import runtime
    rest = runtime.get("REST", [])
    for object in rest:
        object.exit()

class REST(http.server.HTTPServer, Object):

    allow_reuse_address = True
    daemon_thread = True
    path = os.path.join("runtime", "rest")

    def __init__(self, *args, **kwargs):
        http.server.HTTPServer.__init__(self, *args, **kwargs)
        Object.__init__(self)
        self.host = args[0]
        self._last = time.time()
        self._starttime = time.time()
        self._status = "start"

    def exit(self):
        self._status = ""

    def start(self):
        from .space import launcher, runtime
        logging.info("! rest http://%s:%s" % self.host)
        self._status = "ok"
        runtime.register("REST", self)
        self.ready()
        launcher.launch(self.serve_forever, name="REST.server")

    def request(self):
        self._last = time.time()

    def error(self, request, addr):
        logging.info('! error rest %s %s' % (request, addr))

class RESTHandler(http.server.BaseHTTPRequestHandler):

    def setup(self):
        http.server.BaseHTTPRequestHandler.setup(self)
        self._ip = self.client_address[0]
        self._size = 0

    def write_header(self, type='text/plain'):
        self.send_response(200)
        self.send_header('Content-type', '%s; charset=%s ' % (type, "utf-8"))
        self.send_header('Server', botlib.__version__)
        self.end_headers()

    def do_GET(self):
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
        logging.info('! log rest %s code %s path %s' % (self.address_string(), code, self.path))
