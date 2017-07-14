# BSD 3-Clause License
#
# Copyright (c) 2017, Philippe Dellaert
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
nuage-vsd-sim
=============
A sample Nuage VSD API simulator
"""

import argparse
import ConfigParser
import os

from flask import Flask
from flask_restful import Api

from nuagevsdsim import simentities as sim
from nuagevsdsim.common import NUSimConfig, utils


class NuageVSDSim(object):
    def __init__(self):
        """
        Handle commands for interaction between Nuage Networks VSP and Amazon AWS
        """

        parser = argparse.ArgumentParser(
            description="A sample Nuage VSD API simulator."
        )
        parser.add_argument('-c', '--config-file', required=False,
                            help='Configuration file to use, if not specified ~/.nuage-vsd-sim/config.ini is used, it that does not exist, /etc/nuage-vsd-sim/config.ini is used.',
                            dest='config_file', type=str)
        args, command_args = parser.parse_known_args()

        # Handling configuration file
        if args.config_file:
            cfg = utils.parse_config(args.config_file)
        elif os.path.isfile('{0:s}/.nuage-vsd-sim/config.ini'.format(os.path.expanduser('~'))):
            cfg = utils.parse_config('{0:s}/.nuage-vsd-sim/config.ini'.format(os.path.expanduser('~')))
        elif os.path.isfile('/etc/nuage-vsd-sim/config.ini'):
            cfg = utils.parse_config('/etc/nuage-vsd-sim/config.ini')
        else:
            cfg = ConfigParser.ConfigParser()
            cfg.add_section('LOG')
            cfg.set('LOG', 'directory', '')
            cfg.set('LOG', 'file', '')
            cfg.set('LOG', 'level', 'DEBUG')

        # Handling logging
        log_dir = cfg.get('LOG', 'directory')
        log_file = cfg.get('LOG', 'file')
        log_level = cfg.get('LOG', 'level')

        if not log_level:
            log_level = 'WARNING'

        log_path = None
        if log_dir and log_file and os.path.isdir(log_dir) and os.access(log_dir, os.W_OK):
            log_path = os.path.join(log_dir, log_file)

        logger = utils.configure_logging(log_level, log_path)
        logger.debug('Logging initiated')

        utils.init_base_entities()

        self.app = Flask(__name__)

        self.app.config.from_object(NUSimConfig)

        self.api = Api(self.app)

        self.api.add_resource(
            sim.NUSimRoot,
            '/',
            '/nuage',
            '/nuage/api',
            '/nuage/api/v5_0'
        )

        self.api.add_resource(
            sim.NUSimMe,
            '/nuage/api/v5_0/me'
        )
        self.api.add_resource(
            sim.NUSimEnterprise,
            '/nuage/api/v5_0/enterprises',
            '/nuage/api/v5_0/enterprises/<entity_id>'
        )
        self.api.add_resource(
            sim.NUSimUser,
            '/nuage/api/v5_0/users',
            '/nuage/api/v5_0/users/<entity_id>',
            '/nuage/api/v5_0/<parent_type>/<parent_id>/users'
        )
        self.api.add_resource(
            sim.NUSimGroup,
            '/nuage/api/v5_0/groups/<entity_id>',
            '/nuage/api/v5_0/<parent_type>/<parent_id>/groups'
        )

        self.app.run(port=5000, debug=(log_level == 'DEBUG'))


def main():
    NuageVSDSim()
