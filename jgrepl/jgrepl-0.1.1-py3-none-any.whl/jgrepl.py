#!/usr/bin/env python

import argparse

from jgrepl.repl import JSONRepl

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path to a JSON graph to load")
    args = parser.parse_args()

    app = JSONRepl(filepath=args.filepath)
    app.cmdloop()

if __name__ == '__main__':
    main()
