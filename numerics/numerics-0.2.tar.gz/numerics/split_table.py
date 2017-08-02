#!/usr/bin/env python

"""
split a CSV file with a header into parts
"""

# imports
import argparse
import csv
import chunk
import sys
import table
from cli import ensure_dir

class SplitTableParser(table.TableParser):

    def add_arguments(self):
        self.add_argument('input', type=argparse.FileType('r'),
                          help="input CSV file")
        self.add_argument('-o', '--output', dest='output',
                          type=ensure_dir,
                          help="output directory to write to, or stdout by default")
        self.add_argument('-c', '--column', dest='columns', nargs='+',
                          help="column names to output")
        self.add_argument('-v', '--verbose', dest='verbose',
                          action='store_true', default=False,
                          help="be verbose")
        self.add_argument('--name', '--column-name', dest='column_name',
                          help="column name to use for filename")


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = SplitTableParser(description=__doc__)
    options = parser.parse_args(args)

    # read CSV
    data = parser.read_table()

    header = data[0].keys()
    assert header

    if options.column_name:
        assert options.column_name in header
    else:
        column_name = header[0]

    # output
    # right now, only one at a time
    filename_template = '{index}-{column}.csv'
    for index, row in enumerate(data):

        filename = filename_template.format(index=index, column=row[column_name])
        print filename

        output_data = [list(header)]

if __name__ == '__main__':
    main()
