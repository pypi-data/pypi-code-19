import argparse
import sys

from lhc.io.vcf.iterator import VcfIterator


def filter(input, _filter=None):
    it = VcfIterator(input)
    for k, vs in it.hdrs.items():
        for v in vs:
            yield '{}={}\n'.format(k, v)
    yield '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(it.samples) + '\n'
    for line in it:
        local_variables = line._asdict()
        local_variables.update({'NOPASS': 'NOPASS', 'PASS': 'PASS'})
        if eval(_filter, local_variables):
            yield '{}\n'.format(line)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?',
            help='name of the vcf_ file to be filtered (default: stdin).')
    add_arg('output', nargs='?',
            help='name of the filtered vcf_ file (default: stdout).')
    add_arg('-f', '--filter',
            help='filter to apply (default: none).')
    parser.set_defaults(func=filter_init)
    return parser


def filter_init(args):
    with sys.stdin if args.input is None else open(args.input, encoding='utf-8') as input, \
            sys.stdout if args.output is None else open(args.output, 'w') as output:
        for line in filter(input, args.filter):
            output.write(line)


if __name__ == '__main__':
    sys.exit(main())
