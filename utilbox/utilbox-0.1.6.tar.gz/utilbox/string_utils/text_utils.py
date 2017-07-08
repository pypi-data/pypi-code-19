"""
Utility module to manipulate multi-line text.
"""

import re
import pprint


__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class TextUtils:
    """
    Utility class containing methods for manipulation of multi-line text.
    """

    def __init__(self):
        pass

    @staticmethod
    def break_into_lines(text):
        """
        Breaks down multi-line text into a list of strings.

        :param text: The text to be converted to list of string lines.

        :return: List of strings represent lines of supplied text.
        :rtype: list
        """

        return text.split("\n")

    @staticmethod
    def filter_text(text):
        """
        Strip off non-printable characters.

        Based on the Unicode database categorization: http://www.sql-und-xml.de/unicode-database/#kategorien

        :param text: The text to be filtered.

        :return: The filtered text.
        :rtype: str
        """

        # replacing \n with $s$
        text = text.replace('\n', '<br>')

        # method to remove all control characters from received text:
        # all_chars = (unichr(i) for i in xrange(0x110000))
        # control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc' and c != '\n' and c != '\r')

        # more efficient method to remove all control characters from received text:
        control_chars = ''.join(map(unichr, range(0, 32) + range(127, 160)))

        control_char_re = re.compile('[%s]' % re.escape(control_chars))

        return str(control_char_re.sub('', text))

    @staticmethod
    def get_pretty_text(text):
        """
        Returns a neatly formatted text.

        :param text: The text to be prettified.

        :return: The filtered text.
        :rtype: str
        """

        return str(pprint.pformat(text))
