# NFQ Logwrapper. A tool for centralizing and visualizing logs.
# Copyright (C) 2017 Guillem Borrell Nogueras
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import zmq
import json
import logging

from datetime import datetime
from tornado import web
from functools import partial
from zmq.eventloop import ioloop, zmqstream
from tornado.options import options

from nfq.logwrapper.db import engine, Base, LogEntry, session
# Global variables for cached content. Linters will say it is not used.
from nfq.logwrapper.db import clients
from nfq.logwrapper.config import root_path
from nfq.logwrapper.web import IndexHandler, LastLogsHandler, ComponentHandler
from nfq.logwrapper.web import RestLastHandler, RestActiveHandler, RestPageHandler
from nfq.logwrapper.ws import WSHandler

ioloop.install()


def process_log(messages):
    global clients

    for message in messages:
        parsed = json.loads(message.decode())
        entry = LogEntry(
            source=parsed['source'],
            when=datetime.strptime(parsed['when'], "%Y-%m-%dT%H:%M:%S.%f"),
            message=parsed['message']
        )
        session.add(entry)

        # Manage subscriptions
        for client in clients:
            if client.subscription and client.subscription.findall(parsed['message']):
                client.client.write_message(parsed['message'])
    
        
def collector(address):
    """
    Process that collects all logs and saves them to a database
    """
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(address)

    stream_pull = zmqstream.ZMQStream(socket)
    stream_pull.on_recv(process_log)


def make_app():
    return web.Application([
        (r'/', IndexHandler),
        (r'/ws', WSHandler),
        (r'/last/([0-9]+)', LastLogsHandler),
        (r'/co/(.+)/([0-9]+)', ComponentHandler),
        (r'/api/active_last/([0-9]+)', RestActiveHandler),
        (r'/api/last/([0-9]+)', RestLastHandler),
        (r'/api/page/([0-9]+)/count/([0-9]+)', RestPageHandler),
        (r'/(favicon.ico)', web.StaticFileHandler,
         {'path': os.path.join(root_path, 'img', 'favicon.ico')}),
        (r'/css/(.*)', web.StaticFileHandler,
         {'path': os.path.join(root_path, 'css')}),
        (r'/js/(.*)', web.StaticFileHandler,
         {'path': os.path.join(root_path, 'js')})
    ])


def run():
    # Configure DB stuff
    logging.info('Updating DB tables...')
    Base.metadata.create_all(engine)
    logging.info('Done')

    app = make_app()
    app.listen(options.port)
    ioloop.IOLoop.instance().run_sync(
        partial(collector, address=options.collector)
    )
    logging.info('Starting event loop...')
    ioloop.IOLoop.current().start()

if __name__ == '__main__':
    run()

