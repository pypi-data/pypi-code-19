# -*- coding: utf-8 -*-

import contextlib
import datetime
import getpass
import logging
import os
import socket
import sys
from threading import Lock

import pika
import simplejson as json
from dateutil.parser import parse
from pycapo import CapoConfig

# CAPO properties we care about
CAPO_PROP_HOSTNAME = 'edu.nrao.archive.configuration.AmqpServer.hostname'
CAPO_PROP_USERNAME = 'edu.nrao.archive.configuration.AmqpServer.username'
CAPO_PROP_PASSWORD = 'edu.nrao.archive.configuration.AmqpServer.password'
CAPO_PROP_PORT = 'edu.nrao.archive.configuration.AmqpServer.port'

# Assorted other defaults.
CONNECTION_ATTEMPTS = 5
RETRY_DELAY = 500
SOCKET_TIMEOUT = 5000
LOG_ROUTING_KEY_FORMAT = '{application}.{level}'
EVENT_ROUTING_KEY_FORMAT = '{application}.event'
EVENT_EXCHANGE = 'archive.events'
EVENT_EXCHANGE_TYPE = 'topic'
LOG_EXCHANGE = 'archive.logs'
LOG_EXCHANGE_TYPE = 'fanout'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.NOTSET
LOGDUMPER_FORMAT = '{hostname} - {date} [{threadName}] {level:<5} {loggerName:<36}#{method}:{line} - {formattedMessage}\n'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f+00:00'


def _now():
    r""" Get the current date and time in UTC as a string. """
    return datetime.datetime.utcnow().strftime(TIMESTAMP_FORMAT)


@contextlib.contextmanager
def _smart_open(filename=None):
    """If we get a filename and it isn't '-', return a file handle to it for appending, else return a file handle to stdout. Saw on stack overflow, I'm not this clever.
    http://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
    """
    if filename and filename != '-':
        fh = open(filename, 'a')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


class _Pymygdala():
    r""" Class for sending events to a RabbitMQ server. This gets used as a base class for the other exposed classes in the package.

    :Keyword Arguments:
        *profile* ("string"): the name of the profile to use, e.g. 'test', 'production'. If missing this defaults to the CAPO_PROFILE environment variable, if that is missing as well it explodes, throwing a ValueError exception. A profile should be a simple word, one without spaces or tabs or evil things in it. This is not checked and no guarantee is provided.

        *application* ("string"): the name of the application sending the event or message, "unknown" by default.

        *hostname* ("string"): name of the AMQP server to use, defaults to CAPO property pymygdala.CAPO_PROP_HOSTNAME.

        *username* ("string"): username to connect to AMQP with, defaults to CAPO property pymygdala.CAPO_PROP_USERNAME.

        *password* ("string"): password to connect to AMQP with, defaults to CAPO property pymygdala.CAPO_PROP_PASSWORD.

        *port* ("int"): port number to connect to AMQP with, defaults to CAPO property pymygdala.CAPO_PROP_PORT.

        *exchange* ("string"): the exchange to use, defaults to pymygdala.EVENT_EXCHANGE.

        *exchange_type* ("string"): type of exchange to use, defaults to pymygdala.EVENT_EXCHANGE_TYPE.

        *routing_key* ("string"): how messages will be routed to queues, format defaults to pymygdala.EVENT_ROUTING_KEY_FORMAT.

        *connection_attempts* (int): maximum number of retry attempts.

        *retry_delay* (int|float): time to wait in seconds, before the next.

        *socket_timeout* (int|float): use for high latency networks.

    :Example:
    """

    def __init__(self, **kwargs):
        if 'profile' in kwargs:
            self.profile = kwargs['profile']
        elif 'CAPO_PROFILE' in os.environ:
            self.profile = os.environ['CAPO_PROFILE']
        else:
            raise ValueError('Can not deduce CAPO profile to use')
        self.config = CapoConfig(profile=self.profile)
        self.application = kwargs.get('application', 'unknown')
        self.exchange = kwargs.get('exchange', EVENT_EXCHANGE)
        self.exchange_type = kwargs.get('exchange_type', EVENT_EXCHANGE_TYPE)
        self.routing_key = kwargs.get('routing_key', EVENT_ROUTING_KEY_FORMAT.format(application=self.application))

        # Connection parameters for talking to RabbitMQ
        self.connection_parameters = pika.ConnectionParameters(
            host=kwargs.get('hostname', self.config.getstring(CAPO_PROP_HOSTNAME)),
            port=kwargs.get('port', self.config.getint(CAPO_PROP_PORT)),
            connection_attempts=kwargs.get('connection_attempts', CONNECTION_ATTEMPTS),
            socket_timeout=kwargs.get('socket_timeout', SOCKET_TIMEOUT),
            retry_delay=kwargs.get('retry_delay', RETRY_DELAY),
            credentials= \
                pika.PlainCredentials(username=kwargs.get('username', self.config.getstring(CAPO_PROP_USERNAME)),
                                      password=kwargs.get('password', self.config.getstring(CAPO_PROP_PASSWORD))))

        # Parameters we derive or produce and don't let the caller set
        self.sender_username = getpass.getuser()
        self.sender_hostname = socket.gethostname()
        self.connection = None
        self.channel = None
        self._lock = Lock()
        self._open_connection()

    def _close_connection(self):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        self.connection, self.channel = None, None

    def _open_connection(self):
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type=self.exchange_type,
                                      durable=True, auto_delete=False)

    def _del(self):
        self._lock.acquire()
        try:
            self._close_connection()
        finally:
            self._lock.release()

    def _send(self, event, routing_key=None, headers=None):
        """I need a docstring here."""
        if routing_key is None:
            routing_key = self.routing_key
        self._lock.acquire()
        try:
            if headers is not None:
                self.channel.basic_publish(exchange=self.exchange,
                                           routing_key=routing_key,
                                           properties=pika.BasicProperties(headers),
                                           body=event)
            else:
                self.channel.basic_publish(exchange=self.exchange,
                                           routing_key=routing_key,
                                           body=event)
        except Exception:
            self.channel, self.connection = None, None
        finally:
            self._lock.release()


class LogHandler(logging.Handler, _Pymygdala):
    r""" Logging handler for a RabbitMQ server.

    :Keyword Arguments:
        *profile* ("string"): the name of the profile to use, e.g. 'test', 'production'. If missing this defaults to the CAPO_PROFILE environment variable, if that is missing as well it explodes, throwing a ValueError exception. A profile should be a simple word, one without spaces or tabs or evil things in it. This is not checked and no guarantee is provided.

        *hostname* ("string"): name of the AMQP server to use, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.hostname".

        *username* ("string"): username to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.username".

        *password* ("string"): password to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.password".

        *port* ("int"): port number to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.port".

        *connection_attempts* (int): maximum number of retry attempts.

        *retry_delay* (int|float): time to wait in seconds, before the next.

        *socket_timeout* (int|float): use for high latency networks.

        *exchange* ("string"): the exchange to use, defaults to pymygdala.LOG_EXCHANGE.

        *exchange_type* ("string"): type of exchange to use, defaults to pymygdala.LOG_EXCHANGE_TYPE.

        *application* ("string"): the name of the application sending the event or message, "unknown" by default.

        *level* ("level"): the logging level to use.

    :Example:

    >>> import logging
    >>> from pymygdala import LogHandler
    >>> log = logging.getLogger(__name__)
    >>> handler = LogHandler(profile='test', application='test-app', level=logging.DEBUG)
    >>> log.addHandler(handler)
    >>> log.error("my hovercraft is full of eels")

    """

    def __init__(self, **kwargs):
        self.level = kwargs.get('level', LOG_LEVEL)
        self.exchange = kwargs.get('exchange', LOG_EXCHANGE)
        self.exchange_type = kwargs.get('exchange_type', LOG_EXCHANGE_TYPE)
        self.application = kwargs.get('application', 'unknown')
        self.routing_key = LOG_ROUTING_KEY_FORMAT.format(application=self.application, level='WARNING')
        _Pymygdala.__init__(self, **dict(kwargs,
                                         exchange=self.exchange,
                                         exchange_type=self.exchange_type,
                                         routing_key=self.routing_key))
        logging.Handler.__init__(self)

    def record_to_dict(self, record):
        r""" Turn a Python logging.LogRecord into a simple dictionary, with the structure we expect,
        that can easily be turned into a JSON string and sent off to RabbitMQ. """
        d = dict()
        d['timestamp'] = _now()
        d['formattedMessage'] = record.msg
        d['loggerName'] = record.pathname
        d['level'] = record.levelname
        d['threadName'] = record.threadName
        d['referenceMask'] = 1
        d['filename'] = ''
        d['class'] = ''
        d['method'] = record.name
        d['line'] = record.lineno
        d['properties'] = dict()
        d['properties']['user'] = self.sender_username
        d['properties']['HOSTNAME'] = self.sender_hostname
        d['properties']['profile'] = self.profile
        return d

    def emit(self, record):
        r""" Emit a logging message, build the routing key per emission because it has the logging
        level as part of it. """
        self._send(json.dumps(self.record_to_dict(record)),
                   routing_key=LOG_ROUTING_KEY_FORMAT.format(application=self.application,
                                                             level=record.levelname))


class LogDumper(_Pymygdala):
    r""" Dump the logs from a RabbitMQ server.

    :Keyword Arguments:
        *profile* ("string"): the name of the profile to use, e.g. 'test', 'production'. If missing this defaults to the CAPO_PROFILE environment variable, if that is missing as well it explodes, throwing a ValueError exception. A profile should be a simple word, one without spaces or tabs or evil things in it. This is not checked and no guarantee is provided.

        *hostname* ("string"): name of the AMQP server to use, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.hostname".

        *username* ("string"): username to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.username".

        *password* ("string"): password to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.password".

        *port* ("int"): port number to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.port".

        *connection_attempts* (int): maximum number of retry attempts.

        *retry_delay* (int|float): time to wait in seconds, before the next.

        *socket_timeout* (int|float): use for high latency networks.

        *exchange* ("string"): the exchange to use, defaults to pymygdala.LOG_EXCHANGE.

        *exchange_type* ("string"): type of exchange to use, defaults to pymygdala.LOG_EXCHANGE_TYPE.

        *outfile* ("string"): the name of the file to write to, default '-' for sys.stdout.

    :Example:

    >>> # Dump the 'test' logs to stdout
    >>> from pymygdala import LogDumper
    >>> dumper = LogDumper(profile='test')
    >>> dumper.dump()

    """

    def __init__(self, **kwargs):
        _Pymygdala.__init__(self, **kwargs)
        self.outfile = kwargs.get('outfile', '-')
        self.queue = self.channel.queue_declare(exclusive=True, auto_delete=True,
                                                durable=False).method.queue
        self.channel.queue_bind(self.queue, LOG_EXCHANGE)
        self.channel.basic_consume(self._callback, queue=self.queue, no_ack=True)

    def _callback(self, ch, method, properties, body):
        r"""I need more docstrings."""
        with _smart_open(self.outfile) as fh:
            try:
                parsed = json.loads(body)
                parsed['hostname'] = parsed['properties']['HOSTNAME'] \
                    if 'HOSTNAME' in parsed['properties'] else ''

                if 'formattedMessage' in parsed:
                    parsed['date'] = parse(parsed['timestamp'])
                    fh.write(LOGDUMPER_FORMAT.format(**parsed))
                else:
                    fh.write('no formatted message: {}\n'.format(body))

                if 'stackTrace' in parsed:
                    for stack in parsed['stackTrace']:
                        for line in stack:
                            fh.write('{}\n'.format(line))

            except Exception as e:
                fh.write('{}\n'.format(e))
                fh.write('unparseable: {}\n'.format(body))

    def dump(self):
        r"""I need more docstrings."""
        self.channel.start_consuming()


def _datetime_to_dict():
    # Turn 'now' in UTC into the date format events expect to speak.
    d, t = dict(), dict()
    now = datetime.datetime.utcnow()
    d['year'], d['month'], d['day'] = now.year, now.month, now.day
    t['hour'], t['minute'], t['second'], t['nano'] = now.hour, now.minute, now.second, now.microsecond * 1000
    return {'date': d, 'time': t}


class SendEvent(_Pymygdala):
    r"""

    :Keyword Arguments:
        *profile* ("string"): the name of the profile to use, e.g. 'test', 'production'. If missing this defaults to the CAPO_PROFILE environment variable, if that is missing as well it explodes, throwing a ValueError exception. A profile should be a simple word, one without spaces or tabs or evil things in it. This is not checked and no guarantee is provided.

        *application* ("string"): the name of the application sending the event or message, "unknown" by default.

        *hostname* ("string"): name of the AMQP server to use, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.hostname"

        *username* ("string"): username to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.username".

        *password* ("string"): password to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.password".

        *port* ("int"): port number to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.port".

        *connection_attempts* (int): maximum number of retry attempts

        *retry_delay* (int|float): time to wait in seconds, before the next

        *socket_timeout* (int|float): use for high latency networks

        *exchange* ("string"): the exchange to use, defaults to pymygdala.EVENT_EXCHANGE

        *exchange_type* ("string"): type of exchange to use, defaults to pymygdala.EVENT_EXCHANGE_TYPE.

        *routing_key* ("string"): how messages will be routed to queues, format defaults to pymygdala.EVENT_ROUTING_KEY_FORMAT

    :Example:

    >>> # Send the kind of event the solr indexer does when it starts to index
    >>> from pymygdala import SendEvent
    >>> se = SendEvent(profile='test', application='solr-indexer')
    >>> event = {
    ...     "logData": {
    ...         "dryRun": False,
    ...         "numberOfDocuments": 9999
    ...     },
    ...     "message": "Starting reindexing process",
    ...     "request": "some request"
    ... }
    >>> se.send(event)

    """

    def __init__(self, **kwargs):
        _Pymygdala.__init__(self, **kwargs)

    def _add_fields(self, event):
        result = dict()
        result['user'] = self.sender_username
        result['hostname'] = self.sender_hostname
        result['timestamp'] = _datetime_to_dict()
        result['application'] = self.application
        result['version'] = 1.0
        result.update(event)
        return result

    def send(self, event, routing_key=None, headers=None):
        r""" Send an event to RabbitMQ: an 'event' here is a simple dictionary that can be converted into a JSON string.

        :Required Arguments:
            *event* ("dict"): a dictionary representing the event to send.
        :Optional Arguments:
            *routing_key* ("string"): the routing key of the message, defaults to application.event
            *headers* ("dict"): a dictionary of headers to send with the event as 'properties'

        """
        if routing_key is None:
            routing_key = self.routing_key
        event = self._add_fields(event)
        # print(json.dumps(d, sort_keys=True, indent=4 * ' '))
        self._send(json.dumps(event), routing_key=routing_key, headers=headers)


class SendNRAOEvent(SendEvent):
    r""" This subclasses SendEvent and just add some more fields to the event based on the exchange, so you can use it to trigger AAT/PPI workflows more easily.

    :Keyword Arguments:
        *profile* ("string"): the name of the profile to use, e.g. 'test', 'production'. If missing this defaults to the CAPO_PROFILE environment variable, if that is missing as well it explodes, throwing a ValueError exception. A profile should be a simple word, one without spaces or tabs or evil things in it. This is not checked and no guarantee is provided.

        *application* ("string"): the name of the application sending the event or message, "unknown" by default.

        *hostname* ("string"): name of the AMQP server to use, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.hostname"

        *username* ("string"): username to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.username".

        *password* ("string"): password to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.password".

        *port* ("int"): port number to connect to AMQP with, defaults to CAPO property "edu.nrao.archive.configuration.AmqpServer.port".

        *connection_attempts* (int): maximum number of retry attempts

        *retry_delay* (int|float): time to wait in seconds, before the next

        *socket_timeout* (int|float): use for high latency networks

        *exchange* ("string"): the exchange to use, defaults to pymygdala.EVENT_EXCHANGE

        *exchange_type* ("string"): type of exchange to use, defaults to pymygdala.EVENT_EXCHANGE_TYPE.

        *routing_key* ("string"): how messages will be routed to queues, format defaults to pymygdala.EVENT_ROUTING_KEY_FORMAT

    :Example:

    >>> # Send the kind of event the solr indexer does when it starts to index
    >>> from pymygdala import SendNRAOEvent
    >>> se = SendEvent(profile='test', application='solr-indexer')
    >>> headers = {
    ...     "reply-to": "jim@bob.foo"
    ... }
    >>> event = {
    ...     "logData": {
    ...         "dryRun": False,
    ...         "numberOfDocuments": 9999
    ...     },
    ...     "message": "Starting reindexing process",
    ...     "request": "some request"
    ... }
    >>> se.send(event, headers=headers)

    """
    def __init__(self, **kwargs):
        SendEvent.__init__(self, **kwargs)

    def _add_fields(self, event):
        result = SendEvent._add_fields(self, event)
        if self.exchange == 'archive.workflow-commands':
            result['type'] = 'edu.nrao.archive.workflow.messaging.commands.StartWorkflow'
            result['additionalPaths'] = []
        return result


def test_sendlog():
    # A quick and dirty test of logging in our environment.
    LOG = logging.getLogger(__name__)
    handler = LogHandler(profile='test', application='test-app',
                         level=logging.DEBUG)
    LOG.addHandler(handler)
    LOG.error("my hovercraft is full of eels")


def test_sendevent():
    # Send the kind of event the solr indexer does when it starts to index
    se = SendEvent(profile='test', application='solr-indexer')
    event = {
        "logData": {
            "dryRun": False,
            "numberOfDocuments": 9999
        },
        "message": "Starting reindexing process",
        "request": "some request"
    }
    se.send(event)


if __name__ == "__main__":
    # test_sendlog()
    test_sendevent()
