"""
Utilities for working with the terminal.

This should probably be replaced with some third-party package, but where's the
fun in that?
"""

import os
import sys


_OS_POSIX = os.name == 'posix'


if _OS_POSIX:
    from . import _unix
else:
    from . import _windows


class Terminal:

    def __init__(self, input_stream=sys.stdin, output_stream=sys.stdout, error_stream=sys.stderr):
        self._input_stream = input_stream
        self._output_stream = output_stream
        self._error_stream = error_stream

    def _get_character(self):
        """
        Bare-bones (but cross-platform) implementation of getchar.
        """
        if _OS_POSIX:
            return _unix.get_character(self._input_stream)
        else:
            return _windows.get_character()

    def get_character(self, prompt=None, new_line=True):
        if prompt:
            self._output_stream.write(prompt)
            self._output_stream.flush()

        character = self._get_character().decode('utf-8')

        if new_line:
            self._output_stream.write('\n')

        return character

    def clear(self):
        if _OS_POSIX:
            _unix.clear(self._output_stream)
        else:
            _windows.clear()
