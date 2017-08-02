#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
normalize columns
"""

# imports
import sys
from .convert import numeric
from .data import transpose
from .manipulate import ManipulationParser

# module globals
__all__ = ['normalize', 'NormalizationParser']

def normalize(*data):
    """normalize data"""
    norm = float(sum(data))
    return [i/norm for i in data]

class NormalizationParser(ManipulationParser):
    """CLI option parser"""


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = NormalizationParser()
    options = parser.parse_args(args)

    # get columns
    columns = parser.typed_data()
    for index in range(len(columns)):
        column = columns[index]
        if column and isinstance(column[0], numeric):
            columns[index] = normalize(*column)

    # output
    parser.write(transpose(columns))

if __name__ == '__main__':
    main()


