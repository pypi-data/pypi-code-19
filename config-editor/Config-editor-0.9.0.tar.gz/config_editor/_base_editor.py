#    Copyright 2017 Alexey Stepanov aka penguinolog

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Config file editor base class."""

from __future__ import absolute_import

import abc
import copy
import threading

import six


BaseClass = type.__new__(abc.ABCMeta, 'BaseClass', (object, ), {})


class BaseEditor(BaseClass):
    """Base class for editors."""

    __slots__ = (
        '_filename',
        '_file_handler',
        '__revert_on_exception',
        '__original_content',
        '__content',
        '__content_lock'
    )

    # noinspection PyMissingConstructor
    def __init__(
            self,
            source,
            revert_on_exception=True,
    ):
        """Config file editor context manager.

        :param source: source to work on (file name of handler)
        :type source: typing.Union[io.StringIO, str]
        :param revert_on_exception: revert all changes if exception raised
        :type revert_on_exception: bool
        """
        if isinstance(source, six.string_types):
            self._filename = source
            self._file_handler = None
        else:
            self._filename = None
            self._file_handler = source
        self.__revert_on_exception = revert_on_exception
        self.__original_content = None
        self.__content = None
        self.__content_lock = threading.RLock()

    def __enter__(self):
        """Context manager."""
        with self.lock:
            self.__original_content = self._read_source()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager close."""
        with self.lock:
            if self.revert_on_exception and exc_type:
                return
            if self.content != self.__original_content:
                self._write_source()

    @property
    def revert_on_exception(self):
        """Revert all changes if exception raised.

        :rtype: bool
        """
        return self.__revert_on_exception

    @property
    def lock(self):
        """RLock."""
        return self.__content_lock

    # noinspection PyNoneFunctionAssignment
    @property
    def content(self):
        """Parsed content."""
        with self.lock:
            if self.__content is None:
                if self.__original_content is None:
                    self.__original_content = self._read_source()
                self.__content = copy.deepcopy(self.__original_content)
            return self.__content

    @content.setter
    def content(self, new_content):
        """New content setter."""
        with self.lock:
            self.__content = new_content

    @property
    def original_content(self):
        """Copy of original content."""
        return copy.deepcopy(self.__original_content)

    def _replace_original_content(self):
        """Replace original content by current."""
        with self.lock:
            self.__original_content = copy.deepcopy(self.__content)

    @abc.abstractmethod
    def _read_source(self):
        """Read content from source."""

    @abc.abstractmethod
    def _write_source(self):
        """Write content to the target format."""

    @abc.abstractmethod
    def __repr__(self):
        """Repr."""
