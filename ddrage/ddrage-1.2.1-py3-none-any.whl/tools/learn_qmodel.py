#!/usr/bin/env python
"""Module to create .qmodel files from a set of FASTQ files."""
import glob
import numpy as np
import os
import sys
import argparse

from collections import Counter



def find_fastq_files(args):
    """Compile a list of all input files."""
    # flatten the command line parameters
    all_paths = []
    for paths in args.files:
        all_paths.extend(paths)
    # glob them, if possible
    all_files = []
    for path in all_paths:
        globbed = glob.glob(path)
        if not globbed:
            print("Could not locate file:", path, file=sys.err)
            sys.exit(1)
        all_files.extend(globbed)
    # return extended list of files
    return all_files


def count_quality_values(args, paths):
    """Count quality values for all FASTQ files."""

    # initialize a counter for quality values for each position
    read_length = args.length
    all_counts = [Counter() for _ in range(read_length)]

    # count all quality values
    for path in paths:
        count_fastq_file(args, path, all_counts)

    return all_counts


def count_fastq_file(args, path, all_counts):
    """Count quality values in one fastq file and add the results to all_counts in place."""
    print("  Tallying {}".format(path))
    read_length = args.length

    with open(path, "rb") as fastq_file:
        for i, values in enumerate(fastq_file):
            if i % 4 == 3:
                # found a quality line
                for pos, val in enumerate(values.strip(b"\n")):
                    if pos < read_length:
                        all_counts[pos][val] += 1


def compute_relative_abundance(args, all_counts):
    """Compute relative abundances from absolute counts."""
    relative_counts = None

    for pos, pos_tally in enumerate(all_counts):
        total = sum(pos_tally.values())
        probs = np.array([pos_tally[x] / total if pos_tally[x] else 0 for x in range(args.length)])
        if relative_counts is not None:
            relative_counts = np.vstack((relative_counts, probs))
        else:
            relative_counts = probs

    return relative_counts


def compile_qmodel(args, relative_counts):
    """Interpret probs files, absolute QV counts per position."""

    nr_positions = args.length # only consider valid read positions
    nr_quality_values = 104-33 # only consider valid PHRED scores in illumina format
    # initialize array to be plotted
    values = np.zeros(shape=(nr_quality_values, nr_positions), dtype=np.double)

    # transfer probabilities to numpy array
    for pos, probs in enumerate(relative_counts):
        if pos >= nr_positions:
            continue
        else:
            for qvalue, prob in enumerate(probs):
                if 33 < qvalue < 104:
                    # convert ASCII to PHRED
                    values[qvalue-33][pos] = prob
    print("Writing output to", args.output)
    np.savetxt(args.output, values)



def get_argument_parser():
    description_text = ("This tool compiles a position-wise distribution of quality values from one or more "
                        "FASTQ files. It creates a .qmodel file which can be passed to RAGE using the -q parameter."
    )
    parser = argparse.ArgumentParser(
        description=description_text)

    parser.add_argument(
        help="Path(s) to one or more FASTQ files.",
        action="append",
        dest="files",
        nargs="+",
        metavar="FASTQ_PATH",
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file name/path. Default: custom.qmodel",
        action="store",
        dest="output",
        default="custom.qmodel",
    )

    parser.add_argument(
        "-l", "--length",
        help=("Maximum read length. All values after this position will "
              "be truncated and not become part of the model. "
              "Default: 100"
        ),
        action="store",
        dest="length",
        type=int,
        default=100,
    )

    return parser


def main():
    argparser = get_argument_parser()
    args = argparser.parse_args()
    print("Learning quality model:")
    all_files = find_fastq_files(args)
    all_counts = count_quality_values(args, all_files)
    relative_abundances = compute_relative_abundance(args, all_counts)
    compile_qmodel(args, relative_abundances)


if __name__ == '__main__':
    main()
