import argparse
import random
import sys

from ..iterator import VcfIterator


def sample(input, output, proportion):
    it = VcfIterator(input)
    for k, vs in it.hdrs.items():
        output.write('\n'.join('{}={}'.format(k, v) for v in vs))
    output.write('\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(it.samples) + '\n')
    for line in it:
        if random.random() < proportion:
            output.write('{}\n'.format(line))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?')
    add_arg('output', nargs='?')
    add_arg('-p', '--proportion', default=0.01, type=float)
    add_arg('-s', '--seed', type=int)
    parser.set_defaults(func=sample_init)
    return parser


def sample_init(args):
    with sys.stdin if args.input is None else open(args.input, encoding='utf-8') as input, \
            sys.stdout if args.output is None else open(args.output, 'w') as output:
        if args.seed is not None:
            random.seed(args.seed)
        sample(input, output, args.proportion)


if __name__ == '__main__':
    sys.exit(main())
