#!/usr/bin/env python3
import argparse
import gzip
import itertools
import sys
import time
import random


def reservoir(iterator, k):
    """ Performs reservoir sampling of k items in iterator. Make sure that the iterator is a once-only iterator
    (ie. not created using the "range" function).

    :param iterator: set of items to sample from
    :param k: sample k items
    :return: list of sampled items
    """
    sample = list(itertools.islice(iterator, 0, k))
    for i, item in enumerate(iterator):
        replace = random.randint(0, i + k)
        if replace < k:
            sample[replace] = item
    return sample


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('input', nargs='?')
    parser.add_argument('k', type=int)
    parser.add_argument('-c', '--comment')
    parser.add_argument('-o', '--output')
    parser.add_argument('-s', '--seed')
    parser.set_defaults(func=reservoir_init)
    return parser


def reservoir_init(args):
    with sys.stdin if args.input is None else\
            gzip.open(args.input) if args.input.endswith('.gz') else\
                    open(args.input, encoding='utf-8') as input:
        random.seed(args.seed if args.seed else time.time())

        comments = []
        line = next(input)
        if args.comment is not None:
            while True:
                if not line.startswith(args.comment):
                    break
                comments.append(line)
                line = next(input)

        sample = reservoir(itertools.chain([line], input), args.k)

    with sys.stdout if args.output is None else open(args.output, 'w') as output:
        for line in itertools.chain(comments, sample):
            output.write(line)

if __name__ == '__main__':
    sys.exit(main())
