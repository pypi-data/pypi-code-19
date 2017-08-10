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

"""Terminal attribute contexts."""

import termios
import tty


class _TermAttrsContext:

    """Restore terminal attributes of fd on context exit."""

    def __init__(self, fd):
        """Initialize instance."""
        self._fd = fd
        self._old_attrs = None

    def __enter__(self):
        self._old_attrs = termios.tcgetattr(self._fd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        termios.tcsetattr(self._fd, termios.TCSAFLUSH, self._old_attrs)


class RawTerm(_TermAttrsContext):
    """Set terminal to raw mode within the context."""

    def __init__(self, fd):
        """Initialize instance."""
        self._fd = fd

    def __enter__(self):
        super().__enter__()
        tty.setraw(self._fd)
