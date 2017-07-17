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

import json
from tornado import web
from datetime import datetime, timedelta
from nfq.logwrapper.db import session, LogEntry
from nfq.logwrapper.config import loader


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


class RestPageHandler(web.RequestHandler):
    def get(self, fr, count):
        fr = int(fr)
        count = int(count)

        last = session.query(LogEntry).order_by(LogEntry.id.desc()).first()
        last_id = last.id

        self.write(json.dumps(last.to_dict()))

