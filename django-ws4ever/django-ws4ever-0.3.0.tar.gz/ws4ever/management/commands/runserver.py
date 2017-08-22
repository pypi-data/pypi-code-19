

import errno
import os
import socket
import sys
from datetime import datetime

import gevent
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.management.commands.runserver import Command as RunserverCommand
from django.utils import autoreload
from django.utils.encoding import force_text
from geventwebsocket import Resource, WebSocketServer

from ws4ever.helpers import get_websocket_resources

def get_server(addr, port, wsgi_handler):
    resources = get_websocket_resources()
    resources.append(('^/.*', wsgi_handler))
    return WebSocketServer((addr, port), Resource(resources))


def run(addr, port, wsgi_handler):
    server = get_server(addr, port, wsgi_handler)
    g = gevent.spawn(server.serve_forever)
    gevent.joinall([g])


class Command(RunserverCommand):
    def add_arguments(self, parser):
        # remove threading from origin code
        parser.add_argument(
            'addrport', nargs='?',
            help='Optional port number, or ipaddr:port'
        )
        parser.add_argument(
            '--ipv6', '-6', action='store_true', dest='use_ipv6', default=False,
            help='Tells Django to use an IPv6 address.',
        )
        parser.add_argument(
            '--noreload', action='store_false', dest='use_reloader', default=True,
            help='Tells Django to NOT use the auto-reloader.',
        )

    def get_handler(self, *args, **options):
        # add static file handler
        handler = super(Command, self).get_handler(*args, **options)
        return StaticFilesHandler(handler)

    def inner_run(self, *args, **options):
        # origin code ----------------
        autoreload.raise_last_exception()

        # 'shutdown_message' is a stealth option.
        shutdown_message = options.get('shutdown_message', '')
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'

        self.stdout.write("Performing system checks...\n\n")
        self.check(display_num_errors=True)

        # Need to check migrations here, so can't use the
        # requires_migrations_check attribute.
        self.check_migrations()
        now = datetime.now().strftime('%B %d, %Y - %X')
        self.stdout.write(now)
        self.stdout.write(
            (
                "Django version %(version)s, using settings %(settings)r\n"
                "Starting development server at http://%(addr)s:%(port)s/\n"
                "Quit the server with %(quit_command)s.\n"
            ) % {
                "version": self.get_version(),
                "settings": settings.SETTINGS_MODULE,
                "addr": '[%s]' % self.addr if self._raw_ipv6 else self.addr,
                "port": self.port,
                "quit_command": quit_command,
            }
        )
        # origin code ends ----------------
        try:
            run(self.addr, int(self.port), self.get_handler())

        # origin code to end -------------------
        except socket.error as e:
            # Use helpful error messages instead of ugly tracebacks.
            errors = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned to.",
            }
            try:
                error_text = errors[e.errno]
            except KeyError:
                error_text = force_text(e)
            self.stderr.write("Error: %s" % error_text)
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)
