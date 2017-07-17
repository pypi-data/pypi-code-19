import sys
import argparse

from .__init__ import setup_webdriver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    args = parser.parse_args()
    setup_webdriver(args.version)


if __name__ == '__main__':
    sys.exit(main())
