""":mod:`main` module defines the main :mod:`latest` command line script.


"""

import argparse
import os

from .util import path
from .config import create_config
from .config import config as Config
from .shortcuts import render


def main():
    try:
        args = parse_args()
        output = process(args)
        write(output, args)
    except Exception as e:
        print(e)


def parse_args():
    parser = argparse.ArgumentParser(description='A LaTeX-oriented template engine.')
    parser.add_argument('template', help='path to template file.')
    parser.add_argument('data', help='path to data file.')
    parser.add_argument('--output', '-o', help='path to output file; default to stdout.')
    parser.add_argument('--config', '-c', help='path to configuration file; default to ~/.latest/latest.cfg.')
    parser.add_argument('--format', '-f', help='format of data file.')
    return parser.parse_args()


def process(args):

    config = create_config(args.config) if args.config else Config
    return render(args.template, args.data, config=config, data_fmt=args.format)



def write(output, args):
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)


