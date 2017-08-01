#!/usr/bin/env python
"""
caption
header
"""

import argparse
import csv
import sys
import terminaltables

__version__ = '0.4.2'


def main(args):
    """
    Main function to turn CSV into grid tables using args from argparse
    """
    data = list(csv.reader(args.infile))
    table = terminaltables.AsciiTable(data)
    table.inner_row_border = True
    if not args.no_header:
        table.CHAR_H_INNER_HORIZONTAL = '='
    if not args.caption:
        output = table.table
    else:
        output = ': ' + args.caption + '\n\n' + table.table
    args.outfile.write(output)


def cli():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    # Args
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '--caption', help='The caption in the title, which will be print as pandoc styled caption.')
    parser.add_argument('--no-header', action='store_true',
                        help='If not specified, treat 1st row as header row.')
    # IO
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli()
