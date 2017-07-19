import argparse
import gzip
import sys

from lhc.io.bed.iterator import BedLineIterator
from lhc.tools.sorter import Sorter


def sort(iterator, max_lines=100000):
    sorter = Sorter(max_lines=max_lines)
    return sorter.sort(iterator)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input',
            help='name of the bed file with intervals')
    add_arg('-o', '--output', 
            help='output destination (default: stdout)')
    add_arg('-m', '--max-lines', default=1000000, type=int,
            help='maximum number of lines to process simultaneously')
    parser.set_defaults(func=sort_init)
    return parser


def sort_init(args):
    with sys.stdin if args.input is None else \
            gzip.open(args.input) if args.input.endswith('.gz') else \
                    open(args.input, encoding='utf-8') as input, \
            sys.stderr if args.output is None else \
                    open(args.output, 'w') as output:
        input = BedLineIterator(input)
        for line in sort(input, args.max_lines):
            output.write('{}\t{}\t{}\n'.format(line.chr, line.start + 1, '\t'.join(str(field) for field in line[2:])))

if __name__ == '__main__':
    import sys
    sys.exit(main())
