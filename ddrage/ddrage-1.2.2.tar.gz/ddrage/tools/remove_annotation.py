#!/usr/bin/env python
import argparse
import os


def get_argument_parser():
    p = argparse.ArgumentParser(description=
        'Remove annotation from FASTQ headers. '
        'This might be necessary for some analysis tools, '
        'which can not cope with non-standard header formats. '
        'The extracted annotation is written to a file with the '
        'name <filename>_annotation.txt.' )
    p.add_argument('files', nargs='+', metavar='FASTQ',
        help="One or more fastq files from which the annotation is to be extracted.")
    p.add_argument('--buffersize', '-b', metavar="BYTES", 
        type=int, default=128*2**20,
        help='size of output buffer in bytes [128 MB]')
    return p


def main():
    p = get_argument_parser()
    args = p.parse_args()
    for fq_file in args.files:
        clean_file(fq_file, args.buffersize)
    


def clean_file(in_path, buffersize):
    """Remove annotation from a single FASTQ file."""
    # assume fastq files, not gzfastq
    prefix, extension = os.path.splitext(in_path)
    out_path_clean = prefix + "_noheader" + extension
    out_path_annotation = prefix + "_annotation.txt"

    print("Reading FASTQ file {}".format(in_path))
    print("Writing output files:")
    print("  - {}".format(out_path_clean))
    print("  - {}".format(out_path_annotation))

    with open(in_path, "rb") as in_file, \
            open(out_path_clean, "wb", buffering=buffersize) as out_file_clean,\
            open(out_path_annotation, "wb", buffering=buffersize) as out_file_annotation:

        for line in in_file:
            if line.startswith(b"@instrument"):
                casava_1, casava_2, rage = line.split(b" ", maxsplit=2)
                out_file_annotation.write(rage)
                out_file_clean.write(b" ".join((casava_1, casava_2)))
                out_file_clean.write(b"\n")
            else:
                out_file_clean.write(line)

if __name__ == '__main__':
    main()
