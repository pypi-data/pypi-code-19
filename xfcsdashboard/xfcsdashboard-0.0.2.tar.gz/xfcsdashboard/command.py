#!/usr/bin/env python3

import argparse

from xfcsdashboard import dashboard

# ------------------------------------------------------------------------------
def parse_arguments():
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(prog='xfcsdashboard', description='Plots FCS Metadata')

    parser.add_argument(
        '--input', '-i', nargs='+', type=argparse.FileType('rb'),
        metavar='<fcs_metadata.csv>', help='FCS metadata csv files to plot.')

    return parser.parse_args()


# ------------------------------------------------------------------------------
def main():
    args = parse_arguments()
    files = [infile.name for infile in args.input]
    dashboard.plot_csv(files)


# ------------------------------------------------------------------------------
