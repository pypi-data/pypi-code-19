import argparse
import os
import sys
from sosaxy import RecordStream
import utils

def main():
    ns = parse_args(sys.argv[1:])
    run(ns)

def parse_args(args):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="commands", dest="cmd")    

    x2j = subparsers.add_parser('x2j', help='extract desired xml fields into a line-delimited json file')
    x2j.add_argument('input_file', action='store', help='the input file')
    x2j.add_argument('output_file', action='store', help='the output file')
    x2j.add_argument('boundary', action='store', help='the record boundary defined within the xml')
    x2j.add_argument('fields', nargs='+', action='store', help='the fields to extract from the xml')

    return parser.parse_args(args)

def run(ns):
    if ns.cmd == 'x2j':
        directory = os.path.dirname(ns.output_file)

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(ns.output_file, 'w') as out:
            rs = RecordStream(ns.input_file, ns.boundary, ns.fields, lambda x: utils.write_json(out, x))
            rs.play()
