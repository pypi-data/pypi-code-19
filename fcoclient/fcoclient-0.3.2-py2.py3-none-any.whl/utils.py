# Copyright (c) 2017 XLAB d.o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module with various utility functions.
"""

import getpass
import json
import sys
import time


def output_json(data, file=sys.stdout):
    """
    Output indented json data to selected file like object.

    Args:
        data: Data to dump
        file: File like object that should receive serialized data
            (default: standard output)
    """
    json.dump(data, file, indent=2, separators=(",", ": "), sort_keys=True)


def delay(delay_in_secs=5):
    """
    Delay that should be inserted between tho calls when polling API.

    Args:
        delay_in_secs: Delay in seconds (default: 5)
    """
    time.sleep(delay_in_secs)


def prompt(text, is_password=False):
    """
    Interactively prompt user for input.

    Args:
        text: Text that should be displayed to user
        is_password: Set to True in order to avoid echoing the password
    """
    text += ": "
    if is_password:
        return getpass.getpass(text)
    if sys.version_info[0] > 2:
        return input(text)
    else:
        return raw_input(text)
