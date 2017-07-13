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

"""YAML file editor."""

from __future__ import absolute_import
import collections

import six
import yaml

from ._base_editor import BaseEditor

yaml.add_representer(
    collections.OrderedDict,
    lambda self, data: self.represent_mapping(
        'tag:yaml.org,2002:map',
        six.iteritems(data)
    ),
    yaml.SafeDumper
)


class YamlEditor(BaseEditor):
    """Json data editor."""

    __slots__ = (
        '__canonical',
        '__indent',
        '__width',
        '__allow_unicode'
    )

    def __init__(
            self,
            source,
            revert_on_exception=True,
            canonical=None,
            indent=None,
            width=None,
            allow_unicode=None,
    ):
        """JSON file editor context manager.

        :param source: source to work on
        :type source: typing.Union[io.StringIO, str]
        :param revert_on_exception: revert all changes if exception raised
        :type revert_on_exception: bool
        :param canonical: use the canonical YAML format
        :type canonical: typing.Optional[bool]
        :param indent: indent for elements.
        :type indent: typing.Optional[int]
        :param width: width
        :type width: typing.Optional[int]
        :param allow_unicode: Allow unicode in output.
        :type allow_unicode: typing.Optional[bool]
        """
        self.__canonical = canonical
        self.__indent = indent
        self.__width = width
        self.__allow_unicode = allow_unicode

        super(
            YamlEditor, self
        ).__init__(
            source=source,
            revert_on_exception=revert_on_exception
        )

    @property
    def canonical(self):
        """Use the canonical YAML format."""
        return self.__canonical

    @property
    def indent(self):
        """Indent for elements."""
        return self.__indent

    @property
    def width(self):
        """Width."""
        return self.__width

    @property
    def allow_unicode(self):
        """Allow unicode in output."""
        return self.__allow_unicode

    def __repr__(self):
        """Repr."""
        return (
            "<{cls}("
            "source={source!r}, "
            "revert_on_exception={self.revert_on_exception!r}, "
            "canonical={self.canonical!r}, "
            "indent={self.indent!r}, "
            "width={self.width!r}, "
            "allow_unicode={self.allow_unicode!r}, "
            ") at {id}>".format(
                cls=self.__class__.__name__,
                source=self._filename or self._file_handler,
                self=self,
                id=id(self)
            )
        )

    def _read_source(self):
        """Read content from source."""
        if self._filename:
            with open(self._filename) as file_handler:
                return yaml.safe_load(
                    file_handler,
                )
        self._file_handler.seek(0)
        return yaml.safe_load(
            self._file_handler,
        )

    def _write_source(self):
        """Write content to the target format."""
        if self._filename:
            with open(self._filename, 'w') as file_handler:
                yaml.safe_dump(
                    self.content,
                    file_handler,
                    canonical=self.canonical,
                    indent=self.indent,
                    width=self.width,
                    allow_unicode=self.allow_unicode
                )
                file_handler.flush()
        else:
            self._file_handler.seek(0)
            yaml.safe_dump(
                self.content,
                self._file_handler,
                canonical=self.canonical,
                indent=self.indent,
                width=self.width,
                allow_unicode=self.allow_unicode
            )
            self._file_handler.flush()
