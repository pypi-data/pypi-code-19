import argparse
import gzip
import sys

from lhc.collections import InOrderAccessIntervalSet
from lhc.io.bed import BedEntryIterator
from lhc.io.sam import SamIterator
from lhc.io.bam import BamIterator


def depth(interval_iterator, read_iterator):
    read_set = InOrderAccessIntervalSet(read_iterator, set_key=lambda x: (x.chr, x.pos, x.pos + x.qlen))

    for interval in interval_iterator:
        yield interval, len(read_set.fetch(interval.chr, interval.start, interval.stop))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('bed_file', help='regions to get the depth of')
    add_arg('bam_file', help='reads which contribute to depth (can be sam or bam)')
    add_arg('-o', '--output',
            help='output destination in bed format (default: stdout)')
    add_arg('-p', '--processes', default=None, type=int,
            help='number of parallel processes')
    add_arg('-s', '--simultaneous-entries', default=1000000, type=int,
            help='number of entries to submit to each worker')
    parser.set_defaults(func=depth_init)
    return parser


def depth_init(args):
    with gzip.open(args.bed_file) if args.bed_file.endswith('.gz') else \
            open(args.bed_file, encoding='utf-8') as interval_iterator, \
            sys.stdout if args.output is None else open(args.output, 'w') as output:
        interval_iterator = BedEntryIterator(interval_iterator)
        read_iterator = SamIterator(args.bam_file) if args.bam_file.endswith('.sam') else\
            BamIterator(args.bam_file)

        no_overlap = 0
        for region, count in depth(interval_iterator, read_iterator):
            output.write('{region.chr}\t{region.start}\t{region.stop}\t{count}\n'.format(region=region, count=count))
            no_overlap += count == 0
        output.close()
    
    sys.stderr.write('{} reads have no overlapping intervals\n'.format(no_overlap))

if __name__ == '__main__':
    sys.exit(main())
