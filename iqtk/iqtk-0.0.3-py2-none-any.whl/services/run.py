#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 The Regents of the University of California
#
# Licensed under the BSD-3-clause license (the "License"); you may not
# use this file except in compliance with the License.
# You are provided a copy of the license in LICENSE.md at the root of
# this project.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Service runner entrypoint for """

import argparse
import logging

from inquiry.services.api import APIService
from inquiry.services.flow import WorkflowService
from inquiry.services.iot import IOTHandlerService
from inquiry.services.base import ServiceRegistry


def get_iqtk_registry():
    return ServiceRegistry({
        'flow_runner': WorkflowService,
        'iot_handler': IOTHandlerService,
        'api_service': APIService
        })


def main():

    sr = get_iqtk_registry()

    logging.getLogger().setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    args = parser.parse_args()
    sr.run_service(args.service)


if __name__ == '__main__':
    main()
