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
import fcntl
import threading


BaseClass = type.__new__(abc.ABCMeta, 'BaseClass', (object, ), {})


class BaseEditor(BaseClass):
    """Base class for editors."""

    __slots__ = (
        '_file_descriptor',
        '__revert_on_exception',
        '__original_content',
        '__content',
        '__content_lock',
        '__lock_descriptor',
        '__no_block',
    )

    # noinspection PyMissingConstructor
    def __init__(
        self,
        source,
        revert_on_exception=True,
        lock_descriptor=False,
        no_block=False
    ):
        """Config file editor context manager.

        :param source: source to work on (file descriptor)
        :type source: typing.Union[io.StringIO, str]
        :param revert_on_exception: revert all changes if exception raised
        :type revert_on_exception: bool
        :param lock_descriptor: lock file descriptor during operation
        :type lock_descriptor: bool
        :param no_block: Raise exception if lock not acquired.
        :type no_block: bool
        """
        self._file_descriptor = source
        self.__revert_on_exception = revert_on_exception
        self.__original_content = None
        self.__content = None
        self.__content_lock = threading.RLock()
        self.__lock_descriptor = lock_descriptor
        self.__no_block = no_block

    def _lock_descriptor(self):
        """Lock file handler during operation."""
        if self.lock_descriptor:
            cmd = fcntl.LOCK_EX
            if self.no_block:
                cmd |= fcntl.LOCK_NB
            fcntl.lockf(
                self._file_descriptor,
                cmd,
            )

    def _unlock_descriptor(self):
        """Unlock file handler during operation."""
        if self.lock_descriptor:
            fcntl.lockf(
                self._file_descriptor,
                fcntl.LOCK_UN,
            )

    def __enter__(self):
        """Context manager."""
        self.lock.acquire()
        self._lock_descriptor()
        self.__original_content = self._read_source()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager close."""
        try:
            if self.revert_on_exception and exc_type:
                return
            if self.content != self.__original_content:
                self._write_source()
                self._replace_original_content()
        finally:
            self._unlock_descriptor()
            self.lock.release()

    @property
    def lock_descriptor(self):
        """Lock file handler during operation.

        :rtype: bool
        """
        return self.__lock_descriptor

    @property
    def no_block(self):
        """Raise exception if lock not acquired.

        :rtype: bool
        """
        return self.__no_block

    @property
    def revert_on_exception(self):
        """Revert all changes if exception raised.

        :rtype: bool
        """
        return self.__revert_on_exception

    @property
    def lock(self):
        """RLock.

        :rtype: threading.RLock
        """
        return self.__content_lock

    # noinspection PyNoneFunctionAssignment
    @property
    def content(self):
        """Parsed content."""
        if self.__content is None:
            with self.lock:
                if self.__original_content is None:
                    self.__original_content = self._read_source()
                self.__content = copy.deepcopy(self.__original_content)
        return self.__content

    @content.setter
    def content(self, new_content):
        """New content setter."""
        self.__content = new_content

    @property
    def text(self):
        """Content as text.

        :rtype: str
        """
        raise NotImplementedError()  # pragma: no cover

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
