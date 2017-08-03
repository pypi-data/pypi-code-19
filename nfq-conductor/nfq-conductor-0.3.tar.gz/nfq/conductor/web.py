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
import json
import logging
import datetime
from datetime import datetime, timedelta

from tornado import web, template, httpclient

from nfq.conductor.config import loader
from nfq.conductor.db import Daemon, Process, Configuration, session, LogEntry
from operator import attrgetter

root_path = os.path.abspath(os.path.join(os.path.realpath(__file__), os.path.pardir))
loader = template.Loader(os.path.join(root_path, 'templates'))


def get_from_daemon(ip, port, call):
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch("http://{}:{}/{}".format(
            ip, port, call
        ), request_timeout=2.0)
        rval = response.body.decode()
    except httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        rval = 'NA'
    except Exception as e:
        # Other errors are possible, such as IOError.
        rval = 'NA'

    http_client.close()
    return rval


def post_job(ip, port, body):
    http_client = httpclient.HTTPClient()
    logging.info('Sending job')
    response = http_client.fetch(
        "http://{}:{}/send_process".format(ip, port),
        method='POST',
        body=body)

    return response.body


def kill_job(ip, port, pid):
    http_client = httpclient.HTTPClient()
    logging.info('Killing job')
    response = http_client.fetch(
        "http://{}:{}/kill/{}".format(ip, port, pid))

    return response.body


def active_daemons(session):
    daemons = session.query(Daemon).filter(Daemon.active).order_by(
        Daemon.when.desc())
    checked_daemons = list()

    for daemon in daemons:
        key = get_from_daemon(daemon.ip, daemon.port, '')

        if key == daemon.uuid and daemon.uuid not in [d.uuid for d in
                                                      checked_daemons]:
            checked_daemons.append(daemon)
        else:
            logging.info('Daemon {} is inactive'.format(daemon.uuid))
            daemon.active = False

    session.commit()
    return checked_daemons


class DaemonsHandler(web.RequestHandler):
    def get(self):
        checked_daemons = active_daemons(session)
        daemon_info = list()
        for daemon in checked_daemons:
            usage_str = get_from_daemon(daemon.ip, daemon.port, 'usage')
            cpu_usage = json.loads(usage_str)
            daemon_info.append((daemon, cpu_usage))

        processes = session.query(Process).filter(Process.running).order_by(
            Process.when.desc())

        self.write(
            loader.load("daemons.html").generate(daemons=daemon_info,
                                                 processes=processes)
        )


class DaemonHandler(web.RequestHandler):
    def get(self, uuid):
        daemon = session.query(Daemon).filter(
            Daemon.uuid == uuid).order_by(Daemon.when.desc()).first()
        processes = [s for s in session.query(
            Process).filter(
            Process.host == uuid).order_by(
            Process.when
        )]
        processes = [p for p in reversed(sorted(processes,
                                                key=attrgetter('running')))]

        for proc in processes:
            if proc.running:
                # Check if the wrapped process is running
                running = get_from_daemon(
                    daemon.ip,
                    daemon.port,
                    'is_running/{}'.format(proc.process))
                if running == 'False':
                    logging.info('Proccess {} stopped'.format(proc.label))
                    proc.running = False

        session.commit()

        self.write(
            loader.load("daemon.html").generate(daemon=daemon,
                                                processes=processes,
                                                cpu_count=get_from_daemon(
                                                    daemon.ip,
                                                    daemon.port,
                                                    'cpu_count'))
        )

    def post(self, *args, **kwargs):
        if self.get_argument('command', default=None):
            logging.info('Posting job {}'.format(self.get_argument('command')))
            response = post_job(self.get_argument('ip'),
                                self.get_argument('port'),
                                json.dumps([
                                    self.get_argument('name'),
                                    self.get_argument('command')]
                                ))

        elif self.get_argument('pid', default=None):
            logging.info('Killing pid {}'.format(self.get_argument('pid')))
            response = kill_job(self.get_argument('ip'),
                                self.get_argument('port'),
                                self.get_argument('pid'))

        self.write(
            loader.load("posted.html").generate(message=response)
        )


class DeleteHandler(web.RequestHandler):
    def post(self, job_id):
        job = session.query(Process).filter(Process.id == job_id).one_or_none()

        if job:
            session.delete(job)
            session.commit()

            self.write(loader.load("posted.html").generate(
                message='Job successfully deleted')
            )
            return
        else:
            self.write(loader.load("posted.html").generate(
                message='No such job')
            )
            return


class ResetHandler(web.RequestHandler):
    def get(self):
        processes = session.query(Process).filter(Process.running)
        
        for proc in processes:
            # Check if the wrapped process is running
            daemon = session.query(Daemon).filter(
                Daemon.uuid == proc.host).order_by(
                Daemon.when.desc()).first()

            running = get_from_daemon(
                daemon.ip,
                daemon.port,
                'is_running/{}'.format(proc.process))

            if running == 'True':
                logging.info('Proccess {} stopped'.format(proc.label))
                proc.running = False
                _ = kill_job(daemon.ip,
                             daemon.port,
                             '-'.join([str(proc.wrapped), str(proc.process)]))

        session.commit()
        self.write(
            loader.load("posted.html").generate(message='Cluster reset')
        )


class RelaunchHandler(web.RequestHandler):
    def post(self, config_id):
        config = session.query(
            Configuration).filter(Configuration.id == config_id).one_or_none()

        if config:
            # Validation and stuff
            # Get the active daemons
            daemons = active_daemons(session)
            cluster_config = json.loads(config.config.decode())

            for i, daemon in enumerate(daemons):
                pass

            if daemons:
                logging.info('{} active daemons'.format(i + 1))
                if len(cluster_config) > i + 1:
                    self.write(
                        loader.load("posted.html").generate(
                            message=str("Not enough running daemons"))
                    )
                    return
                else:
                    daemons_mapping = {d.uuid: d for d in daemons}

                    # Map jobs when the daemon is present
                    for k, v in cluster_config.copy().items():
                        if k in daemons_mapping:
                            commands = cluster_config.pop(k)
                            daemon = daemons_mapping.pop(k)

                            for uid, command in commands.items():
                                logging.info('Send {} to {}'.format(command,
                                                                    daemon.uuid))
                                _ = post_job(daemon.ip,
                                             daemon.port,
                                             json.dumps([uid, command])
                                             )

                    # Otherwise pick random daemon.
                    for j, d in zip([k for k in cluster_config.keys()],
                                    [k for k in daemons_mapping.keys()]):
                        commands = cluster_config.pop(j)
                        daemon = daemons_mapping.pop(d)

                        for uid, command in commands.items():
                            logging.info(
                                'Send {} to {}'.format(command, daemon.uuid))
                            _ = post_job(daemon.ip,
                                         daemon.port,
                                         json.dumps([uid, command])
                                         )

                    self.write(loader.load("posted.html").generate(
                        message='Job successfully rescheduled')
                    )
                    return
        else:
            self.write(loader.load("posted.html").generate(
                message='No such configuration')
            )
            return


class ConfigHandler(web.RequestHandler):
    def get(self):
        available_scripts = session.query(Configuration
                                          ).order_by(Configuration.when.desc())
        self.write(
            loader.load("config.html").generate(
                available_scripts=available_scripts)
        )

    def post(self):
        try:
            file = self.request.files['config_file'][0]
        except KeyError:
            logging.info('No configuration file provided, Trying the body...')
            if self.request.body:
                # Mocking the file if the config came from the submit script.
                logging.info('Found body')
                file = {'body': self.request.body}
                logging.info('Found config in the body')
            else:
                self.write(
                    loader.load("posted.html").generate(message='No config file')
                )
                return

        logging.info('Got configuration file')

        config = Configuration(
            when=datetime.now(),
            config=file['body']
        )

        session.add(config)

        # Validation and stuff
        # Get the active daemons
        daemons = active_daemons(session)
        try:
            cluster_config = json.loads(file['body'].decode())
        except json.decoder.JSONDecodeError:
            self.write(loader.load("posted.html").generate(
                message=str("Error parsing the config file")))
            return

        for i, daemon in enumerate(daemons):
            pass

        if daemons:
            logging.info('{} active daemons'.format(i+1))
            if len(cluster_config) > i+1:
                self.write(
                    loader.load("posted.html").generate(
                        message=str("Not enough running daemons"))
                )
                return

        else:
            logging.warning('No active daemons')
            self.write(
                loader.load("posted.html").generate(message='No active daemons')
            )
            return

        daemons_mapping = {d.uuid: d for d in daemons}

        # Map jobs when the daemon is present
        for k, v in cluster_config.copy().items():
            if k in daemons_mapping:
                commands = cluster_config.pop(k)
                daemon = daemons_mapping.pop(k)

                for uid, command in commands.items():
                    logging.info('Send {} to {}'.format(command, daemon.uuid))
                    _ = post_job(daemon.ip,
                                 daemon.port,
                                 json.dumps([uid, command])
                                 )

        # Otherwise pick random daemon.
        for j, d in zip([k for k in cluster_config.keys()],
                        [k for k in daemons_mapping.keys()]):
            commands = cluster_config.pop(j)
            daemon = daemons_mapping.pop(d)

            for uid, command in commands.items():
                logging.info('Send {} to {}'.format(command, daemon.uuid))
                _ = post_job(daemon.ip,
                             daemon.port,
                             json.dumps([uid, command])
                             )

        self.write(
            loader.load("posted.html").generate(message='Successful')
        )

        return


class IndexHandler(web.RequestHandler):
    def get(self):

        # Get components that have been active within the last 20 minutes:
        logs20 = session.query(LogEntry).filter(
            LogEntry.when > datetime.now() - timedelta(minutes=20))

        components = list()
        for log in logs20:
            if log.source not in components:
                components.append(log.source)

        self.write(
            loader.load("index.html").generate(components=components)
        )


class LastLogsHandler(web.RequestHandler):
    def get(self, num_entries):
        num_entries = int(num_entries)
        fetched = session.query(
            LogEntry).order_by(
            LogEntry.when.desc()).limit(num_entries)
        self.write(
            loader.load("list.html").generate(
                logs=reversed([f for f in fetched]))
        )


class ComponentHandler(web.RequestHandler):
    def get(self, component, num_entries):
        num_entries = int(num_entries)
        fetched = session.query(
            LogEntry).filter(
            LogEntry.source == component).order_by(
            LogEntry.when.desc()).limit(num_entries)
        self.write(
            loader.load("list.html").generate(
                logs=reversed([f for f in fetched]))
        )


class RestActiveHandler(web.RequestHandler):
    def get(self, active_previous_minutes):
        active_previous_minutes = int(active_previous_minutes)

        # Get components that have been active within the last x minutes:
        logsx = session.query(LogEntry).filter(
            LogEntry.when > datetime.now() - timedelta(
                minutes=active_previous_minutes))

        components = list()
        for log in logsx:
            if log.source not in components:
                components.append(log.source)

        self.write(json.dumps(components))


class RestLastHandler(web.RequestHandler):
    def get(self, num_entries):
        num_entries = int(num_entries)
        fetched = session.query(
            LogEntry).order_by(
            LogEntry.id.desc()).limit(num_entries)

        self.write(json.dumps([f.to_dict() for f in fetched]))


class RestCoLastHandler(web.RequestHandler):
    def get(self, co, num_entries):
        num_entries = int(num_entries)
        fetched = session.query(
            LogEntry).filter(
            LogEntry.source == co).order_by(
            LogEntry.id.desc()).limit(num_entries)

        self.write(json.dumps([f.to_dict() for f in fetched]))


class RestPageHandler(web.RequestHandler):
    def get(self, fr, count):
        fr = int(fr)
        count = int(count)

        last = session.query(LogEntry).order_by(LogEntry.id.desc()).first()
        last_id = last.id

        self.write(json.dumps(last.to_dict()))
