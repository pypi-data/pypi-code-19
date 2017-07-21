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

"""Config (INI) file editor."""

from __future__ import absolute_import

import collections

from six.moves import configparser
import six

from ._base_editor import BaseEditor


class ConfigEditor(BaseEditor):
    """Config (INI) editor."""

    __slots__ = (
        "__defaults",
        "__dict_type",
        "__allow_no_value",
    )

    def __init__(
        self,
        source,
        revert_on_exception=True,
        defaults=None,
        dict_type=collections.OrderedDict,
        allow_no_value=False,
        lock_descriptor=False,
        no_block=False
    ):
        """Config (INI) file editor context manager.

        :param source: source to work on
        :type source: typing.Union[io.StringIO, str]
        :param revert_on_exception: revert all changes if exception raised
        :type revert_on_exception: bool
        :param defaults: When `defaults' is given, it is initialized into the
                         dictionary or intrinsic defaults.
        :type defaults: typing.Dict[str, typing.Any]
        :param dict_type: Dictionary type class for content
        :type dict_type: type
        :param allow_no_value: Allow keys without values (interpreted as None)
        :type allow_no_value: bool
        :param lock_descriptor: lock file descriptor during operation
        :type lock_descriptor: bool
        :param no_block: Raise exception if lock not acquired.
        :type no_block: bool
        """
        self.__defaults = defaults
        self.__dict_type = dict_type
        self.__allow_no_value = allow_no_value
        super(
            ConfigEditor, self
        ).__init__(
            source=source,
            revert_on_exception=revert_on_exception,
            lock_descriptor=lock_descriptor,
            no_block=no_block,
        )

    @property
    def defaults(self):
        """Dictionary or intrinsic defaults.

        :rtype: typing.Dict[str, typing.Any]
        """
        return self.__defaults

    @property
    def dict_type(self):
        """Dictionary type class for content."""
        return self.__dict_type

    @property
    def allow_no_value(self):
        """Allow keys without values (interpreted as None).

        :rtype: bool
        """
        return self.__allow_no_value

    @property
    def text(self):
        """Content as text.

        :rtype: str
        """
        config = self.__rebuild_parser()
        self.__refill_config(config)

        # Use StringIO as file IO
        stream = six.StringIO()
        config.write(stream)
        stream.seek(0)
        return stream.read()

    def __repr__(self):  # pragma: no cover
        """Repr."""
        return (
            "<{cls}("
            "source={source!r}, "
            "revert_on_exception={self.revert_on_exception!r}, "
            "defaults={self.defaults!r}, "
            "dict_type={self.dict_type!r}, "
            "allow_no_value={self.allow_no_value!r}, "
            ") at {id}>".format(
                cls=self.__class__.__name__,
                source=self._filename or self._file_descriptor,
                self=self,
                id=id(self)
            )
        )

    def __rebuild_parser(self):
        """Rebuild ConfigParser object.

        :rtype: configparser.ConfigParser
        """
        return configparser.ConfigParser(
            defaults=self.defaults,
            dict_type=self.dict_type,
            allow_no_value=self.allow_no_value
        )

    def __refill_config(self, config):
        """Refill config from content.

        Fill manually due to no update in 2.7
        """
        for section, data in self.content.items():
            config.add_section(section)
            for option, value in data.items():
                config.set(section, option, value)

    def _read_source(self):
        """Read content from source."""
        config = self.__rebuild_parser()
        # pylint: disable=deprecated-method
        self._file_descriptor.seek(0)
        if six.PY3:  # pragma: no cover
            # noinspection PyUnresolvedReferences
            config.read_file(self._file_descriptor)
        else:  # pragma: no cover
            # noinspection PyDeprecation
            config.readfp(self._file_descriptor)
        # pylint: enable=deprecated-method
        # noinspection PyArgumentList
        return collections.OrderedDict(
            [
                (
                    section,
                    collections.OrderedDict(config.items(section=section))
                )
                for section in config.sections()
            ]
        )

    def _write_source(self):
        """Write content to the target format."""
        config = self.__rebuild_parser()
        self.__refill_config(config)

        self._file_descriptor.seek(0)
        config.write(self._file_descriptor)
        self._file_descriptor.flush()
