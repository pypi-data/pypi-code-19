import argparse
import sys

from ..wrapper import FastaWrapper


def wrap(input, output, *, width, chunk_size=2 ** 1):
    wrapper = FastaWrapper(input, width, chunk_size)
    fragment = next(wrapper)
    header = fragment.hdr
    output.write('>{}\n{}\n'.format(fragment.hdr, fragment.seq))
    for fragment in wrapper:
        if fragment.hdr != header:
            header = fragment.hdr
            output.write('>{}\n{}\n'.format(fragment.hdr, fragment.seq))
        else:
            output.write(fragment.seq)
            output.write('\n')


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?')
    add_arg('output', nargs='?')
    add_arg('-c', '--chunk-size', default=2 ** 16, type=int,
            help='The number of bytes to read at a time.')
    add_arg('-w', '--width', default=80, type=int,
            help='The maximum length of a sequence line (default: 80).')
    parser.set_defaults(func=init_wrap)
    return parser


def init_wrap(args):
    input = args.input if args.input else sys.stdin
    output = args.output if args.output else sys.stdin
    wrap(input, output, width=args.width, chunk_size=args.chunk_size)
    input.close()
    output.close()

if __name__ == '__main__':
    sys.exit(main())
