#!/usr/bin/python

import argparse
import gzip
import os
import sys

from lhc.io.vcf.iterator import VcfIterator
from lhc.io.vcf.merger import VcfMerger


def merge(iterators, out, bams, *, variant_fields=[]):
    merger = VcfMerger(iterators, bams=bams, variant_fields=variant_fields)
    for key, values in merger.hdrs.items():
        for value in values:
            out.write('##{}={}\n'.format(key, value))
    out.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO')
    if len(merger.samples) > 0:
        out.write('\tFORMAT\t{}'.format('\t'.join(merger.samples)))
    out.write('\n')
    for entry in merger:
        out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
            str(entry.chromosome),
            entry.position + 1,
            entry.data['id'],
            entry.data['ref'],
            ','.join(entry.data['alt']),
            '.' if entry.data['qual'] is None else entry.data['qual'],
            ','.join(entry.data['filter']),
            ':'.join('{}={}'.format(k, v) for k, v in entry.data['info'].items()),
            ':'.join(entry.data['format']),
            '\t'.join(format_sample(entry.data['samples'][sample], entry.data['format'])
                      if sample in entry.data['samples']
                      else '.' for sample in merger.samples)
        ))
    out.close()


def format_sample(sample, format):
    return ':'.join(sample[key] for key in format)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('inputs', nargs='+')
    add_arg('-b', '--bams', nargs='+',
            help='Include read counts from bam files')
    add_arg('-o', '--output',
            help='Name of the merged vcf (default: stdout).')
    add_arg('-f', '--variant-fields', nargs='+',
            help='All fields that are variant specific')
    parser.set_defaults(func=init_merge)
    return parser


def init_merge(args):
    non_existent = [filename for filename in args.inputs if not os.path.exists(filename)]
    if len(non_existent) > 0:
        raise FileNotFoundError('The following files were not found:\n{}'.format('\n'.join(non_existent)))

    inputs = [VcfIterator(fileobj) for fileobj in
              (gzip.open(i, 'rt') if i.endswith('.gz') else open(i, encoding='utf-8')
               for i in args.inputs)]
    names = trim_names(args.inputs)
    for name, input in zip(names, inputs):
        if len(input.samples) == 0:
            input.samples.append(name)
    output = sys.stdout if args.output is None else open(args.output)
    merge(inputs, output, args.bams, variant_fields=args.variant_fields)


def trim_names(inputs):
    inputs = [os.path.basename(input) for input in inputs]
    smallest_name_length = min(len(input) for input in inputs)
    i = 1
    while i < smallest_name_length:
        if len(set(input[-i] for input in inputs)) > 1:
            break
        i += 1
    return [input[:-i] for input in inputs]


if __name__ == '__main__':
    sys.exit(main())
