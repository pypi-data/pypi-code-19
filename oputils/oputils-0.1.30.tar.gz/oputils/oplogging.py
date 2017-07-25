import datetime
import json

from flask import request
import logging
import threading
import sys
import os
import hashlib
import traceback
from gevent import pywsgi

import airbrake



from prometheus_client import Counter
exception_counter = Counter('exception_counter', 'Exception counter', ['kind', 'level'])

class OPLogFormatter(logging.Formatter):

    def __init__(self, default=logging._defaultFormatter):
        self._default_formatter = default

    def format(self, record):
        msg = {
            "@timestamp": self.get_date(),
            "message": record.msg,
            "level": record.levelname,
            #"tracetoken": self.get_trace_token(),
            # XXX need to fix this - right now - it will work if you pass in a trace token or if you do not have any io blocks before you get to this log statment
            "tracetoken": getattr(record, "tracetoken", self.get_trace_token()),
            "thread" : self.get_thread_name()
        }

        thread_class = self.get_thread_class()

        if thread_class != "Thread":
            msg["thread_class"] = thread_class

        if hasattr(record, "path") and record.path:
            msg["path"] =  record.path

        if hasattr(record, "timing") and record.timing:
            msg["timing"] = "%.6f" % record.timing

        if hasattr(record, "query") and record.query:
            msg["query"] = record.query

        (trace_string, kind) = self.get_trace_info()
        if trace_string:
            msg["stack_trace"] = trace_string
            try:
                label_dict = {"kind": kind, "level" : record.levelname}
                exception_counter.labels(**label_dict).inc()
            except:
                msg["promethus_error"] = "error calling prometheus exception counter"

        return json.dumps(msg, ensure_ascii=True)

    def get_trace_token(self):
        try:
            return request.headers.get('X-Trace-Token', 'unknown')
        except RuntimeError:
            sys.exc_clear()
            return "unknown"

    def get_trace_info(self):
        exc_info = sys.exc_info()
        (a,b,c) = exc_info
        if a:
            trace_string = self._default_formatter.formatException(exc_info)
            kind = a.__name__
            return trace_string, kind
        else:
            return None, None

    def get_date(self):
        return str(datetime.datetime.now())[:-3].replace(" ","T")  + "Z"

    def get_thread_name(self):
        return threading.current_thread().name

    def get_thread_class(self):
        return type(threading.current_thread()).__name__

class MyHandler(pywsgi.WSGIHandler):
    def __init__(self, socket, address, server, rfile=None):
        super(MyHandler, self).__init__(socket, address, server, rfile)

    def format_request(self):
        length = self.response_length or '-'

        client_address = self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address
        return '%s - - "%s" %s %s' % (
            client_address or '-',
            self.requestline or '',
            # Use the native string version of the status, saved so we don't have to
            # decode. But fallback to the encoded 'status' in case of subclasses
            # (Is that really necessary? At least there's no overhead.)
            (self._orig_status or self.status or '000').split()[0],
            length)

    def log_request(self):
        tracetoken = self.headers.getheader('X-Trace-Token', 'unknown')
        self.server.log._logger.log(20, self.format_request(), extra={'tracetoken': tracetoken, 'timing':  self.time_finish - self.time_start})

    def log_error(self, msg, *args):
        tracetoken = self.headers.getheader('X-Trace-Token', 'unknown')

        try:
            message = msg % args
        except Exception:
            traceback.print_exc()
            message = '%r %r' % (msg, args)
        try:
            message = '%s: %s' % (self.socket, message)
        except Exception:
            pass

        try:
            self.server.error_log._logger.log(40, message, extra={'tracetoken': tracetoken})
        except Exception:
            traceback.print_exc()


def init_logger():
    logger = logging.getLogger()
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter
    formatter = OPLogFormatter()
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    if (os.environ.get('AIRBRAKE_API_KEY', None) and os.environ.get('AIRBRAKE_PROJECT_ID')):
        #logger.addHandler(airbrake.AirbrakeHandler())
        pass
    else:
        logger.info("Airbrake not use: AIRBRAKE_API_KEY or AIRBRAKE_PROJECT_ID not set ")
