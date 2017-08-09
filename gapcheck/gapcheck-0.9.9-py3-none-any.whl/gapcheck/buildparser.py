# -*- coding: utf-8 -*-

import argparse

from gapcheck import __version__


def build_parser():
    """ Parser args """
    parser = argparse.ArgumentParser()

    parser.add_argument('-e', '--file-extension', type=str,
                        dest='extension', default='flac',
                        help='File extension (default FLAC)')

    parser.add_argument('-p', '--path', type=str,
                        dest='path', default='.',
                        help='Path (default current path)')

    parser.add_argument('-s', '--last-analyzed-seconds', type=float,
                        dest='seconds', default=0.2,
                        help='Last analyzed seconds (default 0.2)')

    parser.add_argument('-a', '--limit-maximum-amplitude', type=float,
                        dest='max_amplitude', default=0.0099,
                        help='Limit maximum amplitude (default 0.0099)')

    parser.add_argument('-j', '--join-files-with-gap', action='store_true',
                        dest='join', default=False,
                        help='Join files with gap')

    parser.add_argument('-f', '--analyze-already-tested', action='store_true',
                        dest='force_analyze', default=False,
                        help='Analyze files already tested')

    parser.add_argument('-d', '--verbose', action='store_true',
                        dest='verbose', default=False,
                        help='Prints extra debugging information')

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)

    return parser
