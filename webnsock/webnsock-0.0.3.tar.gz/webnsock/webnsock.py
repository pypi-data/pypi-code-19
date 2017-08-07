#!/usr/bin/env python
import web  # http.server
from os import chdir, path
import signal
import time
import posixpath
import os
import urllib
from json import loads, dumps
from logging import error, warn, info, debug, basicConfig, INFO
from pprint import pformat
from threading import Thread, Condition
from uuid import uuid4
from web.httpserver import StaticMiddleware, LogMiddleware, StaticApp

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

basicConfig(level=INFO)

# TEMPLATE_DIR = path.realpath(
#     path.join(
#         path.dirname(__file__),
#         'www'
#     )
# )


# html_config = {
#     'websocket_suffix': ':9090',
# }



class JsonWSProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        info("WebSocket connection open.")
        self.wait_responses = {}

    def sendJSON(self, data, callback=None):
        data = data.copy()
        data['_id'] = str(uuid4())
        if callback:
            self.wait_responses[data['_id']] = callback
        buf = dumps(data)
        self.sendMessage(buf.encode('utf-8'), False)

    def onMessage(self, payload, isBinary):
        # Debug
        if isBinary:
            warn("Binary message received: {0} bytes".format(len(payload)))
        else:
            debug("Text message received: {0}".format(payload.decode('utf8')))
            message_text = payload.decode('utf8')
            payload = loads(message_text)
            debug(pformat(payload))
            result = self._dispatch(payload)
            if result:
                try:
                    r = result.copy()
                    r['_response_to'] = payload['_id']
                    r['_query'] = payload
                    self.sendJSON(r)
                except Exception as e:
                    warn('Exception: %s', str(e))

    def _dispatch(self, payload):
        if 'method' in payload:
            method = payload['method']
            try:
                method_to_call = getattr(self, 'on_%s' % method)
                info('dispatch to method on_%s' % method)
            except AttributeError:
                warn('cannot dispatch method %s' % method)
                return
            return method_to_call(payload)
        elif '_response_to' in payload:
            if payload['_response_to'] in self.wait_responses:
                info('got a response we have been waiting for')
                method = self.wait_responses.pop(payload['_response_to'])
                method(payload)

            info('got a response to %s for method %s' %
                 (payload['_response_to'], payload['_query']['method']))
        else:
            warn("don't know what to do with message %s" % pformat(payload))


    #@abstractmethod
    def onJSON(self, payload):
        warn('should not work')

    def onClose(self, wasClean, code, reason):
        info("WebSocket connection closed: {0}".format(reason))


class EchoJSONProtocol(JsonWSProtocol):
    def onJSON(self, payload):
        info('echo called')
        return payload



class WSBackend(object):

    def __init__(self, protocol=EchoJSONProtocol):
        self.protocol = protocol

    def wait_until_shutdown(self, loop):
        self.is_running = True
        info('backend is running')
        while self.is_running:
            try:
                time.sleep(.1)
                yield
            except KeyboardInterrupt:
                info("shutdown")
                break
        loop.stop()

    def stop(self):
        self.is_running = False

    def talker(self, port=8128):
        factory = WebSocketServerFactory(u"ws://0.0.0.0:%d" % port)
        factory.protocol = self.protocol

        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_server(factory, '0.0.0.0', port)
        server = self.loop.run_until_complete(coro)
        asyncio.async(self.wait_until_shutdown(self.loop))

        #signal.signal(signal.SIGINT, self.signal_handler)
        self.loop.run_forever()

        info("Closing...")
        server.close()

        self.loop.run_until_complete(server.wait_closed())
        self.loop.close()


class FlexStaticApp(StaticApp):

    def __init__(self, environ, start_response, root=None):
        if root is None:
            self._root = os.getcwd()
        else:
            self._root = root

        try:
            StaticApp.__init__(
                self,
                environ, start_response
            )
        except Exception as e:
            print "INIT failed: ", self._root, e

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        # This the new way to NOT only work in CWD
        path = self._root
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path


class FlexStaticMiddleWare(StaticMiddleware):

    def __init__(self, app, prefix='/static/', root=None):
        self._root = root
        StaticMiddleware.__init__(
            self,
            app, prefix
        )
        # super(FlexStaticMiddleWare, self).__init__(
        #     app, prefix)

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        path = self.normpath(path)

        if path.startswith(self.prefix):
            return FlexStaticApp(environ, start_response, root=self._root)
        else:
            return self.app(environ, start_response)


class WebServer(web.auto_application):

    def __init__(self, add_static=None, static_prefix='/'):

        self._template_dir = None
        self._static_prefix = static_prefix
        self._renderer = web.template.render(
            path.realpath(
                path.join(
                    path.dirname(__file__),
                    'www/webnsock'
                )
            ),
            base='base', globals=globals())
        self._static_dirs = set([])

        self.add_static_dir(
            path.join(
                path.dirname(__file__),
                'www/webnsock'
            )
        )

        if add_static is not None:
            self.add_static_dir(
                path.join(
                    add_static
                )
            )

        web.auto_application.__init__(self)

        # self_app = self

        # class Index(self.page):
        #     path = '/'

        #     def GET(self):
        #         return self_app.render.index({})

    def add_static_dir(self, dir_name):
        self._static_dirs.add(
            path.realpath(dir_name)
        )

    def run(self, port=8027, *middleware):
        global server
        info('NEW webserver running.')
        func = self.wsgifunc(*middleware)
        for s in self._static_dirs:
            print 'add %s as static path' % s
            func = FlexStaticMiddleWare(
                func, prefix=self._static_prefix + os.path.basename(s),
                root=os.path.dirname(s)
            )
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

        # func = StaticMiddleware(func)
        # func = LogMiddleware(func)
        # server_address = ('0.0.0.0', port)

        # server = WSGIServer(server_address, func)

        # if server.ssl_adapter:
        #     print "https://%s:%d/" % server_address
        # else:
        #     print "http://%s:%d/" % server_address

        # try:
        #     server.start()
        # except (KeyboardInterrupt, SystemExit):
        #     server.stop()
        #     server = None
        # return False


class Webserver(Thread):

    def __init__(self, app, port=8127):
        self.app = app
        self.port = port

        super(Webserver, self).__init__()

    def run(self):
        info("Webserver started.")
        self.app.run(port=self.port)
        info("Webserver stopped.")

    def stop(self):
        self.app.stop()


def signal_handler(webserver, backend, signum, frame):
    info('shutdown triggered')
    webserver.stop()
    info('webserver shutdown')
    backend.stop()
    info('backend shutdown')


def main():
    webserver = Webserver(WebServer())
    backend = WSBackend(EchoJSONProtocol)
    signal.signal(signal.SIGINT,
                  lambda s, f: signal_handler(webserver, backend, s, f))
    webserver.start()
    backend.talker()


if __name__ == "__main__":
    main()


