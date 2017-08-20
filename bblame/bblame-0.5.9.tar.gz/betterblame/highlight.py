"""Module for syntax highlighting file content using pygments"""
# pylint: disable=no-name-in-module
import logging
import curses
import re

from operator import ior
from functools import reduce
from pygments.formatters import TerminalFormatter
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments import highlight
from pygments.util import ClassNotFound


FORMATTER = TerminalFormatter()

# ANSI style codes
# Not all codes are used currently, but keep them all here for completeness
ANSI_RESET = 0
ANSI_BOLD_ON = 1
ANSI_BOLD_OFF = 22
ANSI_ITALICS_ON = 3
ANSI_ITALICS_OFF = 23
ANSI_UNDERLINE_ON = 4
ANSI_UNDERLINE_OFF = 24
ANSI_INVERSE_ON = 7
ANSI_INVERSE_OFF = 27
ANSI_STRIKETHROUGH_ON = 9
ANSI_STRIKETHROUGH_OFF = 29
# ANSI colour codes
ANSI_COLOR_BLACK_FG = 30
ANSI_COLOR_BLACK_BG = 40
ANSI_COLOR_RED_FG = 31
ANSI_COLOR_RED_BG = 41
ANSI_COLOR_GREEN_FG = 32
ANSI_COLOR_GREEN_BG = 42
ANSI_COLOR_YELLOW_FG = 33
ANSI_COLOR_YELLOW_BG = 43
ANSI_COLOR_BLUE_FG = 34
ANSI_COLOR_BLUE_BG = 44
ANSI_COLOR_MAGENTA_FG = 35
ANSI_COLOR_MAGENTA_BG = 45
ANSI_COLOR_CYAN_FG = 36
ANSI_COLOR_CYAN_BG = 46
ANSI_COLOR_WHITE_FG = 37
ANSI_COLOR_WHITE_BG = 47
ANSI_COLOR_DEFAULT_FG = 39
ANSI_COLOR_DEFAULT_BG = 49


# ANSI --> curses attributes map
ANSI_TO_CURSES = {
    ANSI_RESET: curses.A_NORMAL,
    ANSI_BOLD_ON: curses.A_BOLD,
    ANSI_UNDERLINE_ON: curses.A_UNDERLINE,
    ANSI_COLOR_DEFAULT_FG: curses.A_NORMAL,
    ANSI_COLOR_DEFAULT_BG: curses.A_NORMAL,
    ANSI_COLOR_BLACK_FG: curses.COLOR_BLACK,
    ANSI_COLOR_RED_FG: curses.COLOR_RED,
    ANSI_COLOR_GREEN_FG: curses.COLOR_GREEN,
    ANSI_COLOR_YELLOW_FG: curses.COLOR_YELLOW,
    ANSI_COLOR_BLUE_FG: curses.COLOR_BLUE,
    ANSI_COLOR_MAGENTA_FG: curses.COLOR_MAGENTA,
    ANSI_COLOR_CYAN_FG: curses.COLOR_CYAN,
    ANSI_COLOR_WHITE_FG: curses.COLOR_WHITE,
}


def get_lexer(lines, filename):
    """Given the lines of text for the file and filename, try find a lexer
    that matches, returning the lexer object or None"""
    text = '\n'.join(lines)
    lexer = None
    try:
        lexer = get_lexer_for_filename(filename)
    except ClassNotFound:
        try:
            # Guess the lexer by the content of the file
            lexer = guess_lexer(text)
        except ClassNotFound:
            logging.info('pygments couldn\'t determine lexer')

    return lexer


def highlight_lines(lines, lexer):
    """Take the lines of text to be highlighted and return a list of
    highlighted lines using pygments"""
    # Join into one string since pygments needs one string to properly
    # highlight multi line statements.
    text = '\n'.join(lines)
    highlighted_lines = highlight(text, lexer, FORMATTER).splitlines()
    # NOTE: pygments.highlight clobbers any blank lines at the beginning of the
    # file, count how many we should have and re add them.
    # Assemble a list of empty lists. Since parse_highlighed_line returns just
    # an empty list for an empty line.
    # Get empty lines at the beginning of the file
    empty_lines_start = []
    empty_lines_end = []
    curr_line_start = lines[0]
    curr_line_end = lines[-1]
    while '' in [curr_line_start, curr_line_end]:
        if curr_line_start == '':
            empty_lines_start.append([])
            curr_line_start = lines[len(empty_lines_start)]
        if curr_line_end == '':
            empty_lines_end.append([])
            curr_line_end = lines[-len(empty_lines_end)]

    return (empty_lines_start +
            # Parse each line into curses attributes
            [parse_highlighed_line(highlighted_line)
             for highlighted_line in highlighted_lines] +
            empty_lines_end)


def parse_highlighed_line(highlighted_line):
    """Takes an ANSI highlighted line of text and returns a list of tuples,
    each of which describing a section of the line and its associated curses
    attribute to colour it."""
    logging.info('Working on line: %s:', highlighted_line)
    split_tokens = highlighted_line.split('\x1b[')
    saved_start = None
    if split_tokens[0] != '':
        # There was text before the first escape sequence, this portion does
        # not need to be coloured
        saved_start = split_tokens[0]
        split_tokens = split_tokens[1:]

    try:
        ansi_content_tuples = [re.match(r'(.*?)m(.*)', _s).groups()
                               for _s in split_tokens if _s]
    except AttributeError:
        # No ansi codes in this line. Just return a list of a single tuple,
        # that describes the whole line, with the default cureses attribute
        return [(highlighted_line, curses.A_NORMAL)]

    logging.info('%s\n%s', highlighted_line, ansi_content_tuples)
    res = []

    # Convert the ansi code portion of each tuple into curses attributes
    for ansi_codes, token_str in ansi_content_tuples:
        if ';' in ansi_codes:
            # There are multiple ansi codes for this portion
            ansi_code_list = ansi_codes.split(';')
        else:
            ansi_code_list = [ansi_codes]

        # map is just fine, settle down pylint
        # pylint: disable=bad-builtin
        # str --> int ansi codes
        ansi_code_list = map(int, ansi_code_list)

        # ansi --> curses
        curses_attributes = [ANSI_TO_CURSES[ansi_code]
                             for ansi_code in ansi_code_list]

        if len(curses_attributes) > 1:
            # Curses attributes are combined with bitwise OR
            curses_attributes = reduce(ior, curses_attributes)
        else:
            curses_attributes = curses_attributes[0]

        res.append((token_str, curses_attributes))

    # Add the un-coloured portion of the line we saved earlier if any
    if saved_start:
        res = [(saved_start, curses.A_NORMAL)] + res

    return res
