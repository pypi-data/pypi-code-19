#-*- coding: utf-8 -*-
import argparse
import os

import domain
import engine
import run

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_generate = subparsers.add_parser('generate')
    parser_generate.add_argument('template', metavar='FILE', help='source template for a WLST-script')
    parser_generate.set_defaults(func=engine.main)

    parser_run = subparsers.add_parser('run')
    parser_run.add_argument('script', nargs=argparse.REMAINDER, metavar='COMMAND', help='a WLST-script with arguments')
    parser_run.set_defaults(func=run.main)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
       print('exception: ' + str(e))

if __name__ == '__main__':
    main()

