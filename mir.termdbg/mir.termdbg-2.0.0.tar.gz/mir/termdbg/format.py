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

"""termdbg output formatting.

Functions:
format_char -- Format a char for printing.
"""

import mir.termdbg.ascii as asciilib


def format_char(char: int):
    """Format a char for printing."""
    if asciilib.is_printable(char):
        return _format_printable(char)
    else:
        return _format_control(char)


def _format_printable(char: int):
    """Format a printable char."""
    return f'{_format_generic(char)}, {_printable_char_string(char)}'


def _format_generic(char: int):
    """Format generic char."""
    return f'{char:3d}, 0o{char:03o}, 0x{char:02X}'


def _printable_char_string(char: int):
    """Format printable char visibly."""
    char = chr(char)
    if char == ' ':
        return 'SPC'
    else:
        return char


def _format_control(char: int):
    """Format a control char."""
    charinfo = asciilib.CONTROL_CHARS[char]
    return (f'{_format_generic(char)}, {charinfo.abbrev}, {charinfo.unicode},'
            f' {charinfo.repr}, {charinfo.name}')
