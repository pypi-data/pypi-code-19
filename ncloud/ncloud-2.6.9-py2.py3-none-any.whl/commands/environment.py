# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-
"""
Subcommands for getting the supported environments.
"""
import logging
from functools import partial
import os

from ncloud.commands.command import (BaseList, build_subparser, Command,
                                     DEFAULT)
from ncloud.config import ENVIRONMENTS

logger = logging.getLogger()


class List(BaseList):
    """
    List the supported environments.
    """
    @classmethod
    def parser(cls, subparser):
        environments = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)
        environments.add_argument("-t", "--job-type",
                                  help="Filter the list of supported "
                                       "environments by job type ('training' "
                                       "or 'interact').")
        environments.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, job_type=None):
        vals = List.BASE_ARGS
        vals.update({'job_type': job_type})

        return List.api_call(config, ENVIRONMENTS, params=vals,
                             return_json=True)


class Default(Command):
    """
    Get the default environment.
    """
    @classmethod
    def parser(cls, subparser):
        default_env = subparser.add_parser(DEFAULT.name,
                                           aliases=DEFAULT.aliases,
                                           help=Default.__doc__,
                                           description=Default.__doc__)
        default_env.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        default_env_path = os.path.join(ENVIRONMENTS, "default")
        return Default.api_call(config, default_env_path, method="GET",
                                params={}, return_json=True)


parser = partial(
    build_subparser, 'environment', ['e'], __doc__,
    (List, Default)

)
