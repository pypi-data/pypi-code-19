#!/usr/bin/python
# -*- coding: UTF-8 -*-

from packemo.subpackage1 import foo1
from packemo.subpackage2 import foo2
from packemo.subpackage1.subsubpackage11 import foo11

description = """Hi,

This is the entrance of the packemo package.

"packemo" means package demo, which is a tiny Python package
containing some rather simple modules and a setup.py file.

This package tries to give a simple demonstration of how Python
packages are organized and how to write a setup.py.

---------------------------------------------------------------
"""


def main():
    print(description)

    print("Testing foo1: ")
    foo1.speak()
    print("")

    print("Testing foo2: ")
    foo2.speak()
    print("")

    print("Testing foo11: ")
    foo11.speak()


if __name__ == "__main__":
    main()
