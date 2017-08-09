# -*- coding: utf-8 -*-
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine
from watson.framework.debug import abc

data = []


@event.listens_for(Engine, "before_cursor_execute")  # pragma: no cover
def before_cursor_execute(conn, cursor, statement, parameters,
                          context, executemany):
    context._query_start_time = time.time()  # pragma: no cover


@event.listens_for(Engine, "after_cursor_execute")  # pragma: no cover
def after_cursor_execute(conn, cursor, statement,
                         parameters, context, executemany):
    total = time.time() - context._query_start_time  # pragma: no cover
    data.append({
        'time': total*1000,
        'statement': statement,
        'parameters': parameters
    })  # pragma: no cover


class Query(abc.Panel):
    title = 'Database'
    icon = 'database'

    def __init__(self, config, renderer, application):
        super(Query, self).__init__(config, renderer, application)
        self.application_run = application.run
        application.run = self.run

    def render(self):
        return self._render({'queries': data})

    def render_key_stat(self):
        return '{0} queries ({1:.2f}ms)'.format(
            len(data),
            sum([query['time'] for query in data]))

    def run(self, environ, start_response):
        # Need to clear this on each run
        self.total = 0
        global data
        data = []
        return self.application_run(environ, start_response)
