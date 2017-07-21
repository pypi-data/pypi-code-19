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

"""JSON file editor."""

from __future__ import absolute_import

import json

from ._base_editor import BaseEditor


class JsonEditor(BaseEditor):
    """Json data editor."""

    __slots__ = (
        '__ensure_ascii',
        '__allow_nan',
        '__indent',
        '__sort_keys',
        '__object_pairs_hook'
    )

    def __init__(
        self,
        source,
        revert_on_exception=True,
        ensure_ascii=True,
        allow_nan=True,
        indent=None,
        sort_keys=False,
        object_pairs_hook=None,
        lock_descriptor=False,
        no_block=False
    ):
        """JSON file editor context manager.

        :param source: source to work on
        :type source: typing.Union[io.StringIO, str]
        :param revert_on_exception: revert all changes if exception raised
        :type revert_on_exception: bool
        :param ensure_ascii: return value can contain non-ASCII characters
        :type ensure_ascii: bool
        :param allow_nan: serialize out of range ``float`` values
                          (``nan``, ``inf``, ``-inf``)
        :type allow_nan: bool
        :param indent: indent for elements.
        :type indent: typing.Optional[int]
        :param sort_keys: Sort object items by key
        :type sort_keys: bool
        :param object_pairs_hook: optional function that will be called
                                  with the result of any object literal
                                  decoded with an ordered list of pairs.
        :type object_pairs_hook: typing.Optional[
                                     typing.Callable[[typing.Iterable], ...]
                                 ]
        :param lock_descriptor: lock file descriptor during operation
        :type lock_descriptor: bool
        :param no_block: Raise exception if lock not acquired.
        :type no_block: bool
        """
        self.__ensure_ascii = ensure_ascii
        self.__allow_nan = allow_nan
        self.__indent = indent
        self.__sort_keys = sort_keys
        self.__object_pairs_hook = object_pairs_hook

        super(
            JsonEditor, self
        ).__init__(
            source=source,
            revert_on_exception=revert_on_exception,
            lock_descriptor=lock_descriptor,
            no_block=no_block,
        )

    @property
    def ensure_ascii(self):
        """Return value can contain non-ASCII characters.

        :rtype: bool
        """
        return self.__ensure_ascii

    @property
    def allow_nan(self):
        """Serialize out of range ``float`` values.

        :rtype: bool
        """
        return self.__allow_nan

    @property
    def indent(self):
        """Indent for elements.

        :rtype: typing.Optional[int]
        """
        return self.__indent

    @property
    def sort_keys(self):
        """Sort object items by key.

        :rtype: str
        """
        return self.__sort_keys

    @property
    def object_pairs_hook(self):
        """Hook for object pairs.

        :rtype: typing.Optional[typing.Callable[[typing.Iterable], ...]]
        """
        return self.__object_pairs_hook

    def __repr__(self):  # pragma: no cover
        """Repr."""
        return (
            "<{cls}("
            "source={source!r}, "
            "revert_on_exception={self.revert_on_exception!r}, "
            "ensure_ascii={self.ensure_ascii!r}, "
            "allow_nan={self.allow_nan!r}, "
            "indent={self.indent!r}, "
            "sort_keys={self.sort_keys!r}, "
            "object_pairs_hook={self.object_pairs_hook!r}, "
            ") at {id}>".format(
                cls=self.__class__.__name__,
                source=self._filename or self._file_descriptor,
                self=self,
                id=id(self)
            )
        )

    @property
    def text(self):
        """Content as text.

        :rtype: str
        """
        return json.dumps(
            self.content,
            ensure_ascii=self.ensure_ascii,
            allow_nan=self.allow_nan,
            indent=self.indent,
            sort_keys=self.sort_keys
        )

    def _read_source(self):
        """Read content from source."""
        self._file_descriptor.seek(0)
        return json.load(
            self._file_descriptor,
            object_pairs_hook=self.object_pairs_hook
        )

    def _write_source(self):
        """Write content to the target format."""
        self._file_descriptor.seek(0)
        json.dump(
            self.content,
            self._file_descriptor,
            ensure_ascii=self.ensure_ascii,
            allow_nan=self.allow_nan,
            indent=self.indent,
            sort_keys=self.sort_keys
        )
        self._file_descriptor.flush()
