# NFQ Conductor. A tool for centralizing and visualizing logs.
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

import datetime
import json
import logging
import multiprocessing
import subprocess
from uuid import uuid4

import psutil
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import zmq
from tornado.options import define, options

from nfq.conductor.runner import launch

UUID = str(uuid4())

define("port", default=8999, help="run on the given port", type=int)
define("interface", default='lo', help="network interface for collector connection", type=str)
define("collector", default='tcp://127.0.0.1:5555', help="Collector socket address", type=str)
define("uuid", default=UUID, help="Unique ID for the daemon", type=str)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(options.uuid)


class CpuCountHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(str(psutil.cpu_count()))


class UsageHandler(tornado.web.RequestHandler):
    def get(self):
        usage_str = psutil.cpu_times_percent()
        usage = dict(
            user=usage_str.user,
            system=usage_str.system,
            nice=usage_str.nice,
            iowait=usage_str.iowait,
            irq=usage_str.irq,
            softirq=usage_str.softirq,
            steal=usage_str.steal,
            guest=usage_str.guest,
            guest_nice=usage_str.guest_nice
            )
        self.write(json.dumps(usage))


class ProcessHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        command = 'nfq-runner --command "{}" --collector {} --host {}'.format(
            self.request.body.decode(),
            options.collector,
            options.uuid
        )
        logging.info(command)
        name, command = json.loads(self.request.body.decode())
        p = multiprocessing.Process(target=launch,
                                    args=(options.collector,
                                          command,
                                          options.uuid,
                                          name)
                                    )
        p.start()
        logging.info('Launched')

        self.write(command)


class KillHandler(tornado.web.RequestHandler):
    def get(self, pid):
        wrapped, process = pid.split('-')
        subprocess.Popen('kill -9 {}'.format(int(process)), shell=True)
        subprocess.Popen('kill -2 {}'.format(int(wrapped)), shell=True)


class RunningHandler(tornado.web.RequestHandler):
    def get(self, pid):
        self.write(str(psutil.pid_exists(int(pid))))


def run():
    tornado.options.parse_command_line()

    # Fetch network information
    ip = psutil.net_if_addrs()[options.interface][0].address

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    logging.info('Connecting to {}'.format(options.collector))

    socket.connect(options.collector)
    
    logging.info('Addr: {}:{}'.format(str(ip), str(options.port)))

    logging.info('Preparing configuration message...')
    socket.send_json({
        'source': options.uuid,
        'when': datetime.datetime.now().isoformat(),
        'message': '^^^^{{"ip": "{}", "port": {}, "uuid": "{}" }}'.format(
            ip, options.port, options.uuid
        )
    })

    socket.close()
    context.destroy()
    logging.info('Sent configuration message')
    logging.info('{{"ip": "{}", "port": {}, "uuid": "{}" }}'.format(
            ip, options.port, options.uuid
        ))

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/cpu_count", CpuCountHandler),
        (r"/usage", UsageHandler),
        (r"/send_process", ProcessHandler),
        (r"/kill/(.+)", KillHandler),
        (r"/is_running/([0-9]+)", RunningHandler)
    ], autoreload=False)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run()
