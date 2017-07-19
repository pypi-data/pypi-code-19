#!/usr/bin/env python

import argparse

from repl import JSONRepl

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path to a JSON graph to load")
    args = parser.parse_args()

    app = JSONRepl(filepath=args.filepath)
    app.cmdloop()
