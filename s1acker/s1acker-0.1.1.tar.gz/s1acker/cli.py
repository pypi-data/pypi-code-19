# -*- coding: utf-8 -*-
"""
    s1acker.cli
    ~~~~~~~~~~~

    The command line interface for s1acker

    :copyright: (c) 2017 by quinoa42.
    :license: MIT, see LICENSE for more details.
"""

import argparse
import logging
import pprint
import sys

from pkg_resources import get_distribution

from s1acker.__init__ import formatter
from s1acker.s1acker import S1ack

logger = logging.getLogger(__name__)

__version__ = get_distribution(__package__).version


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="image searching and downloading utility for stage1st",
        allow_abbrev=False
    )
    parser.add_argument(
        "srchtxt",
        metavar="SRCHTXT",
        help="the text to search",
        type=str,
        nargs='+'
    )
    parser.add_argument(
        "-n",
        "--srchuname",
        metavar="UNAME",
        help="the username of whom post the thread(s)",
        type=str
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        help="don't download the images; just list them",
        action="store_true"
    )
    parser.add_argument(
        "-o",
        "--path",
        metavar="DIR",
        help="the directory where images will be downloaded to",
        type=str,
        default=""
    )
    vq = parser.add_mutually_exclusive_group()
    vq.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=2,
        default=1,
        dest="verbosity"
    )
    vq.add_argument(
        "-q", "--quiet", action="store_const", const=0, dest="verbosity"
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {0}'.format(__version__)
    )
    logger = logging.getLogger(__package__)
    args = vars(parser.parse_args(argv))
    args['srchtxt'] = " ".join(args['srchtxt'])

    logger.debug("after parsing: %s", args)
    return args


def _set_logging(verbosity):
    logger = logging.getLogger(__package__)
    ch = logging.StreamHandler()
    if verbosity == 2:
        ch.setLevel(logging.DEBUG)
    else:  # verbosity == 1
        ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def main():
    args = parse_args(sys.argv[1:])
    if args['verbosity'] != 0:
        _set_logging(args['verbosity'])
    s = S1ack(args['srchtxt'], srchuname=args['srchuname'])
    imgs = s.search()
    if args['dry_run']:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(imgs)
    else:
        for img in imgs:
            img.download(args['path'])


if __name__ == "__main__":
    main()
