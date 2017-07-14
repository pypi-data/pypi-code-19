#!/usr/bin/env python

"""Whitespace checking tool."""

import argparse
import os
import sys

from checker import WhitespaceChecker, RULES
from printer import ErrorPrinter
from version import Version


def main():
    args = _get_args()

    if args.list_rules:
        _list_rules()
        return 0

    checker = WhitespaceChecker(excluded_rules=args.excludes)
    for file_path in args.paths:
        checker.check_file(file_path)

    printer = ErrorPrinter(args.paths, checker.issues)
    printer.print_to_tty()
    if args.output_checkstyle:
        printer.write_checkstyle(args.output_checkstyle)

    if checker.issues:
        return 1

    return 0


def _list_rules():
    row_template = '{:<6s} {}'
    print(row_template.format('[RULE]', '[MESSAGE]'))
    for rule, message in RULES.items():
        print(row_template.format(rule, message))


def _get_args():
    def rule(rule_name):
        if rule_name not in RULES:
            raise argparse.ArgumentTypeError('Unknown rule')
        return rule_name

    parser = argparse.ArgumentParser(description=__doc__, version=Version().release, formatter_class=WideHelpFormatter)

    parser.add_argument('paths', type=str, nargs='*',
                        help='Path of files for test')
    parser.add_argument('-l', '--list-rules', dest='list_rules', action='store_true',
                        help='List rules')

    parser.add_argument('-e', '--exclude', dest='excludes', metavar='RULE', type=rule, nargs='+',
                        help='Exclude rule(s)')
    parser.add_argument('--checkstyle', dest='output_checkstyle', type=str,
                        help='Path of checkstyle output')

    args = parser.parse_args()

    if not args.list_rules and not args.paths:
        parser.error('paths')

    return args


class WideHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog, *args, **kwargs):
        indent_increment = 2
        max_help_position = 40
        width = int(os.getenv("COLUMNS", 120)) - 2

        super(WideHelpFormatter, self).__init__(prog, indent_increment, max_help_position, width)


if __name__ == '__main__':
    sys.exit(main())
