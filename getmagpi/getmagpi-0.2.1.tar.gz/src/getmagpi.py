#! /usr/bin/python
# coding: utf-8

"""
                _                               _
      __ _  ___| |_ _ __ ___   __ _  __ _ _ __ (_)
     / _` |/ _ \\ __| '_ ` _ \\ / _` |/ _` | '_ \\| |
    | (_| |  __/ |_| | | | | | (_| | (_| | |_) | |
     \__, |\___|\__|_| |_| |_|\__,_|\__, | .__/|_|
     |___/                          |___/|_|

    Simple utility to sync free MagPi PDFs.

"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

import argparse
import errno
import fnmatch
import os
import re
import sys
from html.parser import HTMLParser

import requests

SOURCE = 'https://www.raspberrypi.org/magpi-issues/'
NON_EN = ['french', 'hebrew', 'spanish', 'italian']


class AnchorParse(HTMLParser):
    def __init__(self, args):
        HTMLParser.__init__(self)
        self.data = []
        self.en_only = args.en_only

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for key, value in attrs:
                if key == 'href' and 'pdf' in value.lower():
                    if (self.en_only and not (any(x in value.lower() for x in NON_EN))) or (not self.en_only):
                        self.data.append(value)


def fetch_pdf_index(args):
    """ Retrieves available files from the the MagPi PDF Library. """
    try:
        file_listing = requests.get(SOURCE).text
    except requests.exceptions.RequestException as e:
        print('\nERROR-- CANNOT RETRIEVE REMOTE FILES!\n\n{}'.format(e))
        raise
    parser = AnchorParse(args)
    parser.feed(file_listing)

    return parser.data


def check_folder(path):
    """ Confirms or creates (if it can) the supplied directory; then returns list of [any] existing PDFs. """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    rule = re.compile(fnmatch.translate('*.pdf'), re.IGNORECASE)
    return [name for name in os.listdir(path) if rule.match(name)]


def process_files(source_files, target_files, compare, path):
    """ Process source and destination files. """
    print(__doc__)
    missing_files = [file for file in source_files if file not in target_files]
    if len(missing_files) == 0:
        print('Your library is up to date.\n')
        exit()

    print('You are missing {} files:'.format(len(missing_files)))
    for file in missing_files:
        print('  {}'.format(file), end='')
        if not compare:
            print(' ...retrieving...')
            try:
                r = requests.get(os.path.join(SOURCE, file), stream=True)
                with open(os.path.join(path, file), 'wb') as fileout:
                    for chunk in r.iter_content(chunk_size=50000):
                        fileout.write(chunk)
            except requests.exceptions.RequestException as e:
                print('  ERROR RETRIEVING {}:\n{}'.format(file, e))
        else:
            print('')
    print('\nDone.')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'DOWNLOAD_PATH',
        action='store',
        help='Destination folder for downloads'
    )
    parser.add_argument(
        '-c', '--compare',
        action='store_true',
        default=False,
        dest='compare_only',
        help='Only display missing files (no downloads)'
    )
    parser.add_argument(
        '-e', '--english-only',
        action='store_true',
        default=False,
        dest='en_only',
        help='Ignore non-English files (identified via description)'
    )
    args = parser.parse_args()

    process_files(
        source_files=fetch_pdf_index(args),
        target_files=check_folder(path=args.DOWNLOAD_PATH),
        compare=args.compare_only,
        path=args.DOWNLOAD_PATH
    )


if __name__ == '__main__':
    sys.exit(main())
