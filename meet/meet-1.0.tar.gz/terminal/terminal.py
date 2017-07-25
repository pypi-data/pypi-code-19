#!usr/bin/python
#  terminal.py

import argparse


def main():
    pass


def get_user_input():
    try:
        parser = argparse.ArgumentParser(description='a cli application to \
                create a meeting notes google doc or local markdown file \
                current or impending meeting on your google calendar')
        parser.add_argument('-g', '--google',
                            help='create a new google doc with minutes',
                            action='store_true',
                            dest='google')
        parser.add_argument('-s', '--share',
                            help='automatically share the google doc with \
                                meeting participants',
                            action='store_true',
                            dest='share')
        parser.add_argument('-m', '--markdown',
                            help='create a local markdown file with minutes',
                            action='store_true',
                            dest='markdown')
        args = parser.parse_args()
        return args
    except ImportError:
        flags = None

if __name__ == '__main__':
    main()
