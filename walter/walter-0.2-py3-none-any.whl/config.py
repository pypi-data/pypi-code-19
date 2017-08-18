from itertools import chain

import appdirs
import attr

from .na import NA
from .source_list import SourceList


@attr.s(frozen=True)
class ConfigError(ValueError):
    key = attr.ib()
    error_type = attr.ib()  # one of 'not_found', 'cast_fail' TODO: validate
    exception = attr.ib(default=None)

    def __str__(self):
        if self.error_type == 'not_found':
            return "{} not set".format(self.key)
        return "{} set incorrectly, got {}: {}".format(
            self.key,
            self.exception.__class__.__name__,
            str(self.exception),
        )


@attr.s(frozen=True)
class ConfigErrors(ValueError):
    errors = attr.ib()

    def __str__(self):
        not_found_count = sum(
            1 for x in self.errors if x.error_type == 'not_found')
        cast_fail_count = sum(
            1 for x in self.errors if x.error_type == 'cast_fail')
        summary_line = "{} configuration values not set, {} invalid".format(
            not_found_count, cast_fail_count)
        return '\n'.join(chain(
            (summary_line, ''),
            (str(x) for x in self.errors)
        ))


class Config:
    """Creates a config object.

    :param author: Name of the person or company that created this
        program. Used on Windows to set the default search path.
    :type author: str
    :param name: Name of this program. Used on Windows to set the
        default search path.
    :type name: str
    :param sources: An iterable of :class:`~walter.sources.Source`
        objects to pull configuration from. Defaults to the following:

        - :class:`~walter.sources.EnvironmentSource`
        - :class:`~walter.sources.IniFileSource`
    :type sources: iterable
    :param search_path: An iterable of directories to search for
        configuration files. Defaults to the current directory,
        followed by an appropriate user and site config directory
        depending on the operating system.
    :type search_path: iterable
    """

    def __init__(self, author, name, sources=None, search_path=None):
        if search_path is None:
            search_path = (
                '.',
                appdirs.user_config_dir(name, author),
                appdirs.site_config_dir(name, author),
            )
        self.search_path = search_path
        self.source = SourceList(search_path=search_path,
                                 input_sources=sources)
        self.values = []
        self.help_text = {}
        self.errors = []
        self.collect_errors = False

    def _report_error(self, error):
        if self.collect_errors:
            self.errors.append(error)
        else:
            raise error

    def __enter__(self):
        self.collect_errors = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO: handle properly
        self.collect_errors = False
        if exc_value is None and self.errors:
            raise ConfigErrors(errors=self.errors)

    def get(self, key, cast=None, help_text=None):
        """Get a configuration parameter.

        :param key: The name of the configuration parameter to get.
        :type key: str
        :param cast: A function to call on the returned parameter to
            convert it to the appropriate value.
        :type cast: function
        :param help_text: Help text to display to the user, explaining
            the usage of this parameter.
        :type help_text: str
        """
        self.values.append(key)
        if help_text is not None:
            self.help_text[key] = help_text

        try:
            raw_value = self.source[key]
        except KeyError:
            self._report_error(ConfigError(key=key, error_type='not_found'))
            return NA

        if cast is not None:
            try:
                value = cast(raw_value)
            except Exception as e:
                self._report_error(ConfigError(key=key, error_type='cast_fail',
                                               exception=e))
                return NA
        else:
            value = raw_value

        return value
