"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        main.py -- main

    FIRST RELEASE
        2017-07-03  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import argparse
import configparser
import sys
import logging
from pkg_resources import resource_filename, iter_entry_points

import requests

from messgeraet_anzapfen import __version__
from messgeraet_anzapfen.sensor import Sensor, MeasurementError
from messgeraet_anzapfen.server import Server, ServerError
from messgeraet_anzapfen.statusled import StatusLed

__author__ = "Sebastian Stigler"
__copyright__ = "Sebastian Stigler"
__license__ = "mit"

_logger = logging.getLogger(__name__)


class Main:
    """Main class"""

    def parse_args(self, args):
        """Parse command line parameters"""

        parser = argparse.ArgumentParser(
            description=("Collecting data from messuring device and send "
                         "result to a server."))
        parser.add_argument(
            '--version',
            action='version',
            version='messgeraet_anzapfen {ver}'.format(ver=__version__))
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-c',
            '--config_file',
            dest='config_file',
            type=argparse.FileType('r'),
            help='The config file to be used.')
        group.add_argument(
            '--print-config-file',
            dest='print_config_file',
            action='store_true',
            help='Print a template for a config file.')
        group.add_argument(
            '--print-known-sensors',
            dest='print_known_sensors',
            action='store_true',
            help='Print all known sensors with a small description.')
        parser.add_argument(
            '--no-sending',
            dest='sending',
            action='store_false',
            help="Don't send data to the server but print it to stdout.")
        parser.add_argument(
            '-v',
            '--verbose',
            dest="loglevel",
            help="set loglevel to INFO",
            action='store_const',
            const=logging.INFO)
        parser.add_argument(
            '-vv',
            '--very-verbose',
            dest="loglevel",
            help="set loglevel to DEBUG",
            action='store_const',
            const=logging.DEBUG)
        self.args = parser.parse_args(args)

    def setup_logging(self):
        """Setup basic logging

        Args:
          loglevel (int): minimum loglevel for emitting messages
        """
        logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
        logging.basicConfig(level=self.args.loglevel, stream=sys.stdout,
                            format=logformat, datefmt="%Y-%m-%d %H:%M:%S")

    def load_sensor_plugins(self):
        """load all registered sensors"""
        self.sensor_plugins = {}
        for ep in iter_entry_points(group='messgeraet_sensoren'):
            self.sensor_plugins.update({ep.name: ep.load()()})

    def print_config_file(self):
        """Print the template for the config file and exit"""
        if self.args.print_config_file:
            inifile = resource_filename('messgeraet_anzapfen', 'anzapfen.ini')
            with open(inifile) as fil:
                print(fil.read())
            print('#'*79 + '\n## Sensors\n' + '#'*79 + '\n')
            for sensor in self.sensor_plugins.values():
                sensor.print_ini_file()
            sys.exit(0)

    def print_known_sensors(self):
        """Print all the currently implemented sensors and exit"""
        if self.args.print_known_sensors:
            for cls in self.sensor_plugins.values():
                print('%s:' % cls.__name__)
                print('    %s\n' % cls.__doc__.strip())
            sys.exit(0)

    def read_config(self):
        """Read and parse the config file """
        _logger.info("Read all configfiles")
        config = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation())
        config.read_file(self.args.config_file)
        section = config['DEFAULT']
        for key in ['sensor', 'id']:
            if key not in section:
                raise KeyError(('The key "%s" is not in the section "%s" of '
                                'the config file') % (key, section.name))
        self.config = config

    def read_sensor(self):
        """Read data from the configured sensor"""

        sensor_name = self.config.get('DEFAULT', 'sensor')
        for cls in self.sensor_plugins.values():
            if sensor_name == cls.__name__:
                break
        else:
            raise NotImplementedError(
                    ('Sensor %s is not implemented!\nUse the option '
                     '--print-known-sensors to list all available sensors.') %
                    sensor_name)

        self.sensor = cls()
        self.sensor.load_config(self.config)
        self.sensor.measure()

    def send_data(self):
        """send data to logging server"""
        server = Server()
        server.load_config(self.config)
        server.send(self.sensor.data, self.args.sending)

    def __init__(self, args):
        """Main entry point allowing external calls
        """
        self.parse_args(args)
        self.setup_logging()

        self.load_sensor_plugins()
        self.print_config_file()
        self.print_known_sensors()

        self.read_config()
        self.statusled = StatusLed(self.config)

        try:
            self.statusled.sensor.blink(2)
            self.read_sensor()

            self.statusled.server.blink(2)
            self.send_data()

        except MeasurementError as err:
            """measurementerror"""
            _logger.error('MeasurementError: %r' % err)
            self.statusled.sensor.on()
        except ServerError as err:
            """servererror"""
            _logger.error('ServerError: %r' % err)
            self.statusled.server.on()


def run():
    """Entry point for console_scripts
    """
    Main(sys.argv[1:])


if __name__ == "__main__":
    run()

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
