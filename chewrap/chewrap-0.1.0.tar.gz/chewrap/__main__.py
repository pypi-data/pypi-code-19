#!/usr/bin/env python
"""This file is the main entry point to CheWrap via the terminal."""

from .core import CheWrap


def main():
    che_wrap = CheWrap()
    che_wrap.run()


if __name__ == '__main__':
    main()
