# -*- coding: utf-8 -*-
# Copyright © 2017 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# CLI parsing
'''CLI parsing'''

# standard library imports
from argparse import ArgumentParser
import glob
import logging
import os.path
import sys

__version__ = '0.5'

def cliparse():
    '''Parse the command line to get options'''
    epilog = 'For more information: https://remindr.readhthedocs.org'
    description = 'Send toots to remind people about blog entries'
    parser = ArgumentParser(prog='remindr',
                            description=description,
                            epilog=epilog)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-c', '--config',
                        default=[os.path.join(os.getenv('XDG_CONFIG_HOME', '~/.config'),
                                              'remindr.ini')],
                        nargs='+',
                        dest="config",
                        help='Location of config file (default: %(default)s)',
                        metavar='FILE')
    parser.add_argument('-n', '--dry-run', dest='dryrun',
                        action='store_true', default=False,
                        help='Do not actually post toots')
    parser.add_argument('-v', '--verbose', '--info', dest='log_level',
                        action='store_const', const='info', default='warning',
                        help='enable informative (verbose) output, work on log level INFO')
    parser.add_argument('-d', '--debug', dest='log_level',
                        action='store_const', const='debug', default='warning',
                        help='enable debug output, work on log level DEBUG')
    levels = [i for i in logging._nameToLevel.keys()
    if (type(i) == str and i != 'NOTSET')]
    parser.add_argument('--syslog', nargs='?', default=None,
                        type=str.upper, action='store',
                        const='INFO', choices=levels,
                        help='''log to syslog facility, default: no
                        logging, INFO if --syslog is specified without
                        argument''')
    opts = parser.parse_args()
    # verify if the path to cache file is an absolute path
    # get the different config files, from a directory or from a *.ini style
    opts.config = list(map(os.path.expanduser, opts.config))
    for element in opts.config:
        if element and not os.path.exists(element):
            sys.exit('You should provide an existing path for the config file: %s' % element)
        if os.path.isdir(element):
            opts.configs = glob.glob(os.path.join(element, '*.ini'))
        else:
            # trying to glob the path
            opts.configs = glob.glob(element)
    # verify if a configuration file is provided
    if not opts.configs:
        sys.exit('no configuration file was found at the specified path(s) with the option -c')
    return opts
