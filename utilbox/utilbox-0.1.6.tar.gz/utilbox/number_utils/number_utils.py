"""
Utility module to handle manipulation of numeric data.
"""


__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class NumberUtils():
    """
    Utility class containing methods for manipulation of numeric data.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_missing_numbers(number_list):
        """
        Takes a sequence of numbers and returns a copy additionally containing all the missing numbers in the sequence.

        Example:
        If a list [1, 4, 6] is provided as input, the returned list value will be [1, 2, 3, 4, 5, 6].

        :param number_list: The list/sequence of numbers.

        :return: Copy of the input list with additional numbers which were 'missing' in the original.
        :rtype: list
        """

        # make sure all elements are integers
        number_list = list(map(int, number_list))
        number_list = sorted(number_list)

        start, end = number_list[0], number_list[-1]

        return sorted(set(xrange(start, end + 1)).difference(number_list))
