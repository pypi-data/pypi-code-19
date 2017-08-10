# Copyright (C) 2016 Allen Li
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

"""ASCII character table.

Constants:
CONTROL_CHARS -- Mapping of ints to control character information

Functions:
is_printable -- Return whether character is printable
"""

import collections
import csv
import io

import pkg_resources

CONTROL_CHARS = None
ControlChar = collections.namedtuple(
    'ControlChar', 'value,abbrev,unicode,repr,name')


def is_printable(char: int):
    """Return whether char is printable."""
    return char not in CONTROL_CHARS


def _init_control_chars():
    """Initialize CONTROL_CHARS constant."""
    global CONTROL_CHARS
    CONTROL_CHARS = {
        char.value: char
        for char in _load_control_chars()
    }


def _load_control_chars():
    """Yield ControlChars read from the package's list."""
    with _open_control_chars_file() as file:
        yield from _load_control_chars_from_file(file)


def _open_control_chars_file():
    """Open control chars file shipped with this package."""
    binary_stream = pkg_resources.resource_stream(__name__, 'ascii.csv')
    return io.TextIOWrapper(binary_stream)


def _load_control_chars_from_file(file):
    """Yield ControlChars read from a CSV file."""
    reader = csv.reader(file)
    for row in reader:
        row[0] = int(row[0])
        yield ControlChar(*row)


_init_control_chars()
