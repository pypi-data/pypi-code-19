"""
Utility module to manipulate strings.
"""

import re
import types

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class StringUtils:
    """
    Utility class containing methods for manipulation of strings.
    """

    def __init__(self):
        pass

    @staticmethod
    def is_blank(string):
        """
        Checks is supplied string is blank.

        :param string: The string to be verified.

        :return: True if string is blank, False otherwise.
        :rtype: bool
        """

        if string.strip():
            return False

        return True

    @staticmethod
    def join_list_elements(string_list, join_char=""):
        """
        Joins list elements into a single string, using the joining character.

        :param string_list: The list of strings to be joined.
        :param join_char: The character to use for joining the strings.

        :return: The combined string of joined list elements, if string_list is a valid list, False otherwise.
        :rtype: str
        """

        if isinstance(string_list, types.ListType):
            if len(string_list) > 0:
                return str(join_char).join(string_list)

        return False

    @staticmethod
    def remove_lines(text, line_count):
        """
        Removes specified number of lines from beginning or end of supplied text.

        :param text: Text from which lines are to be removed.
        :param line_count: The number of lines to remove.
                           +ve value starts removal from beginning and -ve value start removal from end.

        :return: The updated text with removed lines.
        :rtype: str
        """

        text_lines = text.split("\n")

        if len(text_lines) > 0:
            if line_count > 0:
                for index in range(0, line_count):
                    text_lines.remove(text_lines[index])
            elif line_count < 0:
                text_lines_r = text_lines
                text_lines_r.reverse()

                # print "baa... " + str(text_lines) + "...aab"
                # print "baaR... " + str(text_lines_r) + "...Raab"

                for index in range(0, line_count):
                    text_lines_r.remove(text_lines_r[index])

                text_lines = text_lines_r
                text_lines.reverse()
            else:
                pass

        updated_text = StringUtils.join_list_elements(text_lines, "\n")

        return updated_text

    @staticmethod
    def remove_lines_range(text, start_line_number, end_line_number):
        """
        Removes a range of lines from the supplied text.

        :param text: Text from which lines are to be removed.
        :param start_line_number: Starting line number where removal will begin.
        :param end_line_number: Ending line number where removal will end.

        :return: The updated text with removed lines.
        :rtype: str
        """

        text_lines = text.split("\n")

        if len(text_lines) > 0:
            for index in range(start_line_number, end_line_number):
                text_lines.remove(text_lines[index])

        updated_text = StringUtils.join_list_elements(text_lines, "\n")

        return updated_text

    @staticmethod
    def remove_lines_list(text, line_list):
        """
        Removes specified lines from the supplied text.

        :param text: Text from which lines are to be removed.
        :param line_list: List containing specific lines to remove from the text.

        :return: The updated text with removed lines.
        :rtype: str
        """

        text_lines = text.split("\n")

        if len(text_lines) > 0:
            for line_index in line_list:
                text_lines.remove(text_lines[line_index])

        updated_text = StringUtils.join_list_elements(text_lines, "\n")

        return updated_text

    @staticmethod
    def remove_leading_blanks(string):
        """
        Removes leading blank spaces from supplied string.

        :param string: String from which leading blanks are to be removed.

        :return: String with leading blanks removed.
        :rtype: str
        """

        text_lines = string.split("\n")

        if len(text_lines) > 0:
            for line in text_lines:
                if StringUtils.is_blank(line):
                    text_lines.remove(line)
                else:
                    break

        updated_string = StringUtils.join_list_elements(text_lines, "\n")

        return updated_string

    @staticmethod
    def remove_trailing_blanks(string):
        """
        Removes trailing blank spaces from supplied string.

        :param string: String from which trailing blanks are to be removed.

        :return: String with trailing blanks removed.
        :rtype: str
        """

        text_lines = string.split("\n")
        text_lines_r = ""

        if len(text_lines) > 0:
            text_lines_r = text_lines
            text_lines_r.reverse()

            for line in text_lines_r:
                if StringUtils.is_blank(line):
                    text_lines_r.remove(line)
                else:
                    break

        text_lines = text_lines_r
        text_lines.reverse()
        updated_string = StringUtils.join_list_elements(text_lines, "\n")

        return updated_string

    @staticmethod
    def extract_line(text, line_number):
        """
        Extracts specified line from the supplied text based on line number.

        :param text: Text from which line is to be extracted.
        :param line_number: Line number to be extracted.

        :return: The extracted line.
        :rtype: str
        """

        text_lines = text.split("\n")

        if len(text_lines) > 0:
            return text_lines[line_number - 1]

        return False

    @staticmethod
    def get_line_number(text, string):
        """
        Determines line number of first occurrence of given string within given text.

        :param text: Text in which 'string' is to be searched.
        :param string: Data to locate within given text.

        :return: The extracted line number.
        :rtype: str
        """

        text_lines = text.split("\n")

        # look for exact match in the supplied text
        line_ctr = 1
        for text_line in text_lines:
            if StringUtils.equals_ignore_case(text_line, string):
                return line_ctr

            line_ctr += 1

        line_ctr = 1
        for text_line in text_lines:
            if StringUtils.check_pattern(text_line, string):
                return line_ctr

            line_ctr += 1

        return False

    @staticmethod
    def check_pattern(text, pattern):
        """
        Looks for supplied pattern in given text.

        :param text: Text in which 'pattern' is to be searched.
        :param pattern: Pattern expression to locate within given text.

        :return: True if match was found, False otherwise.
        :rtype: bool
        """

        compiled_pattern = re.compile(pattern)

        if len(compiled_pattern.findall(text)) > 0:
            return True

        return False

    @staticmethod
    def equals_ignore_case(string1, string2):
        """
        Compares 2 given strings for equality regardless of case.

        :param string1: String to be compared for equality.
        :param string2: String to be compared for equality.

        :return: True, if matching, False otherwise
        :rtype: bool
        """

        return string1.lower() == string2.lower()

    @staticmethod
    def equals_match_case(string1, string2):
        """
        Compares 2 given strings for equality.

        :param string1: String to be compared for equality.
        :param string2: String to be compared for equality.

        :return: True, if matching, False otherwise
        :rtype: bool
        """

        return string1 == string2
