import gzip
import sys
import argparse

from contextlib import contextmanager
from typing import IO
from lhc.binf.genomic_coordinate import GenomicInterval
from lhc.io.bed.iterator import BedLineIterator


def filter(regions, expression=None) -> GenomicInterval:
    for region in regions:
        local_variables = {
            'chromosome': region.chromosome,
            'start': region.start,
            'stop': region.stop,
            'strand': region.strand,
            'data': region.data
        }
        if eval(expression, local_variables):
            yield region


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?',
            help='name of the bed file to be filtered (default: stdin).')
    add_arg('output', nargs='?',
            help='name of the filtered bed file (default: stdout).')
    add_arg('-f', '--filter', required=True,
            help='filter to apply (default: none).')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--region',
            help='filter in region (default: none).')
    group.add_argument('-x', '--exclude',
            help='filter out region (default: none).')
    parser.set_defaults(func=init_filter)
    return parser


def init_filter(args):
    with open_input(args.input) as input, open_output(args.output) as output:
        for item in input.hdrs:
            output.write(str(item) + '\n')
        for line in filter(input, args.filter):
            output.write('{}\t{}\t{}\t{}\n'.format(line.chromosome, line.start.position + 1, line.stop.position, line.data['name']))


@contextmanager
def open_input(filename: str):
    fileobj = sys.stdin if filename is None else \
        gzip.open(filename, 'rt', encoding='utf-8') if filename.endswith('.gz') else \
        open(filename, encoding='utf-8')
    if filename.endswith('.bed') or filename.endswith('.bed.gz'):
        yield BedLineIterator(fileobj)
    else:
        raise ValueError('unrecognised file format: {}'.format(filename))
    fileobj.close()


@contextmanager
def open_output(filename: str) -> IO:
    fileobj = sys.stdout if filename is None else \
        gzip.open(filename, 'wt', encoding='utf-8') if filename.endswith('.gz') else \
        open(filename, 'w', encoding='utf-8')
    yield fileobj
    fileobj.close()


if __name__ == '__main__':
    sys.exit(main())
