import argparse
from . import server

def run():
    parser = build_parser()
    args = parser.parse_args()
    args.func()

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose')
    parser.set_defaults(func=server.run)
    
    sp = parser.add_subparsers()
    sp_serve = sp.add_parser('serve')
    sp_serve.set_defaults(func=server.run)
    return parser