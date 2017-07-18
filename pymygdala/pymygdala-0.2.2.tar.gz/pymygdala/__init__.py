# -*- coding: utf-8 -*-

r""" Pymygdala: a CAPO aware Python library built atop pika for interacting with RabbitMQ, plus assorted simple command line applications built on the library.

Using this library you can log messages to RabbitMQ with a standard-isg logging handler and the Python logging package, you can monitor a RabbitMQ server and dump out the logs, and you can send various events to the server.
Many (most?) of the defaults for things like routing keys, exchange names and CAPO properties are heavily NRAO-centric but you can order-ride them if you want.
"""

from pymygdala._version import ___version___ as version
from pymygdala.models import (EVENT_EXCHANGE, LOG_EXCHANGE, LOG_FORMAT, LOG_LEVEL,
                              LOG_ROUTING_KEY_FORMAT, EVENT_ROUTING_KEY_FORMAT)
from pymygdala.models import (CAPO_PROP_HOSTNAME, CAPO_PROP_USERNAME, CAPO_PROP_PASSWORD,
                              CAPO_PROP_PORT)
from pymygdala.models import (LogHandler, LogDumper, SendEvent, SendNRAOEvent)
