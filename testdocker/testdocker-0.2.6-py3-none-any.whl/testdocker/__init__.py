"""
testdocker
~~~~~~~~~~

Unit Testing for docker containers.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.

See `README.rst` for usage.

"""

from . import util, commands, objects, mixins, cli

from .util import match, get_content_type
from .commands import CommandBase, CurlCommand, NetCatCommand, CatCommand
from .objects import Compose, Container
from .mixins import ContainerTestMixinBase, ContainerTestMixin, main


__title__ = 'testdocker'
__version__ = '0.2.6'
__build__ = 0x000206
__author__ = "Joe Black <joeblack949@gmail.com>"
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 Joe Black'
