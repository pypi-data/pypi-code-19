# coding: utf-8
# $Id: __init__.py 8073 2017-05-23 12:41:45Z milde $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Miscellaneous utilities for the documentation utilities.
"""

__docformat__ = 'reStructuredText'

import sys
import os
import os.path
import re
import itertools
import warnings
import unicodedata
from docutils import ApplicationError, DataError
from docutils import nodes
import docutils.io
from docutils.utils.error_reporting import ErrorOutput, SafeString


class SystemMessage(ApplicationError):

    def __init__(self, system_message, level):
        Exception.__init__(self, system_message.astext())
        self.level = level


class SystemMessagePropagation(ApplicationError): pass


class Reporter:

    """
    Info/warning/error reporter and ``system_message`` element generator.

    Five levels of system messages are defined, along with corresponding
    methods: `debug()`, `info()`, `warning()`, `error()`, and `severe()`.

    There is typically one Reporter object per process.  A Reporter object is
    instantiated with thresholds for reporting (generating warnings) and
    halting processing (raising exceptions), a switch to turn debug output on
    or off, and an I/O stream for warnings.  These are stored as instance
    attributes.

    When a system message is generated, its level is compared to the stored
    thresholds, and a warning or error is generated as appropriate.  Debug
    messages are produced if the stored debug switch is on, independently of
    other thresholds.  Message output is sent to the stored warning stream if
    not set to ''.

    The Reporter class also employs a modified form of the "Observer" pattern
    [GoF95]_ to track system messages generated.  The `attach_observer` method
    should be called before parsing, with a bound method or function which
    accepts system messages.  The observer can be removed with
    `detach_observer`, and another added in its place.

    .. [GoF95] Gamma, Helm, Johnson, Vlissides. *Design Patterns: Elements of
       Reusable Object-Oriented Software*. Addison-Wesley, Reading, MA, USA,
       1995.
    """

    levels = 'DEBUG INFO WARNING ERROR SEVERE'.split()
    """List of names for system message levels, indexed by level."""

    # system message level constants:
    (DEBUG_LEVEL,
     INFO_LEVEL,
     WARNING_LEVEL,
     ERROR_LEVEL,
     SEVERE_LEVEL) = range(5)

    def __init__(self, source, report_level, halt_level, stream=None,
                 debug=False, encoding=None, error_handler='backslashreplace'):
        """
        :Parameters:
            - `source`: The path to or description of the source data.
            - `report_level`: The level at or above which warning output will
              be sent to `stream`.
            - `halt_level`: The level at or above which `SystemMessage`
              exceptions will be raised, halting execution.
            - `debug`: Show debug (level=0) system messages?
            - `stream`: Where warning output is sent.  Can be file-like (has a
              ``.write`` method), a string (file name, opened for writing),
              '' (empty string) or `False` (for discarding all stream messages)
              or `None` (implies `sys.stderr`; default).
            - `encoding`: The output encoding.
            - `error_handler`: The error handler for stderr output encoding.
        """

        self.source = source
        """The path to or description of the source data."""

        self.error_handler = error_handler
        """The character encoding error handler."""

        self.debug_flag = debug
        """Show debug (level=0) system messages?"""

        self.report_level = report_level
        """The level at or above which warning output will be sent
        to `self.stream`."""

        self.halt_level = halt_level
        """The level at or above which `SystemMessage` exceptions
        will be raised, halting execution."""

        if not isinstance(stream, ErrorOutput):
            stream = ErrorOutput(stream, encoding, error_handler)

        self.stream = stream
        """Where warning output is sent."""

        self.encoding = encoding or getattr(stream, 'encoding', 'ascii')
        """The output character encoding."""

        self.observers = []
        """List of bound methods or functions to call with each system_message
        created."""

        self.max_level = -1
        """The highest level system message generated so far."""

    def set_conditions(self, category, report_level, halt_level,
                       stream=None, debug=False):
        warnings.warn('docutils.utils.Reporter.set_conditions deprecated; '
                      'set attributes via configuration settings or directly',
                      DeprecationWarning, stacklevel=2)
        self.report_level = report_level
        self.halt_level = halt_level
        if not isinstance(stream, ErrorOutput):
            stream = ErrorOutput(stream, self.encoding, self.error_handler)
        self.stream = stream
        self.debug_flag = debug

    def attach_observer(self, observer):
        """
        The `observer` parameter is a function or bound method which takes one
        argument, a `nodes.system_message` instance.
        """
        self.observers.append(observer)

    def detach_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer(message)

    def system_message(self, level, message, *children, **kwargs):
        """
        Return a system_message object.

        Raise an exception or generate a warning if appropriate.
        """
        # `message` can be a `string`, `unicode`, or `Exception` instance.
        if isinstance(message, Exception):
            message = SafeString(message)

        attributes = kwargs.copy()
        if 'base_node' in kwargs:
            source, line = get_source_line(kwargs['base_node'])
            del attributes['base_node']
            if source is not None:
                attributes.setdefault('source', source)
            if line is not None:
                attributes.setdefault('line', line)
                # assert source is not None, "node has line- but no source-argument"
        if not 'source' in attributes: # 'line' is absolute line number
            try: # look up (source, line-in-source)
                source, line = self.get_source_and_line(attributes.get('line'))
                # print "locator lookup", kwargs.get('line'), "->", source, line
            except AttributeError:
                source, line = None, None
            if source is not None:
                attributes['source'] = source
            if line is not None:
                attributes['line'] = line
        # assert attributes['line'] is not None, (message, kwargs)
        # assert attributes['source'] is not None, (message, kwargs)
        attributes.setdefault('source', self.source)

        msg = nodes.system_message(message, level=level,
                                   type=self.levels[level],
                                   *children, **attributes)
        if self.stream and (level >= self.report_level
                            or self.debug_flag and level == self.DEBUG_LEVEL
                            or level >= self.halt_level):
            self.stream.write(msg.astext() + '\n')
        if level >= self.halt_level:
            raise SystemMessage(msg, level)
        if level > self.DEBUG_LEVEL or self.debug_flag:
            self.notify_observers(msg)
        self.max_level = max(level, self.max_level)
        return msg

    def debug(self, *args, **kwargs):
        """
        Level-0, "DEBUG": an internal reporting issue. Typically, there is no
        effect on the processing. Level-0 system messages are handled
        separately from the others.
        """
        if self.debug_flag:
            return self.system_message(self.DEBUG_LEVEL, *args, **kwargs)

    def info(self, *args, **kwargs):
        """
        Level-1, "INFO": a minor issue that can be ignored. Typically there is
        no effect on processing, and level-1 system messages are not reported.
        """
        return self.system_message(self.INFO_LEVEL, *args, **kwargs)

    def warning(self, *args, **kwargs):
        """
        Level-2, "WARNING": an issue that should be addressed. If ignored,
        there may be unpredictable problems with the output.
        """
        return self.system_message(self.WARNING_LEVEL, *args, **kwargs)

    def error(self, *args, **kwargs):
        """
        Level-3, "ERROR": an error that should be addressed. If ignored, the
        output will contain errors.
        """
        return self.system_message(self.ERROR_LEVEL, *args, **kwargs)

    def severe(self, *args, **kwargs):
        """
        Level-4, "SEVERE": a severe error that must be addressed. If ignored,
        the output will contain severe errors. Typically level-4 system
        messages are turned into exceptions which halt processing.
        """
        return self.system_message(self.SEVERE_LEVEL, *args, **kwargs)


class ExtensionOptionError(DataError): pass
class BadOptionError(ExtensionOptionError): pass
class BadOptionDataError(ExtensionOptionError): pass
class DuplicateOptionError(ExtensionOptionError): pass


def extract_extension_options(field_list, options_spec):
    """
    Return a dictionary mapping extension option names to converted values.

    :Parameters:
        - `field_list`: A flat field list without field arguments, where each
          field body consists of a single paragraph only.
        - `options_spec`: Dictionary mapping known option names to a
          conversion function such as `int` or `float`.

    :Exceptions:
        - `KeyError` for unknown option names.
        - `ValueError` for invalid option values (raised by the conversion
           function).
        - `TypeError` for invalid option value types (raised by conversion
           function).
        - `DuplicateOptionError` for duplicate options.
        - `BadOptionError` for invalid fields.
        - `BadOptionDataError` for invalid option data (missing name,
          missing data, bad quotes, etc.).
    """
    option_list = extract_options(field_list)
    option_dict = assemble_option_dict(option_list, options_spec)
    return option_dict

def extract_options(field_list):
    """
    Return a list of option (name, value) pairs from field names & bodies.

    :Parameter:
        `field_list`: A flat field list, where each field name is a single
        word and each field body consists of a single paragraph only.

    :Exceptions:
        - `BadOptionError` for invalid fields.
        - `BadOptionDataError` for invalid option data (missing name,
          missing data, bad quotes, etc.).
    """
    option_list = []
    for field in field_list:
        if len(field[0].astext().split()) != 1:
            raise BadOptionError(
                'extension option field name may not contain multiple words')
        name = str(field[0].astext().lower())
        body = field[1]
        if len(body) == 0:
            data = None
        elif len(body) > 1 or not isinstance(body[0], nodes.paragraph) \
              or len(body[0]) != 1 or not isinstance(body[0][0], nodes.Text):
            raise BadOptionDataError(
                  'extension option field body may contain\n'
                  'a single paragraph only (option "%s")' % name)
        else:
            data = body[0][0].astext()
        option_list.append((name, data))
    return option_list

def assemble_option_dict(option_list, options_spec):
    """
    Return a mapping of option names to values.

    :Parameters:
        - `option_list`: A list of (name, value) pairs (the output of
          `extract_options()`).
        - `options_spec`: Dictionary mapping known option names to a
          conversion function such as `int` or `float`.

    :Exceptions:
        - `KeyError` for unknown option names.
        - `DuplicateOptionError` for duplicate options.
        - `ValueError` for invalid option values (raised by conversion
           function).
        - `TypeError` for invalid option value types (raised by conversion
           function).
    """
    options = {}
    for name, value in option_list:
        convertor = options_spec[name]  # raises KeyError if unknown
        if convertor is None:
            raise KeyError(name)        # or if explicitly disabled
        if name in options:
            raise DuplicateOptionError('duplicate option "%s"' % name)
        try:
            options[name] = convertor(value)
        except (ValueError, TypeError), detail:
            raise detail.__class__('(option: "%s"; value: %r)\n%s'
                                   % (name, value, ' '.join(detail.args)))
    return options


class NameValueError(DataError): pass


def decode_path(path):
    """
    Ensure `path` is Unicode. Return `nodes.reprunicode` object.

    Decode file/path string in a failsave manner if not already done.
    """
    # see also http://article.gmane.org/gmane.text.docutils.user/2905
    if isinstance(path, unicode):
        return path
    try:
        path = path.decode(sys.getfilesystemencoding(), 'strict')
    except AttributeError: # default value None has no decode method
        return nodes.reprunicode(path)
    except UnicodeDecodeError:
        try:
            path = path.decode('utf-8', 'strict')
        except UnicodeDecodeError:
            path = path.decode('ascii', 'replace')
    return nodes.reprunicode(path)


def extract_name_value(line):
    """
    Return a list of (name, value) from a line of the form "name=value ...".

    :Exception:
        `NameValueError` for invalid input (missing name, missing data, bad
        quotes, etc.).
    """
    attlist = []
    while line:
        equals = line.find('=')
        if equals == -1:
            raise NameValueError('missing "="')
        attname = line[:equals].strip()
        if equals == 0 or not attname:
            raise NameValueError(
                  'missing attribute name before "="')
        line = line[equals+1:].lstrip()
        if not line:
            raise NameValueError(
                  'missing value after "%s="' % attname)
        if line[0] in '\'"':
            endquote = line.find(line[0], 1)
            if endquote == -1:
                raise NameValueError(
                      'attribute "%s" missing end quote (%s)'
                      % (attname, line[0]))
            if len(line) > endquote + 1 and line[endquote + 1].strip():
                raise NameValueError(
                      'attribute "%s" end quote (%s) not followed by '
                      'whitespace' % (attname, line[0]))
            data = line[1:endquote]
            line = line[endquote+1:].lstrip()
        else:
            space = line.find(' ')
            if space == -1:
                data = line
                line = ''
            else:
                data = line[:space]
                line = line[space+1:].lstrip()
        attlist.append((attname.lower(), data))
    return attlist

def new_reporter(source_path, settings):
    """
    Return a new Reporter object.

    :Parameters:
        `source` : string
            The path to or description of the source text of the document.
        `settings` : optparse.Values object
            Runtime settings.
    """
    reporter = Reporter(
        source_path, settings.report_level, settings.halt_level,
        stream=settings.warning_stream, debug=settings.debug,
        encoding=settings.error_encoding,
        error_handler=settings.error_encoding_error_handler)
    return reporter

def new_document(source_path, settings=None):
    """
    Return a new empty document object.

    :Parameters:
        `source_path` : string
            The path to or description of the source text of the document.
        `settings` : optparse.Values object
            Runtime settings.  If none are provided, a default core set will
            be used.  If you will use the document object with any Docutils
            components, you must provide their default settings as well.  For
            example, if parsing, at least provide the parser settings,
            obtainable as follows::

                settings = docutils.frontend.OptionParser(
                    components=(docutils.parsers.rst.Parser,)
                    ).get_default_values()
    """
    from docutils import frontend
    if settings is None:
        settings = frontend.OptionParser().get_default_values()
    source_path = decode_path(source_path)
    reporter = new_reporter(source_path, settings)
    document = nodes.document(settings, reporter, source=source_path)
    document.note_source(source_path, -1)
    return document

def clean_rcs_keywords(paragraph, keyword_substitutions):
    if len(paragraph) == 1 and isinstance(paragraph[0], nodes.Text):
        textnode = paragraph[0]
        for pattern, substitution in keyword_substitutions:
            match = pattern.search(textnode)
            if match:
                paragraph[0] = nodes.Text(pattern.sub(substitution, textnode))
                return

def relative_path(source, target):
    """
    Build and return a path to `target`, relative to `source` (both files).

    If there is no common prefix, return the absolute path to `target`.
    """
    source_parts = os.path.abspath(source or type(target)('dummy_file')
                                  ).split(os.sep)
    target_parts = os.path.abspath(target).split(os.sep)
    # Check first 2 parts because '/dir'.split('/') == ['', 'dir']:
    if source_parts[:2] != target_parts[:2]:
        # Nothing in common between paths.
        # Return absolute path, using '/' for URLs:
        return '/'.join(target_parts)
    source_parts.reverse()
    target_parts.reverse()
    while (source_parts and target_parts
           and source_parts[-1] == target_parts[-1]):
        # Remove path components in common:
        source_parts.pop()
        target_parts.pop()
    target_parts.reverse()
    parts = ['..'] * (len(source_parts) - 1) + target_parts
    return '/'.join(parts)

def get_stylesheet_reference(settings, relative_to=None):
    """
    Retrieve a stylesheet reference from the settings object.

    Deprecated. Use get_stylesheet_list() instead to
    enable specification of multiple stylesheets as a comma-separated
    list.
    """
    if settings.stylesheet_path:
        assert not settings.stylesheet, (
            'stylesheet and stylesheet_path are mutually exclusive.')
        if relative_to == None:
            relative_to = settings._destination
        return relative_path(relative_to, settings.stylesheet_path)
    else:
        return settings.stylesheet

# Return 'stylesheet' or 'stylesheet_path' arguments as list.
#
# The original settings arguments are kept unchanged: you can test
# with e.g. ``if settings.stylesheet_path:``
#
# Differences to ``get_stylesheet_reference``:
# * return value is a list
# * no re-writing of the path (and therefore no optional argument)
#   (if required, use ``utils.relative_path(source, target)``
#   in the calling script)
def get_stylesheet_list(settings):
    """
    Retrieve list of stylesheet references from the settings object.
    """
    assert not (settings.stylesheet and settings.stylesheet_path), (
            'stylesheet and stylesheet_path are mutually exclusive.')
    stylesheets = settings.stylesheet_path or settings.stylesheet or []
    # programmatically set default can be string or unicode:
    if not isinstance(stylesheets, list):
        stylesheets = [path.strip() for path in stylesheets.split(',')]
    # expand relative paths if found in stylesheet-dirs:
    return [find_file_in_dirs(path, settings.stylesheet_dirs)
            for path in stylesheets]

def find_file_in_dirs(path, dirs):
    """
    Search for `path` in the list of directories `dirs`.

    Return the first expansion that matches an existing file.
    """
    if os.path.isabs(path):
        return path
    for d in dirs:
        if d == '.':
            f = path
        else:
            d = os.path.expanduser(d)
            f = os.path.join(d, path)
        if os.path.exists(f):
            return f
    return path

def get_trim_footnote_ref_space(settings):
    """
    Return whether or not to trim footnote space.

    If trim_footnote_reference_space is not None, return it.

    If trim_footnote_reference_space is None, return False unless the
    footnote reference style is 'superscript'.
    """
    if settings.trim_footnote_reference_space is None:
        return hasattr(settings, 'footnote_references') and \
               settings.footnote_references == 'superscript'
    else:
        return settings.trim_footnote_reference_space

def get_source_line(node):
    """
    Return the "source" and "line" attributes from the `node` given or from
    its closest ancestor.
    """
    while node:
        if node.source or node.line:
            return node.source, node.line
        node = node.parent
    return None, None

def escape2null(text):
    """Return a string with escape-backslashes converted to nulls."""
    parts = []
    start = 0
    while True:
        found = text.find('\\', start)
        if found == -1:
            parts.append(text[start:])
            return ''.join(parts)
        parts.append(text[start:found])
        parts.append('\x00' + text[found+1:found+2])
        start = found + 2               # skip character after escape

def unescape(text, restore_backslashes=False, respect_whitespace=False):
    """
    Return a string with nulls removed or restored to backslashes.
    Backslash-escaped spaces are also removed.
    """
    if restore_backslashes:
        return text.replace('\x00', '\\')
    else:
        for sep in ['\x00 ', '\x00\n', '\x00']:
            text = ''.join(text.split(sep))
        return text

def split_escaped_whitespace(text):
    """
    Split `text` on escaped whitespace (null+space or null+newline).
    Return a list of strings.
    """
    strings = text.split('\x00 ')
    strings = [string.split('\x00\n') for string in strings]
    # flatten list of lists of strings to list of strings:
    return list(itertools.chain(*strings))

def strip_combining_chars(text):
    if isinstance(text, str) and sys.version_info < (3,0):
        return text
    return u''.join([c for c in text if not unicodedata.combining(c)])

def find_combining_chars(text):
    """Return indices of all combining chars in  Unicode string `text`.

    >>> from docutils.utils import find_combining_chars
    >>> find_combining_chars(u'A t̆ab̆lĕ')
    [3, 6, 9]

    """
    if isinstance(text, str) and sys.version_info < (3,0):
        return []
    return [i for i,c in enumerate(text) if unicodedata.combining(c)]

def column_indices(text):
    """Indices of Unicode string `text` when skipping combining characters.

    >>> from docutils.utils import column_indices
    >>> column_indices(u'A t̆ab̆lĕ')
    [0, 1, 2, 4, 5, 7, 8]

    """
    # TODO: account for asian wide chars here instead of using dummy
    # replacements in the tableparser?
    string_indices = range(len(text))
    for index in find_combining_chars(text):
        string_indices[index] = None
    return [i for i in string_indices if i is not None]

east_asian_widths = {'W': 2,   # Wide
                     'F': 2,   # Full-width (wide)
                     'Na': 1,  # Narrow
                     'H': 1,   # Half-width (narrow)
                     'N': 1,   # Neutral (not East Asian, treated as narrow)
                     'A': 1}   # Ambiguous (s/b wide in East Asian context,
                               # narrow otherwise, but that doesn't work)
"""Mapping of result codes from `unicodedata.east_asian_widt()` to character
column widths."""

def column_width(text):
    """Return the column width of text.

    Correct ``len(text)`` for wide East Asian and combining Unicode chars.
    """
    if isinstance(text, str) and sys.version_info < (3,0):
        return len(text)
    try:
        width = sum([east_asian_widths[unicodedata.east_asian_width(c)]
                     for c in text])
    except AttributeError:  # east_asian_width() New in version 2.4.
        width = len(text)
    # correction for combining chars:
    width -= len(find_combining_chars(text))
    return width

def uniq(L):
     r = []
     for item in L:
         if not item in r:
             r.append(item)
     return r

# by Li Daobing http://code.activestate.com/recipes/190465/
# since Python 2.6 there is also itertools.combinations()
def unique_combinations(items, n):
    """Return n-length tuples, in sorted order, no repeated elements"""
    if n==0: yield []
    else:
        for i in xrange(len(items)-n+1):
            for cc in unique_combinations(items[i+1:],n-1):
                yield [items[i]]+cc

def normalize_language_tag(tag):
    """Return a list of normalized combinations for a `BCP 47` language tag.

    Example:

    >>> from docutils.utils import normalize_language_tag
    >>> normalize_language_tag('de_AT-1901')
    ['de-at-1901', 'de-at', 'de-1901', 'de']
    >>> normalize_language_tag('de-CH-x_altquot')
    ['de-ch-x-altquot', 'de-ch', 'de-x-altquot', 'de']

    """
    # normalize:
    tag = tag.lower().replace('-','_')
    # split (except singletons, which mark the following tag as non-standard):
    tag = re.sub(r'_([a-zA-Z0-9])_', r'_\1-', tag)
    subtags = [subtag for subtag in tag.split('_')]
    base_tag = [subtags.pop(0)]
    # find all combinations of subtags
    taglist = []
    for n in range(len(subtags), 0, -1):
        for tags in unique_combinations(subtags, n):
            taglist.append('-'.join(base_tag+tags))
    taglist += base_tag
    return taglist


class DependencyList(object):

    """
    List of dependencies, with file recording support.

    Note that the output file is not automatically closed.  You have
    to explicitly call the close() method.
    """

    def __init__(self, output_file=None, dependencies=[]):
        """
        Initialize the dependency list, automatically setting the
        output file to `output_file` (see `set_output()`) and adding
        all supplied dependencies.
        """
        self.set_output(output_file)
        for i in dependencies:
            self.add(i)

    def set_output(self, output_file):
        """
        Set the output file and clear the list of already added
        dependencies.

        `output_file` must be a string.  The specified file is
        immediately overwritten.

        If output_file is '-', the output will be written to stdout.
        If it is None, no file output is done when calling add().
        """
        self.list = []
        if output_file:
            if output_file == '-':
                of = None
            else:
                of = output_file
            self.file = docutils.io.FileOutput(destination_path=of,
                                   encoding='utf8', autoclose=False)
        else:
            self.file = None

    def add(self, *filenames):
        """
        If the dependency `filename` has not already been added,
        append it to self.list and print it to self.file if self.file
        is not None.
        """
        for filename in filenames:
            if not filename in self.list:
                self.list.append(filename)
                if self.file is not None:
                    self.file.write(filename+'\n')

    def close(self):
        """
        Close the output file.
        """
        self.file.close()
        self.file = None

    def __repr__(self):
        try:
            output_file = self.file.name
        except AttributeError:
            output_file = None
        return '%s(%r, %s)' % (self.__class__.__name__, output_file, self.list)
