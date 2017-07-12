# -*- coding: utf-8 -*-

import threading
from cherrypy.process.plugins import SimplePlugin
import pgpxmlrpc
from . import base, interfaces
import cherrypy
import logging
import uuid
import functools
from cherrybase import rpc, utils
import time
import sys
from .compat import unicode, PY3


def error_info ():
    e = sys.exc_info ()[1]
    if hasattr (e, 'args') and len (e.args) > 1:
        message = unicode (e.args [0])
        code = utils.to (int, e.args [1], 1)
    else:
        message = u'{}: {}'.format (type (e).__name__, str(e) if PY3 else str(e).decode('utf-8'))
        code = 1
    return (message, code)


class RpcAsyncProcess (object):
    
    def __init__ (self, owner, func, args, calltag, caller_key, cb_done, cb_error):
        self.owner = owner
        self.func = func
        self.cb_done = cb_done
        self.cb_error = cb_error
        self.calltag = calltag
        self.caller_key = caller_key
        
        self.gpg_homedir = base.config ('security.homedir', strict = True)
        self.gpg_key = base.config ('security.key', strict = True)
        self.gpg_password = base.config ('security.password', strict = True)
        self.request = cherrypy.request
        
        self.thread = threading.Thread (target = self.run, args = args)
    
    def callback (self, url, *res):
        uri, method = url.rsplit (':', 1)
        svc = pgpxmlrpc.Service (
            uri = uri,
            service_key = self.caller_key,
            gpg_homedir = self.gpg_homedir,
            gpg_key = self.gpg_key,
            gpg_password = self.gpg_password
        )
        for attr in method.split ('.'):
            svc = getattr (svc, attr)
        return svc (self.calltag, *res)
    
    def start (self):
        self.thread.start ()
    
    def stop (self):
        if self.thread.isAlive ():
            self.thread.join (timeout = 1)
        if self.thread.isAlive ():
            self.owner.bus.log ('Async handler still alive!', level = logging.WARNING)
        
    def run (self, *args):
        self.owner.bus.publish ('acquire_thread')
        try:
            cherrypy.log.error ('Async task started', 'RPCAsync')
            self.callback (self.cb_done, self.func (*args))
            cherrypy.log.error ('Async task done', 'RPCAsync')
        except Exception:
            try:
                if self.cb_error:
                    self.callback (self.cb_error, *error_info ())
            except:
                cherrypy.log.error ('Error while callback %s' % self.cb_error,
                    'RPCAsync', severity = logging.ERROR, traceback = True)
        try:
            del self.owner.threads [self.owner.threads.index (self)]
        except:
            pass
        
        self.owner.bus.publish ('release_thread')


class Request (object):
    
    def __init__ (self, key, uri, method, on_done, on_error, timeout):
        self.key = key
        self.uri = uri
        self.method = method
        self.on_done = on_done
        self.on_error = on_error
        self.timeout = time.time () + timeout
    
    def error (self, calltag, code, message):
        if self.on_error:
            self.on_error (calltag, code, message)
    
    def done (self, calltag, result):
        if self.on_done:
            self.on_done (calltag, result)
    
    def check (self):
        if time.time () >= self.timeout:
            self.error (-1, 'Call to %s:%s timed out' % (self.uri, self.method))
            return False
        return True


class RpcAsyncPlugin (SimplePlugin):

    def __init__ (self, bus, name = None):
        super (RpcAsyncPlugin, self).__init__ (bus)
        self.name = name or type (self).__name__
        self.threads = []
        self.requests = {}
    
    def get_calltag (self):
        while True:
            res = uuid.uuid4 ()
            if res not in self.requests:
                return str (res)
    
    def get_proxy (self, key, uri, method):
        res = pgpxmlrpc.Service (
            uri = uri,
            service_key = key,
            gpg_homedir = base.config ('security.homedir', strict = True),
            gpg_key = base.config ('security.key', strict = True),
            gpg_password = base.config ('security.password', strict = True),
        )        
        for attr in method.split ('.'):
            res = getattr (res, attr)
        return res

    def append (self, calltag, func, args, cb_done, cb_error):
        proc = RpcAsyncProcess (
            owner = self,
            func = func,
            args = args,
            calltag = calltag,
            caller_key = cherrypy.request.rco_client,
            cb_done = cb_done,
            cb_error = cb_error
        )
        self.threads.append (proc)
        proc.start ()
    
    def call (self, key, uri, method, on_done, on_error, tiemout, args):
        calltag = self.get_calltag ()
        app = cherrypy.request.app
        self.requests [calltag] = Request (key, uri, method, on_done, on_error, tiemout)
        self.get_proxy (key, uri, method)(
            calltag,
            app.service.url ('callback.done'),
            app.service.url ('callback.error'),
            *args
        )
        return calltag
    
    def stop (self):
        self.bus.log ('Stopping RpcAsyncPlugin...')
        for process in self.threads:
            process.stop ()
        self.bus.log ('Stopped RpcAsyncPlugin')
        

async_plugin = RpcAsyncPlugin (cherrypy.engine)
async_plugin.subscribe ()
        
        
def method (func):
    @functools.wraps (func)
    def _wrapped (*args):
        largs = list (args)
        if len (largs) < 4:
            raise RuntimeError ('Not enough arguments to call async RPC method')
        calltag, cb_done, cb_error = largs [1:4]
        del largs [1:4]
        async_plugin.append (calltag, func, largs, cb_done, cb_error)
    return _wrapped


class _CallHelper (object):
    
    def __init__ (self, owner, name):
        self.owner = owner
        self.name = name
    
    def __getattr__ (self, name):
        return _CallHelper (self.owner, '%s.%s' % (self.name, name))
    
    def __call__ (self, *args):
        return async_plugin.call (
            self.owner.key,
            self.owner.uri,
            self.name,
            self.owner.on_done,
            self.owner.on_error,
            self.owner.timeout,
            args
        )


class call (object):
    
    def __init__ (self, key, uri, on_done, on_error = None, timeout = 3600):
        self.key = key
        self.uri = uri
        self.on_done = on_done
        self.on_error = on_error
        self.timeout = timeout
    
    def __getattr__ (self, name):
        return _CallHelper (self, name)


class CallbackLib (interfaces.Namespace):
    
    def find_request (self, calltag):
        res = async_plugin.requests [calltag]
        if not res.key.startswith (cherrypy.request.rco_client) \
                and not cherrypy.request.rco_client.startswith (res.key):
            raise KeyError ('Client keys does not match')
        return res
    
    @rpc.expose
    def done (self, calltag, result):
        self.find_request (calltag).done (calltag, result)
    
    @rpc.expose
    def error (self, calltag, code, message):
        self.find_request (calltag).error (calltag, code, message)
        

def mount_lib (root):
    root.callback = CallbackLib ()

