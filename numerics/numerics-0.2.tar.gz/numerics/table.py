#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
parse header-based CSV
"""

# imports
import argparse
import csv
import json
import os
import sys
import time
from collections import OrderedDict

string = (str, unicode)


def duplicates(*values):
    """return all duplicates in `values`"""

    counts = {value: values.count(value)
              for value in set(values)}
    retval = []
    for value in values:
        if counts[value] > 1 and value not in retval:
            retval.append(value)
    return retval


def read_table(fp, verbose=False):
    """read table with header and return list of dictionaries"""

    if isinstance(fp, string):
        with open(fp, 'r') as _fp:
            return read_table(_fp, verbose)

    # read CSV
    data = [row for row in csv.reader(fp)]

    # check data
    columns =  set([len(row) for row in data])
    if len(columns) != 1:
        raise AssertionError("Expected: a constant number of columns, instead got: {}".format(', '.join([str(column)
                                                                                                         for column in sorted(columns)])))
    columns = columns.pop()
    if verbose:
        print "{} columns".format(columns)
    data = [[item.strip() for item in row]
            for row in data]

    # xform to JSON-format structure
    header = data.pop(0)
    if verbose:
        print "Header:\n{header}".format(header=json.dumps(header, indent=1))
    duplicate_fields = duplicates(*header)
    if duplicate_fields:
        raise AssertionError("Duplicate header fields found: {duplicates}".format(duplicates=', '.join(duplicate_fields)))
    return [OrderedDict(zip(header, row))
            for row in data]


class TableParser(argparse.ArgumentParser):
    """CLI option parser"""

    def __init__(self, **kwargs):
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_arguments()
        self.options = None

    def add_arguments(self):
        self.add_argument('input', type=argparse.FileType('r'),
                          help="input CSV file")
        self.add_argument('-o', '--output', dest='output',
                          type=argparse.FileType('w'), default=sys.stdout,
                          help="output file to write to, or stdout by default")
        self.add_argument('-c', '--column', dest='columns', nargs='+',
                          help="column names to output")
        self.add_argument('--format', dest='format',
                          choices=('json', 'csv'), default='json',
                          help="output in this format")
        self.add_argument('-v', '--verbose', dest='verbose',
                          action='store_true', default=False,
                          help="be verbose")

    def parse_args(self, *args, **kw):
        options = argparse.ArgumentParser.parse_args(self, *args, **kw)
        self.validate(options)
        self.options = options
        return options

    def validate(self, options):
        """validate options"""

    def read_table(self):

        assert self.options

        data = read_table(self.options.input,
                          verbose=self.options.verbose)
        if not data:
            parser.error("No data found: {}".format(self.options.intput))
        if self.options.columns:
            header = data[0].keys()
            missing = [column
                       for column in self.options.columns
                       if column not in header]
            if missing:
                self.error("Columns not found in header: {0}".format(", ".join(missing)))
            header = options.columns
            data = [OrderedDict(zip(header,
                                    [row[column] for column in header]))
                    for row in data]
        return data

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = TableParser()
    options = parser.parse_args(args)

    # read table
    data = parser.read_table()

    # output to JSON
    if options.verbose:
        print ("Output {format}:".format(format=options.format))
    if options.format == 'json':
        options.output.write(json.dumps(data, indent=1))
    elif options.format == 'csv':
        writer = csv.writer(options.output)
        for row in data:
            writer.writerow([row[column] for column in header])


if __name__ == '__main__':
    main()
