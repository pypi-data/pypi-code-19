from configparser import ConfigParser, NoOptionError
from fnmatch import fnmatch
from os import environ


class Source:
    """Base class for configuration sources.

    To implement a simple (non-file-based) configuration source,
    subclass this class and override ``__getitem__``.

    ``__getitem__`` should return a string, or raise ``KeyError`` if
    a key isn't found in the configuration source.

    If you are implementing an ambient configuration source (e.g. one
    that reads from environment variables, command-line args, a single
    file in a well-known location, or something else that doesn't
    depend on Walter's search path), you can expose your ``Source``
    subclass to users directly.
    If instead you are implementing a file-based source, see also
    :class:`~walter.sources.FileSource`.
    """
    pass


class FileSource:
    """Base class for file-based configuration sources.

    Because Walter implements searching for configuration files
    internally, and allows for a mix of different types of configuration
    files, a file-based configuration source consists of two classes.

    One is the actual source itself. This is a subclass of
    :class:`~walter.sources.Source` — not this class — and behaves like
    a normal source, except it takes a file-like object as its first
    positional argument, and it is an implementation detail that is not
    exposed to your users.

    The other is the "meta-source", which is a subclass of
    ``FileSource``. It is responsible for two things: determining which
    filenames match the source, and creating new source objects from
    files. Users will create an instance of the meta-source and pass
    that to Walter, which will use it to create source instances.

    While it is possible to override :meth:`match_filename` and
    :meth:`create` entirely, most meta-sources should be able to get by
    with simply setting two properties and adding a docstring:

    * ``source_class``, your actual source class.
    * ``pattern``, a default file pattern to match on, which can be
      either a shell glob or a compiled regular expression.

    Unless you override ``__init__``, your meta-source will accept a
    ``filename`` arg that allows users to override ``pattern``; any
    other keyword arguments given to the meta-source will be passed
    through to the source itself.

    .. example::

        A file-based source that uses JSON might look like this::

            class JsonSource(Source):
                def __init__(self, f, allow_comments=True):
                    self.data = json.load(
                        f, allow_comments=allow_comments)

                def __getitem__(self, key):
                    return self.data[key]

            class JsonFileSource(FileSource):
                \"\"\"A file source for JSON blobs.

                :param allow_comments: Whether to allow comments.
                :type allow_comments: bool
                \"\"\"
                source_class = JsonSource
                pattern = "config.json"
    """

    def __init__(self, filename=None, **kwargs):
        if filename is not None:
            self.pattern = filename
        self.kwargs = kwargs

    def match_filename(self, filename):
        """Test a filename to see if it matches this source.

        :return: Whether the filename matches this source.
        :rtype: bool
        """
        if hasattr(self.pattern, 'match'):
            return bool(self.pattern.match(filename))
        return fnmatch(filename, self.pattern)

    def create(self, file_obj):
        """Return a new source with the given file object.

        :return: A new source object.
        """
        return self.source_class(file_obj, **self.kwargs)


class EnvironmentSource(Source):
    """Source that extracts values from environment variables.

    :param prefix: Prefix to expect at the beginning of environment
        variable names.
    :type prefix: str
    """

    def __init__(self, prefix=''):
        self.prefix = prefix

    def __getitem__(self, key):
        return environ[self.prefix + key]


class IniSource(Source):
    def __init__(self, file, section='settings'):
        self.section = section
        self.parser = ConfigParser()
        self.parser.read_file(file)

    def __getitem__(self, key):
        try:
            return self.parser.get(self.section, key)
        except NoOptionError:
            raise KeyError(key)


class IniFileSource(FileSource):
    """Source that extracts values from ``.ini`` files.

    Files should be in the format expected by
    :class:`configparser.ConfigParser`.

    :param section: Section header to look for settings under. Defaults
    to ``settings``.
    :type section: str
    """
    pattern = "settings.ini"
    source_class = IniSource
