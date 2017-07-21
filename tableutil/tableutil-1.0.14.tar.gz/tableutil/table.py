# -*- coding: utf-8 -*-

import codecs
import inspect
import os
import pprint
import webbrowser
from collections import OrderedDict

import logging_helper
from conversionutil.convert import (CONVERTER,
                                    convert,
                                    convert_to_full_width_characters)
import table_html

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'

logging = logging_helper.setup_logging()


def log_debug_if__main__(message):
    if __name__ == u"__main__":
        logging.debug(message)


HEADING = u'heading'
JUSTIFY = u'justify'
MAX = u'max'

KEY = u'key'
VALUE = u'value'
CONVERT = u'convert'
PROPERTY = u'property'

LEFT_JUSTIFY   = u'<'
CENTRE_JUSTIFY = u'^'
CENTER_JUSTIFY = u'^'
RIGHT_JUSTIFY  = u'>'

DUMMY          = u'dummy'
DUMMY_HEADINGS = [{HEADING: DUMMY, JUSTIFY: LEFT_JUSTIFY}]

KEY_VALUE_HEADINGS = [{HEADING: KEY, JUSTIFY: LEFT_JUSTIFY},
                      {HEADING: VALUE, JUSTIFY: LEFT_JUSTIFY}]

SPACE           = u' SPACE'
TOP_LEFT        = u'┌ TOP_LEFT'
TOP_RIGHT       = u'┐ TOP_RIGHT '
BOTTOM_LEFT     = u'└ BOTTOM_LEFT'
BOTTOM_RIGHT    = u'┘ BOTTOM_RIGHT'
HORIZONTAL      = u'─ HORIZONTAL'
VERTICAL        = u'│ VERTICAL'
INTERSECTION    = u'┼ INTERSECTION'
HORIZONTAL_DOWN = u'┬ HORIZONTAL_DOWN'
HORIZONTAL_UP   = u'┴ HORIZONTAL_UP'
VERTICAL_RIGHT  = u'├ VERTICAL_RIGHT'
VERTICAL_LEFT   = u'┤ VERTICAL_LEFT'


def table_format_string_to_table_format_dictionary(table_format_string):
    table_format_chars = [char for char in table_format_string.replace(u'\n', u'')]
    table_format_dictionary = {}
    for name in (BOTTOM_RIGHT,
                 HORIZONTAL_UP,
                 HORIZONTAL,
                 BOTTOM_LEFT,

                 VERTICAL_LEFT,
                 INTERSECTION,
                 HORIZONTAL,
                 VERTICAL_RIGHT,

                 VERTICAL,
                 VERTICAL,
                 SPACE,
                 VERTICAL,

                 TOP_RIGHT,
                 HORIZONTAL_DOWN,
                 HORIZONTAL,
                 TOP_LEFT):
        try:
            table_char = table_format_chars.pop()
        except IndexError:
            raise ValueError(u'Bad Table Format String. Expected format:\n'
                             u'16 chars (newlines can be added) :\n'
                             u'    1:Top Left\n'
                             u'    2:Horizontal\n'
                             u'    3:Horizontal with Downstroke\n'
                             u'    4:Top Right\n'
                             u'    5:Vertical\n'
                             u'    6:Space\n'
                             u'    7:Vertical\n'
                             u'    8:Vertical\n'
                             u'    9:Vertical with Right stroke\n'
                             u'   10:Horizontal\n'
                             u'   11:Intersection\n'
                             u'   12:Vertical with Left stroke\n'
                             u'   13:Bottom Left\n'
                             u'   14:Horizontal\n'
                             u'   15:Horizontal with Up stroke\n'
                             u'   16:Bottom Right\n'
                             u"E.g.:"
                             u"┌─┬┐\\n\n"
                             u"│ ││\\n\n"
                             u"├─┼┤\\n\n"
                             u"└─┴┘\\n\n\n"
                             )
        table_format_dictionary[name] = table_char
    return table_format_dictionary


def is_dictionary(thing):
    return isinstance(thing, dict) or isinstance(thing, OrderedDict)


def is_list(thing):
    return isinstance(thing, list)


def is_list_or_dictionary(thing):
    return is_list(thing) or is_dictionary(thing)


def is_list_of_dictionaries(thing):
    return len([True for element in thing if is_dictionary(element)]) == len(thing) and len(thing) != 0


# TODO: Make real tests for these.
assert is_list_of_dictionaries([{}, {}, {}])
assert not is_list_of_dictionaries([{}, {}, {}, 1])
assert not is_list_of_dictionaries([])


def make_index_headings(width,
                        justification = CENTRE_JUSTIFY):
    return [{HEADING: column, JUSTIFY:justification}
            for column in range(width)]


def make_multi_line_list(line,
                         maximum_width = 50):
    """
    Takes a string makes it many lines with a maximum
    maximum_width while with the split points at word
    boundaries (doesn't split words in the middle unless
    the word is over the maximum width).

    :param line:
    :param maximum_width:
    :return:
    """

    def limit_word_lengths(words,
                           maximum_width):

        def limit_word_length(word,
                              maximum_width):
            word_parts = []
            while len(word) > maximum_width:
                word_parts.append(word[0:maximum_width - 1] + u'-')
                word = word[(maximum_width - 1):]
            word_parts.append(word)
            return word_parts

        limited_words = []
        [limited_words.extend(limit_word_length(word = word,
                                                maximum_width = maximum_width)) for word in words]

        return limited_words

    multi_line = []
    lines = line.split(u'\n')
    if len(lines) > 1:
        # Need to call multiple times, respecting \n
        for line in lines:
            multi_line.extend(make_multi_line_list(line = line,
                                                   maximum_width = maximum_width))
    else:
        words = limit_word_lengths(words = line.split(u' '),
                                   maximum_width = maximum_width)
        line = []
        while words:
            line.append(words.pop(0))
            if sum([len(word) for word in line]) + len(line) > maximum_width:
                new_line = u' '.join(line[:-1])
                multi_line.append(new_line)
                line = [line[-1]]
        multi_line.append(u' '.join(line))
    return multi_line


def make_multi_line(line,
                    maximum_width = 50):
    return u'\n'.join(make_multi_line_list(line,
                                           maximum_width = maximum_width))


def make_multi_line_conversion(maximum_width = 50):
    return {u'converter':     make_multi_line_list,
            u'maximum_width': maximum_width}


def escape_jira_markup(text):
    return u''.join([u'\\' + c if c in u'*_?-+^~{}#' else c for c in unicode(text)])


def add_href_to_tags(href,
                     tags):
    if href:
        href = {u'href': href}

        if isinstance(tags, dict):
            tags = [tags]

        if tags:
            for tag in tags:
                if u'a' in tag:
                    tags[u'a'].update(href)
                    return tags
            tags.append({u'a': href})
        else:
            tags = {u'a': href}
    return tags


class Cell(object):
    def __init__(self,
                 value = u'',
                 tags = None,
                 href = None,
                 tooltip = None,
                 conversion = None):
        """
        A Cell is a container that is used by Row and Table in order to
        correctly format a value for display as text, for JIRA, as HTML.

        The source value can be modified with a supplied conversion.

        :param value: Contents of the cell. Can be a string,
                      a list, a Cell or a Table.
        :param tags: tags used to format the output
                    e.g.  {u'img':{u'src':u'an_image.jpg'}}
        :param href: can be used instead of tags if only the href is needed
                     or to easily add an href to tags
        :param tooltip: Use instead of title attribute of an anchor.
                        This should have all the HTML required for the
                        toolip. If it's added inside an anchor, you
                        can set the class of the anchor (e.g. class="tooltip")
                        inside the tags parameter.
        :param conversion: Conversion to apply to the value
        """

        if isinstance(value, Cell):
            if tags is None:
                tags = value.tags
            if conversion is None:
                conversion = value.conversion
            value = value.raw_value
        else:
            tags = add_href_to_tags(tags = tags,
                                    href = href)

        if callable(conversion):
            conversion = {CONVERTER: conversion}

        self.__value = value
        self.tags = tags
        self.conversion = conversion
        self.tooltip = tooltip

    @property
    def value(self):
        try:
            converted_value = (self.__value
                               if not self.conversion
                               else convert(value = self.__value,
                                            **self.conversion))
        except Exception as e:
            logging.warning(unicode(e))
            converted_value = self.__value
        return self._split_cell(converted_value)

    @property
    def raw_value(self):
        return self.__value

    @value.setter
    def value(self,
              value):
        self.__value = value

    def width(self):
        if self.__value.__class__ == Table:
            return max([len(part)
                        for part in self._split_cell(unicode(self.__value))])
        else:
            return max([len(part) for part in self.value])

    def jira_width(self):
        return max([len(part) for part in self.jira()])

    def __eq__(self, other):
        if other.__class__ == Cell:
            return self.value == other.value and self.tags == other.tags
        return self.value == other

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        try:
            return self.value[item]
        except IndexError:
            return u''

    @staticmethod
    def _split_cell(value,
                    level = 1):
        """
        Takes cell and returns a list of strings.
        The cell source is strings or nested lists,
        A list of substrings is returned.

        e.g. cell is ['first\nsecond',['third','fourth',['fifth','sixth']]]

        is returned as ['first',
                        'second',
                        'third',
                        'fourth',
                        'fifth',
                        'sixth']

        :param value: a string or a list of strings
        :return: a list of strings
        """
        # print('> ',value.__class__, value)

        # the replace('\r','') below is because printing strings the have \r
        # can result in some odd behaviour that messes up tables:
        # >>> print 'abc\r123'
        # 123

        if value.__class__ == Table:
            return value
        if is_list_or_dictionary(value):

            value = u'\n'.join([u'\n'.join(Cell._split_cell(part, level + 1))
                                for part in value])

        else:
            value = unicode(value).replace(u'\r', u'')
        return [part for part in value.split(u'\n')]

    def get_hrefs(self,
                  tags = None):
        """
        :param tags: None if called externally
        :return: list of values for 'href' keys
        """
        if tags is None:
            tags = self.tags

        hrefs = []
        if isinstance(tags, list):
            hrefs = []
            [hrefs.extend(self.get_hrefs(sub_list)) for sub_list in tags]
            if hrefs:
                return hrefs

        elif isinstance(tags, dict):
            hrefs = []
            for tag in tags:
                if tag.lower() == u'href':
                    hrefs.append(tags[tag])
                else:
                    try:
                        hrefs.extend(self.get_hrefs(tags = (tags[tag]
                                                            if tags[tag] is not None
                                                            else u'')))
                    except TypeError:
                        pass
        try:
            return hrefs
        except IndexError:
            return None

    def get_href(self):
        """
        :return: First href in tags or explicit href value if there are none
        """
        try:
            return self.get_hrefs()[0]
        except IndexError:
            return None

    def html(self,
             target = None):
        """
        Formats the value as an HTML element by wrapping in tags
        :param target: Used only with deprecated href in Cell init
                       Adds target to anchor <A> to open in new tab/window etc
                       Use target attribute of anchor instead.
        :return:
        """

        def has_single_tag(tag):
            if len(tag) > 1:
                raise ValueError(
                    u'Multiple tags must be in a list, not a dictionary.\n'
                    u'tag:{tag}'.format(tag=tag))

            return len(tag) == 1

        def wrap_with_tag_or_inline_html(html,
                                         tag_or_inline_html_to_add):

            if not has_single_tag(tag_or_inline_html_to_add):
                return html

            if isinstance(tag_or_inline_html_to_add, basestring):
                return html + tag_or_inline_html_to_add  # This is inlin

            tag_name = tag_or_inline_html_to_add.keys()[0]

            attributes = [u'{key}="{value}"'.format(key = key, value = value)
                          for key, value in tag_or_inline_html_to_add[tag_name].iteritems()]

            if attributes:
                attributes = u' ' + u' '.join(attributes)

            return u'<{opening}{attributes}{self_closing}>{html}{closing}' \
                .format(html = html,
                        opening = tag_name,
                        closing = u'' if html == u''
                        else u'</{tag}>'.format(tag = tag_name),
                        attributes = attributes,
                        self_closing = u'/' if html == u'' else u''
                        )

        if target is None:
            target = u"_self"
        if self.__value.__class__ == Table:
            value = self.__value.html()
        else:
            value = u'<br>'.join(self.value)

        if self.tags:
            html = value
            if self.tooltip:
                html += self.tooltip  # Need to write tooltip HTML separately

            if isinstance(self.tags, list):
                for tag in self.tags:
                    html = wrap_with_tag_or_inline_html(html = html,
                                                        tag_or_inline_html_to_add= tag)

            elif isinstance(self.tags, dict):
                if self.tooltip:
                    add_tooltip_class(tag=self.tags)

                html = wrap_with_tag_or_inline_html(html = html,
                                                    tag_or_inline_html_to_add= self.tags)
            return html
        else:
            return value

    def csv(self,
            delimiter = u','):

        field = u' '.join(self.value)

        if delimiter in field:
            field = u'"{field}"'.format(field = field.replace(u'"', u'""'))

        return field

    @staticmethod
    def __jira_excluded_href(href):
        exclusions = (u'file://',)
        if href:
            if u'://' in href:
                for exclusion in exclusions:
                    if href.startswith(exclusion):
                        return True
                return False
        return True

    def jira(self):

        if self.__value.__class__ == Table:
            value = (u'{{panel:borderStyle=none}}{subtable}{{panel}}'
                     .format(subtable=unicode(self.__value.jira_table_notation())))
        else:
            value = u'\n'.join(self.value)

        # add href if it exists and it's not a file reference
        href = self.get_href()
        if not self.__jira_excluded_href(href):
            value = u'\n'.join([u'[{line}|{href}]'
                                .format(line = escape_jira_markup(line),
                                        href = href)
                                for line in value.splitlines()])
        return value


class Row(object):
    def __init__(self,
                 keys,
                 row,
                 conversions = None):

        log_debug_if__main__(inspect.currentframe().f_code.co_name)
        log_debug_if__main__(row)

        conversions = conversions if conversions else {}
        complex_conversions = [key for key in conversions if is_list_or_dictionary(key)]
        self.keys = keys
        if not is_dictionary(row):
            # assume row is iterable.
            # assume it's the whole row in order
            # make a dictionary
            assert len(row) == len(self.keys)
            row = {key: Cell(value = cell,
                             conversion = conversions.get(key))
                   for key, cell in zip(self.keys, row)}
        else:
            # Got here, so we assume it's a dictionary
            row = {key: Cell(value = value,
                             conversion = conversions.get(key))
                   for key, value in row.iteritems()}

        for complex_conversion in complex_conversions:
            if len([True for key in complex_conversion if key in row]) == len(complex_conversion):
                values = list(
                        conversions[complex_conversion][u'converter'](
                                *[row[key].raw_value
                                  for key in complex_conversion]))

                for key in complex_conversion:
                    row[key].value = values.pop(0)

        new_row = {key: Cell(u'') for key in self.keys}

        new_row.update(row)
        # new_row = {key:'\n'.join(new_row[key]) for key in new_row}
        self.row = new_row

    def __getitem__(self,
                    item):
        return self.row[item]

    def __setitem__(self,
                    key,
                    value):
        # Todo: Figure out how to add conversion.
        #       Conversions probably need to be
        #       configured per column at table level.
        #       Currently if a value is changed,
        #       the conversion is lost. Could pass
        #       parent table in instead of keys
        self.row[key] = Cell(value)


class Table(object):
    LIGHT_TABLE_FORMAT = \
        table_format_string_to_table_format_dictionary(
                u"┌─┬┐"
                u"│ ││"
                u"├─┼┤"
                u"└─┴┘")

    ROUNDED_TABLE_FORMAT = \
        table_format_string_to_table_format_dictionary(
                u"╭─┬╮"
                u"│ ││"
                u"├─┼┤"
                u"╰─┴╯")

    DOUBLE_TABLE_FORMAT = \
        table_format_string_to_table_format_dictionary(
                u"╔═╦╗"
                u"║ ║║"
                u"╠═╬╣"
                u"╚═╩╝")

    TEXT_TABLE_FORMAT = \
        table_format_string_to_table_format_dictionary(
                u" -- "
                u"| ||"
                u"|-+|"
                u" -- ")

    TSV_TABLE_FORMAT = \
        table_format_string_to_table_format_dictionary(
                u"  \t "
                u"  \t "
                u"  \t "
                u"  \t ")

    CSV_TABLE_FORMAT = \
        table_format_string_to_table_format_dictionary(
                u"  , "
                u"  , "
                u"  , "
                u"  , ")

    def __init__(self,
                 headings,
                 rows = None,
                 title = None,
                 row_numbers = True,
                 conversions = None,
                 table_format = None,
                 show_separators = False,
                 show_summaries = False,
                 show_column_headings = True,
                 empty_table_indication = u'Empty'):
        """
        TODO: Flesh this out

        :param headings: list of dicts:
                         dict: {HEADING: text or Cell,
                                MAX:     maximum width for the column
                                JUSTIFY: one of LEFT_JUSTIFY (default)
                                                CENTRE_JUSTIFY
                                                CENTER_JUSTIFY
                                                RIGHT_JUSTIFY
        :param rows:
        :param title: text or Cell: Title of table. Spans all columns
        :param row_numbers: bool: Show or hide row numbers. Defauls
        :param conversions:
        :param table_format: string: Defines the characters used for text
                                     formatting. See examples above.
        :param show_separators: bool
        :param show_summaries: bool
        :param show_column_headings: bool
        :param empty_table_indication: text or Cell to show if there are no
                                       rows
        """

        self.conversions = {} if conversions is None else conversions
        log_debug_if__main__(u'Headings')
        log_debug_if__main__(headings)
        self.keys = [heading[HEADING] for heading in headings]
        log_debug_if__main__(u'Keys')
        log_debug_if__main__(self.keys)
        self.headings = OrderedDict()
        for key in self.keys:
            self.headings[key] = Cell(key)
        if title is not None:
            self.title = title
        else:
            self._title = None
        self.justifications = [heading.get(JUSTIFY, LEFT_JUSTIFY)
                               for heading in headings]
        self.max_widths = [heading.get(MAX, None) for heading in headings]
        self.row_numbers = row_numbers
        self.suppress_empty_table_indication = empty_table_indication is None
        self.empty_table_indication = Cell(empty_table_indication)
        self.show_column_headings = show_column_headings
        self.show_separators = show_separators
        self.summaries = {key: Cell(u'') for key in self.keys} if show_summaries else None
        self.rows = []
        self.set_table_format(table_format)
        if rows:
            self.add_rows(rows)

    @property
    def title(self):
        return self._title.raw_value

    @title.setter
    def title(self,
              title):
        self._title = Cell(title)

    def update_empty_table_indication(self,
                                      empty_table_indication):
        self.empty_table_indication = Cell(empty_table_indication)

    def add_row(self,
                row):
        self.rows.append(Row(keys = self.keys,
                             row = row,
                             conversions = self.conversions))

    def add_rows(self,
                 rows):
        for row in rows:
            self.add_row(row)

    def add_summary(self,
                    heading,
                    value):
        self.add_summaries({heading: value})

    def add_summaries(self,
                      summaries):
        summaries = {key: Cell(value)
                     for key, value in summaries.iteritems()}
        self.summaries.update(summaries)

    def sort_by_column(self,
                       column,
                       ascending = True):
        self.rows = sorted(self.rows,
                           key = lambda k: k[column].value,
                           reverse = not ascending)

    def __len__(self):
        return len(unicode(self).split(u'\n'))

    def __getitem__(self, item):
        try:
            return unicode(self).split(u'\n')[item]
        except IndexError:
            return u''

    def set_table_format(self,
                         table_format=None):
        if table_format is None:
            table_format = Table.LIGHT_TABLE_FORMAT
        elif not is_dictionary(table_format):
            table_format = table_format_string_to_table_format_dictionary(table_format)
        self.table_format = table_format
        # TODO: Propagate to sub-tables.

    def as_text(self,
                show_title=True,
                table_format=None,
                solid_borders=True,
                sort_column=None,
                sort_ascending=True):

        if table_format is not None:
            self.set_table_format(table_format)
        del table_format

        def _cell_widths():
            if self.rows:
                widths = {key: max([row[key].width() for row in self.rows]) for key in self.keys}
                if self.summaries:
                    widths = {key: self.summaries[key].width()
                              if self.summaries[key].width() > widths[key]
                              else widths[key]
                              for key in self.keys}
                widths = [self.headings[key].width()
                          if self.headings[key].width() > widths[key]
                          else widths[key]
                          for key in self.keys]
            else:
                widths = [self.headings[key].width()
                          for key in self.keys]
            if self.row_numbers:
                widths.insert(0, len(str(len(self.rows))))
            return widths

        def _formatted_cell(width,
                            string,
                            justification,
                            sep=None):
            if sep is None:
                sep = u'{space}{vertical}{space}' \
                    .format(space = self.table_format[SPACE],
                            vertical = self.table_format[VERTICAL])

            justified_string = u'{string:{fill}{justification}{width}}' \
                .format(string = string,
                        fill = self.table_format[SPACE],
                        width = width,
                        justification = justification)

            return u'{sep}{justified_string}' \
                .format(justified_string = justified_string,
                        sep = sep)

        def _formatted_row(widths,
                           strings,
                           justifications = None,
                           sep = u'{space}{v}{space}'
                           .format(space = self.table_format[SPACE],
                                   v = self.table_format[VERTICAL])):

            widths = [width for width in widths]

            justifications = [LEFT_JUSTIFY for _ in xrange(len(widths))] \
                if justifications is None else justifications

            row_parts = [_formatted_cell(string = strings[0],
                                         width = widths[0],
                                         sep = u'',
                                         justification = justifications[0])]

            for (string,
                 width,
                 justification) in zip(strings[1:],
                                       widths[1:],
                                       justifications[1:]):
                row_parts.append(_formatted_cell(string = string,
                                                 width = width,
                                                 justification = justification,
                                                 sep = sep))
            return u''.join(row_parts)

        def _formatted_rows(widths,
                            cells,
                            sep = None,
                            left_edge = None,
                            right_edge = None,
                            justifications = None,
                            extra = u''):

            number_of_sub_rows = max([len(cell) for cell in cells])

            if sep is None:
                sep = u'{space}{v}{space}' \
                    .format(space = self.table_format[SPACE],
                            v = self.table_format[VERTICAL])

            if left_edge is None:
                left_edge = u'{v}{space}' \
                    .format(space = self.table_format[SPACE],
                            v = self.table_format[VERTICAL])

            if right_edge is None:
                right_edge = u'{space}{v}' \
                    .format(space = self.table_format[SPACE],
                            v = self.table_format[VERTICAL])

            row_parts = []
            for sub_row in xrange(number_of_sub_rows):
                strings = [cell[sub_row] for cell in cells]
                row_parts.append(
                    u'{left_edge}{sub_row}{extra}{right_edge}'
                    .format(left_edge = left_edge,
                            right_edge = right_edge,
                            sub_row = _formatted_row(
                                          widths = widths,
                                          strings = strings,
                                          sep = sep,
                                          justifications = justifications),
                            extra = extra))
            return row_parts

        # as_text body

        if sort_column is not None:
            self.sort_by_column(column = sort_column,
                                ascending = sort_ascending)

        left_edge_at_data = u' ' if not solid_borders \
            else u'{v}{space}'.format(v = self.table_format[VERTICAL],
                                      space = self.table_format[SPACE])

        right_edge_at_data = u' ' if not solid_borders \
            else u'{space}{v}'.format(v = self.table_format[VERTICAL],
                                      space = self.table_format[SPACE])

        left_edge_at_line = u' ' if not solid_borders \
            else u'{v}{h}'.format(v = self.table_format[VERTICAL_RIGHT],
                                  h = self.table_format[HORIZONTAL])

        right_edge_at_line = u' ' if not solid_borders \
            else u'{h}{v}'.format(v = self.table_format[VERTICAL_LEFT],
                                  h = self.table_format[HORIZONTAL])

        if not self.rows and len(self.headings) > 1:
            table_lines = Table(title = self._title,
                                headings = [{u'heading': u'dummy'}],
                                show_column_headings = False,
                                empty_table_indication = self.empty_table_indication,
                                table_format = self.table_format)

            return unicode(table_lines)

        if self.row_numbers:
            if self.justifications:
                justifications = [RIGHT_JUSTIFY] + \
                                 [j for j in self.justifications]
            else:
                justifications = [RIGHT_JUSTIFY] + \
                                 [LEFT_JUSTIFY
                                  for _ in xrange(len(self.headings))]
        else:
            justifications = self.justifications

        widths = _cell_widths()

        line = _formatted_row(widths = widths,
                              strings = [self.table_format[HORIZONTAL] * width for width in widths],
                              sep = self.table_format[HORIZONTAL] * 3)

        sep = u'{h}{hd}{h}'.format(h = self.table_format[HORIZONTAL],
                                   hd = self.table_format[HORIZONTAL_DOWN]
                                   if self.rows
                                   else self.table_format[HORIZONTAL])

        top_line = _formatted_row(widths = widths,
                                  strings = [self.table_format[HORIZONTAL] * width
                                             for width in widths],
                                  sep = sep)

        sep = u'{h}{hu}{h}'.format(h = self.table_format[HORIZONTAL],
                                   hu = self.table_format[HORIZONTAL_UP]
                                   if self.rows
                                   else self.table_format[HORIZONTAL])

        bottom_line = _formatted_row(widths = widths,
                                     strings = [self.table_format[HORIZONTAL] * width
                                                for width in widths],
                                     sep = sep)

        extra = u''
        if not self.rows and len(line) < self.empty_table_indication.width():
            extra = self.table_format[HORIZONTAL] \
                    * (self.empty_table_indication.width() - len(line))  # -------
            line += extra

        if self._title and show_title:
            length_of_longest_title_line = self._title.width() \
                if self._title else 0

            if len(line) < length_of_longest_title_line:
                extra = \
                    self.table_format[HORIZONTAL] * \
                    (length_of_longest_title_line - len(line))  # --------
                line += extra
                top_line += extra
                bottom_line += extra

        sep = (self.table_format[HORIZONTAL] +     # -+-
               self.table_format[INTERSECTION] +
               self.table_format[HORIZONTAL])

        separator = \
            _formatted_row(widths = widths,
                           strings = [self.table_format[HORIZONTAL] * width
                                      for width in widths],
                           sep = sep) \
            + extra

        table_lines = []

        if solid_borders:
            table_lines.append(
                u'{tl}{h}{line}{h}{tr}'
                .format(tl = self.table_format[TOP_LEFT],
                        h = self.table_format[HORIZONTAL],
                        line = line if self._title and show_title else top_line,
                        tr = self.table_format[TOP_RIGHT]))

        if self._title and show_title:
            for title_line in self._title.value:
                table_lines.append(
                    u'{le}{title_line:^{width}}{re}'
                    .format(le = left_edge_at_data,
                            re = right_edge_at_data,
                            title_line = title_line,
                            width = len(line)))

            table_lines.append(left_edge_at_line +
                               (top_line if self.rows else line) +
                               right_edge_at_line)

        if self.rows:
            if self.show_column_headings:
                headers = [self.headings[key] for key in self.keys]
                headers = [Cell(u'#')] + headers \
                    if self.row_numbers else headers

                header = _formatted_rows(
                        widths = widths,
                        cells = headers,
                        justifications = [CENTRE_JUSTIFY
                                          for _ in xrange(len(justifications))],
                        left_edge = left_edge_at_data,
                        right_edge = right_edge_at_data,
                        extra = self.table_format[SPACE] * len(extra))
                table_lines.extend(header)
                table_lines.append(u'{le}{separator}{re}'
                                   .format(le = left_edge_at_line,
                                           re = right_edge_at_line,
                                           separator = separator))

            for row_number, row in enumerate(self.rows):
                cells = [Cell(str(row_number + 1))] if self.row_numbers else []
                cells.extend([row[key] for key in self.keys])

                table_lines.extend(
                        _formatted_rows(
                                widths = widths,
                                cells = cells,
                                justifications = justifications,
                                left_edge = left_edge_at_data,
                                right_edge = right_edge_at_data,
                                extra = self.table_format[SPACE] * len(extra)))

                if self.show_separators and row != self.rows[-1]:
                    table_lines.append(u'{le}{separator}{re}'
                                       .format(le = left_edge_at_line,
                                               re = right_edge_at_line,
                                               separator = separator))

            if self.summaries:
                summaries = [Cell(u'')] if self.row_numbers else []
                summaries.extend([self.summaries[key] for key in self.keys])

                table_lines.append(u'{le}{separator}{re}'
                                   .format(le = left_edge_at_line,
                                           re = right_edge_at_line,
                                           header = header,
                                           separator = separator))

                table_lines.extend(
                    _formatted_rows(
                         widths = widths,
                         cells = summaries,
                         justifications = justifications,
                         left_edge = left_edge_at_data,
                         right_edge = right_edge_at_data,
                         extra = self.table_format[SPACE] * len(extra)))

        else:
            if not self.suppress_empty_table_indication:
                table_lines.extend(
                        _formatted_rows(
                                widths = [len(line)],
                                cells = [self.empty_table_indication],
                                left_edge = left_edge_at_data,
                                right_edge = right_edge_at_data))

        if solid_borders and not self.suppress_empty_table_indication:
            if self.rows:
                table_lines.append(
                    u'{bl}{h}{line}{h}{br}'
                    .format(bl = self.table_format[BOTTOM_LEFT],
                            h = self.table_format[HORIZONTAL],
                            line = bottom_line,
                            br = self.table_format[BOTTOM_RIGHT]))
            else:
                # TODO: Need to tidy this up and
                # test for empty indication wider than title
                table_lines.append(
                    u'{bl}{h}{line}{h}{br}'
                    .format(bl = self.table_format[BOTTOM_LEFT],
                            h = self.table_format[HORIZONTAL],
                            line = line if self._title and show_title else bottom_line,
                            br = self.table_format[BOTTOM_RIGHT]))

        return u'\n'.join(table_lines)

    def __unicode__(self):
        return self.as_text()

    def fixed_width(self):
        return convert_to_full_width_characters(self.as_text())

    def jira_table_notation(self,
                            sort_column = None,
                            sort_ascending = True):

        if sort_column is not None:
            self.sort_by_column(column = sort_column,
                                ascending = sort_ascending)

        # TODO: Add styles
        # pdb.set_trace()
        table_lines = []

        if not self.rows:
            number_of_columns = 1
        else:
            number_of_columns = len(self.headings) + (1 if self.row_numbers else 0)

        if self._title:
            table_lines.append(u'|| {value} ||\n'
                               .format(value = self._title.jira()))

        if self.rows:
            if self.show_column_headings:
                headers = [self.headings[key] for key in self.keys]
                headers = [Cell(u' ')] + headers if self.row_numbers else headers

                table_lines.append(u'|| {headers} ||'
                                   .format(headers = u' || '.join([heading.jira()
                                                                 for heading in headers])))

        if self.rows:
            for row_number, row in enumerate(self.rows):
                cells = [Cell(unicode(row_number + 1))] if self.row_numbers else []
                cells.extend([row[key] for key in self.keys])

                table_lines.append(u'| {cells} |'
                                   .format(cells = u' | '
                                                   .join([cell.jira()
                                                          for cell in cells])))

        else:
            if not self.suppress_empty_table_indication:
                table_lines.append(u'| {eti} |'
                                   .format(eti=self.empty_table_indication.jira()))

        if self.rows and self.summaries:
            summaries = [Cell(u'')] if self.row_numbers else []
            summaries.extend([self.summaries[key] for key in self.keys])

            table_lines.append(u'| {summary} |'
                               .format(summary = u' | '
                                                 .join([summary.jira()
                                                        for summary in summaries])))
        return u'\n'.join(table_lines)

    def html(self,
             target = None,
             sort_column = None,
             sort_ascending = True):

        if sort_column is not None:
            self.sort_by_column(column = sort_column,
                                ascending = sort_ascending)

        # TODO: Add styles
        # pdb.set_trace()
        html = [u"<table cellspacing='0'>",
                u'    <thead>']

        if not self.rows:
            number_of_columns = 1
        else:
            number_of_columns = len(self.headings) + (1 if self.row_numbers else 0)

        if self._title:
            html.extend([u'        <tr>',
                         u'            <th colspan="{colspan}">{value}</th>'
                        .format(colspan = number_of_columns,
                                value = self._title.html(target = target)),
                         u'        </tr>'])

        if self.rows:
            if self.show_column_headings:
                headers = [self.headings[key] for key in self.keys]
                headers = [Cell(u'#')] + headers if self.row_numbers else headers
                html.append(u'        <tr>')
                for heading in headers:
                    html.append(u'            <th>{value}</th>'
                                .format(value = heading.html(target = target)))
                html.append(u'        </tr>')

        html.append(u'    </thead>'
                    u'    <tbody>')

        if self.rows:
            for row_number, row in enumerate(self.rows):
                cells = [Cell(unicode(row_number + 1))] if self.row_numbers else []
                cells.extend([row[key] for key in self.keys])
                html.append(u'        <tr>')
                for cell in cells:
                    html.append(u'            <td>{value}</td>'
                                .format(value = cell.html(target = target)))
                html.append(u'        </tr>')
        else:
            if not self.suppress_empty_table_indication:
                html.extend([u'        <tr>',
                             u'            <td colspan="{colspan}">{value}</th>'
                            .format(colspan = number_of_columns,
                                    value = self.empty_table_indication.html()),
                             u'        </tr>'])

        html.append(u'    </tbody>')

        if self.rows and self.summaries:
            html.append(u'    <tfoot>'
                        u'        <tr>')
            summaries = [Cell(u'')] if self.row_numbers else []
            summaries.extend([self.summaries[key] for key in self.keys])
            for summary in summaries:
                html.append(u'            <td>{value}</td>'
                            .format(value = summary.html(target = target)))
            html.append(u'        </tr>'
                        u'    </tfoot>')

        html.append(u'</table>')

        return u'\n'.join(html)

    def csv(self,
            sort_column = None,
            sort_ascending = True,
            delimiter = u','):

        if sort_column is not None:
            self.sort_by_column(column = sort_column,
                                ascending = sort_ascending)

        csv = []

        if self.show_column_headings or True:
            csv.extend([delimiter.join([self.headings[key].csv(delimiter = delimiter) for key in self.keys]),
                        u'\n'])

        for row in self.rows:
            cells = [row[key].csv(delimiter = delimiter) for key in self.keys]
            csv.append(delimiter.join(cells) + u'\n')

        return u''.join(csv)

    @staticmethod
    def init_from_tree__root_dictionary(tree,
                                        title,
                                        level,
                                        conversions,
                                        table_format):

        log_debug_if__main__(inspect.currentframe().f_code.co_name)
        log_debug_if__main__(tree)

        table = Table(title = title,
                      headings = KEY_VALUE_HEADINGS,
                      row_numbers = False,
                      conversions = conversions,
                      table_format = table_format,
                      show_column_headings = False)

        # Currently do complex conversionutil here, but may may more sense to do it
        # a row level.
        complex_conversions = [key for key in conversions if is_list_or_dictionary(key)]
        for complex_conversion in complex_conversions:
            if len([True for key in complex_conversion if key in tree]) == len(complex_conversion):
                values = list(conversions[complex_conversion][u'converter'](*[tree[key] for key in complex_conversion]))
                for key in complex_conversion:
                    tree[key] = values.pop(0)

        for field in tree:
            table.add_row({KEY:   field,
                           VALUE: Table.init_from_tree(tree = tree[field],
                                                       level = level + 1,
                                                       field_name = field,
                                                       conversions = conversions,
                                                       table_format = table_format)})
        return table

    @staticmethod
    def init_from_tree__dictionary(tree,
                                   level,
                                   conversions,
                                   table_format):
        headings = {}

        for field in tree:
            headings[field] = None

        log_debug_if__main__(inspect.currentframe().f_code.co_name)
        log_debug_if__main__(tree)

        table = Table(headings = [{u'heading': heading}
                                  for heading in headings],
                      row_numbers = False,
                      conversions = conversions,
                      table_format = table_format)

        complex_conversions = [key
                               for key in conversions
                               if is_list_or_dictionary(key)]

        for complex_conversion in complex_conversions:
            # TODO: Add an explanation of this!
            if len([True
                    for key in complex_conversion
                    if key in tree]) == len(complex_conversion):
                values = \
                    list(
                            conversions[complex_conversion]
                            [u'converter'](*[tree[key]
                                            for key in complex_conversion]))

                for key in complex_conversion:
                    tree[key] = values.pop(0)

        row = {}
        for field in tree:
            row[field] = Table.init_from_tree(tree = tree[field],
                                              level = level + 1,
                                              conversions = conversions,
                                              table_format = table_format)
        table.add_row(row)

        return table

    @staticmethod
    def init_from_tree__dictionaries(tree,
                                     level,
                                     conversions,
                                     table_format,
                                     title = None,
                                     row_numbers = True):
        log_debug_if__main__(inspect.currentframe().f_code.co_name)
        log_debug_if__main__(tree)
        # If these are highly amorphous dictionaries, it's going to get interesting!
        # Get ALL the keys!
        headings = OrderedDict()
        for record in tree:
            for field in record:
                headings[field] = None

        table = Table(title = title,
                      headings = [{u'heading': heading}
                                  for heading in headings],
                      row_numbers = row_numbers,
                      conversions = conversions,
                      table_format = table_format)

        for record in tree:
            row = {}
            for field in headings:
                row[field] = u'-'
            for field_name in record:
                log_debug_if__main__(u'{field}, {type}, {record}'
                                     .format(field = field_name,
                                             type = record[field_name].__class__,
                                             record = record[field_name]))

                row[field_name] = Table.init_from_tree(tree = record[field_name],
                                                       level = level + 1,
                                                       field_name = field_name,
                                                       conversions = conversions,
                                                       table_format = table_format)

                log_debug_if__main__(u'back in init_from_tree__dictionaries')
            table.add_row(row)

        return table

    @staticmethod
    def init_from_tree__list(tree,
                             level,
                             conversions,
                             table_format,
                             title = None):

        log_debug_if__main__(inspect.currentframe().f_code.co_name)
        log_debug_if__main__(tree.__class__)
        log_debug_if__main__(tree)

        table = Table(title = title,
                      headings = DUMMY_HEADINGS,
                      row_numbers = False,
                      conversions = conversions,
                      table_format = table_format,
                      show_column_headings = False)

        for record in tree:
            table.add_row({DUMMY: Table.init_from_tree(tree = record,
                                                       level = level + 1,
                                                       conversions = conversions,
                                                       table_format = table_format)})

        return table

    @staticmethod
    def init_from_tree(tree,
                       title = None,
                       level = 0,
                       field_name = None,
                       conversions = None,
                       row_numbers = True,
                       table_format = None):
        """

        :rtype: object
        """
        log_debug_if__main__(inspect.currentframe().f_code.co_name)
        log_debug_if__main__(tree)

        conversions = conversions if conversions else {}

        log_debug_if__main__(u'Conversions: {conversions}'.format(conversions = conversions))

        if isinstance(tree, Cell):
            # We've reached a leaf node that has already been processed. Return it.
            return tree

        elif is_dictionary(tree):
            if level == 0:
                return Table.init_from_tree__root_dictionary(tree = tree,
                                                             title = title,
                                                             level = level,
                                                             conversions = conversions,
                                                             table_format = table_format)
            else:
                return Table.init_from_tree__dictionary(tree = tree,
                                                        level = level,
                                                        conversions = conversions,
                                                        table_format = table_format)
        elif is_list(tree):

            if is_list_of_dictionaries(tree):

                return Table.init_from_tree__dictionaries(tree = tree,
                                                          title = title if level == 0 else None,
                                                          level = level,
                                                          conversions = conversions,
                                                          row_numbers = row_numbers,
                                                          table_format = table_format)
            else:
                return Table.init_from_tree__list(tree = tree,
                                                  level = level,
                                                  title = title if level == 0 else None,
                                                  conversions = conversions,
                                                  table_format = table_format)
        else:
            # Not a cell, not a dictionary, not a list,
            # it must be a unprocessed leaf.
            log_debug_if__main__(u'leaf: {leaf}'.format(leaf = tree))
            return Cell(value = u'-' if tree is None else tree,
                        conversion = None if not conversions else conversions.get(field_name))

    def log(self,
            level = logging_helper.INFO):
        logging.log(level = level,
                    msg = u'\n' + unicode(self))

    @staticmethod
    def init_from_text(text,
                       conversions = None,
                       table_format = None):

        def is_horizontal_separator_line(line):
            h = table_format[HORIZONTAL]
            v = table_format[VERTICAL]
            i = table_format[INTERSECTION]

            just_horizontals = line.strip().replace(v, h).replace(i, h)

            return len(just_horizontals) * h == just_horizontals

        lines = [line.strip() for line in text.strip().splitlines()]

        if is_horizontal_separator_line(lines[-1]):
            lines.pop()

        if is_horizontal_separator_line(lines[0]):
            lines.pop(0)

        log_debug_if__main__(pprint.pformat(lines))
        rows = []
        while not is_horizontal_separator_line(lines[-1]):
            line = lines.pop()
            if line[0] == line[-1] == table_format[VERTICAL]:
                line = line[1:-1]
            rows.append([part.strip() for part in line.split(table_format[VERTICAL])])
        rows.reverse()

        lines.pop()

        header_lines = []

        while lines and not is_horizontal_separator_line(lines[-1]):
            line = lines.pop()
            if line[0] == line[-1] == table_format[VERTICAL]:
                line = line[1:-1]
            header_lines.append(line.split(table_format[VERTICAL]))

        lines.pop()

        headings = []
        for heading in xrange(len(header_lines[0])):
            heading_parts = u'\n'.join([header_line[heading].strip() for header_line in reversed(header_lines)])
            headings.append(heading_parts.strip())

        title_lines = []

        while lines and not is_horizontal_separator_line(lines[-1]):

            line = lines.pop()
            if line[0] == line[-1] == table_format[VERTICAL]:
                line = line[1:-1]
            title_lines.append(line.strip())
        title_lines.reverse()
        title = (u'\n'.join(title_lines)).strip()

        row_numbers = headings[0] == u'#'

        if row_numbers:
            headings.pop(0)

            for row in rows:
                row.pop(0)

        table = Table(title = title if title else None,
                      headings = [{u'heading': heading}
                                  for heading in headings],
                      row_numbers = row_numbers,
                      conversions = conversions,
                      table_format = table_format)
        for row in rows:
            table.add_row(row)

        return table

    @staticmethod
    def init_from_file(filename,
                       conversions = None):
        return Table.init_from_text(codecs.open(filename,
                                                u'r',
                                                encoding = u'utf8').read(),
                                    conversions = conversions)

    @staticmethod
    def init_from_pasted_excel(pasted_excel,
                               row_numbers = False):
        rows = [row.split() for row in pasted_excel.splitlines()]
        table = Table(headings = [{u'heading':       heading,
                                   u'justification': u'^'}
                                  for heading in rows.pop(0)],
                      row_numbers = row_numbers)
        for _ in rows:
            table.add_row(rows.pop(0))
        return table

    @staticmethod
    def init_as_grid(values,
                     title = None,
                     columns = 3,
                     max_cell_width = None,
                     unfilled = u'-',
                     justify = CENTRE_JUSTIFY):
        rows = []

        detected_lists = None
        for value in values:
            if (isinstance(value, list) or isinstance(value, tuple)):
                if detected_lists in (None, True):
                    detected_lists = True
                else:
                    raise ValueError(u'Cannot mix values and lists:{value}'
                                     .format(value = value))
                # value is a row
                if len(value) <= columns:
                   row = [unfilled for _ in range(columns)]
                   for i, cell in enumerate(value):
                       row[i] = cell
                   rows.append(row)
                else:
                    raise ValueError(u'Too many columns in row:{value}'
                                     .format(value = value))
            else:
                if detected_lists is True:
                    raise ValueError(u'Cannot mix values and lists:{value}'
                                     .format(value = value))

        if not detected_lists:

            # Just a flat list. sort into rows
            rows = []
            column = 0

            while values:
                if column == 0:
                    try:
                        rows.append(row)
                        del row
                    except NameError:
                        pass

                value = values.pop(0)
                try:
                    row
                except NameError:
                    row = {column: unfilled for column in range(columns)}
                finally:
                    row[column] = value

                column = (column + 1) % columns

            try:
                rows.append(row)
            except NameError:
                    pass

        conversions = (None if not max_cell_width
                       else {column: make_multi_line_conversion(max_cell_width)
                             for column in range(columns)})

        return Table(title = title,
                     headings = make_index_headings(
                                    width = columns,
                                    justification = justify),
                     show_column_headings = False,
                     row_numbers = False,
                     rows = rows,
                     show_separators = True,
                     conversions = conversions)


    @staticmethod
    def escaped(string):
        doc = (u'<!doctype html>\n'
               u'<html lang="en-GB">\n'
               u'    <head>\n'
               u'        <meta charset="UTF-8">\n'
               u'    </head>\n'
               u'    <body>\n'
               u'        <pre>\n'
               u'{table}\n'
               u'        <pre>\n'
               u'    </body>\n'
               u'</html>')

        return u'\\n'.join(doc.format(table = string).splitlines()). \
            replace(u"'", u"\\x27").replace(u'"', u"\\x22")

    def write_to_html(self,
                      sort_column = None,
                      sort_ascending = True,
                      filename = None,
                      html_folder = None,
                      target = None,
                      filehandle = None,
                      jira_helper = True,
                      text_helper = True,
                      open_in_browser = False, ):

        if (filename and html_folder) or filehandle:

            if not filehandle:
                f = table_html.open(
                        table_html.html_filename(html_folder = html_folder,
                                                 filename = filename))
            else:
                f = filehandle

            f.write(self.html(target = target,
                              sort_column = sort_column,
                              sort_ascending = sort_ascending))

            if text_helper or jira_helper:

                if jira_helper or text_helper:
                    f.write(u'Click for a ')
                    if jira_helper:
                        escaped_jira = self.escaped(self.jira_table_notation())
                        f.write(
                            (u"""<a href="javascript:open_document('{jira}')">"""
                             u"""JIRA table notation</A>"""
                             .format(jira = escaped_jira)))
                        if text_helper:
                            f.write(u' or ')
                    if text_helper:
                        f.write(u"""<a href="javascript:open_document('{text}')">Formatted text table</A>"""
                                .format(text = self.escaped(unicode(self))))
                    f.write(u' of the table above\n<BR>\n<BR>\n')

            if filehandle is None:
                table_html.close(f)
                if open_in_browser:

                    html_path = \
                        table_html.html_filename(
                                html_folder = html_folder,
                                filename = filename)

                    if os.name == u"posix":
                        html_path = u"file://" + html_path

                    webbrowser.open(html_path)
        else:
            raise ValueError(u'Must supply a filehandle or an html_folder and '
                             u'filename to write_to_html.')

    def write_to_textfile(self,
                          filepath):
        with codecs.open(filepath, u'w', encoding = u'utf8') as f:
            f.write(unicode(self))

    def log_and_write_to_html(self,
                              filename = None,
                              html_folder = None,
                              target = None,
                              filehandle = None,
                              jira_helper = True,
                              text_helper = True,
                              open_in_browser = False,
                              level = logging_helper.DEBUG):

        self.log(level = level)

        self.write_to_html(filename = filename,
                           html_folder = html_folder,
                           target = target,
                           filehandle = filehandle,
                           jira_helper = jira_helper,
                           text_helper = text_helper,
                           open_in_browser = open_in_browser)

    def properties_as_list_of_key_values(self,
                                         object,
                                         lookup):
        """
        Uses lookup to transform properties of a class into a dictionary

        :param lookup: This is a list of dictionaries describing each property
                       and how to transform it in the results.
                       {PROPERTY: The name of a property method in the class
                                  that this is mixed into. e.g. 'start_time'
                        KEY:      The name of the key to use in the results
                                  for this property, e.g. "Start Time"
                        CONVERT: A conversion function that can be called
                                 to convert the value to something more
                                 presentable. If parameters are required,
                                 use a dictionary conforming to convert
                                 signature in conversionutils
        :return: dictionary e.g. {"Start Time": 1497535810,
                                  "End Time": 1497535809}
        """
        key_values = {}

        for field in lookup:
            key = field[KEY]
            conversion = field.get(CONVERT)
            value = None
            try:
                exec (u"value = object.{property}".format(property=field[PROPERTY]))
            except AttributeError:
                value = u'Missing property'
            except KeyError:
                pass  # No property to fetch
            else:
                if conversion:
                    if callable(conversion):
                        value = conversion(value)
                    else:
                        try:
                            value = convert(value=value,
                                            **conversion)
                        except Exception as e:
                            value = unicode(e)
            if value is not None:
                key_values[key] = value

        return key_values

    def add_row_from_object_properties(self,
                                       object,
                                       lookup):
        self.add_row(self.properties_as_list_of_key_values(object=object,
                                                           lookup=lookup))

    def add_key_value_rows_from_object_properties(self,
                                                  object,
                                                  lookup):
        if len(self.keys) != 2:
            raise ValueError(u"Can only add rows as key value pairs to a table with two columns.")

        key_heading = self.keys[0]
        value_heading = self.keys[1]

        self.add_rows([{key_heading: key, value_heading: value}
                       for key, value in self.properties_as_list_of_key_values(object=object,
                                                                               lookup=lookup).iteritems()])


if __name__ == u'__main__':
    log_debug_if__main__(u'x')
    t = Table(title=Cell(value=u'multi\nline\ntitle',
                         href=u'http://www.apple.com'),
              headings=[{u'heading': u'x'},{u'heading': u'y'}],
              show_column_headings=True,
              row_numbers=False,
              )

    sub_table = Cell(Table.init_from_tree([Cell(value = u'fds',
                                                href = u'http://google.co.uk'),
                                           Cell(value=u'pppp',
                                                tags={u'img': {u'src': u'vlah'}})]))

    t.add_rows([{u'x': u'a', u'y': u'b'},
                {u'x': u'c', u'y': sub_table},
                ])

    print t.jira_table_notation()