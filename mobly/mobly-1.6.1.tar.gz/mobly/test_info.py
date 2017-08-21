# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import copy
import functools
import inspect
import logging
import sys


class TestInfo(object):
    """Container class for runtime information of a test.

    Attributes:
    """

    TAG = None

    def __init__(self, test_name):
        """Constructor of BaseTestClass.

        The constructor takes a config_parser.TestRunConfig object and which has
        all the information needed to execute this test class, like log_path
        and controller configurations. For details, see the definition of class
        config_parser.TestRunConfig.

        Args:
            configs: A config_parser.TestRunConfig object.
        """
        self.name = test_name
        self.output_dir = 