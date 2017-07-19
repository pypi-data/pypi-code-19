# -*- coding: utf-8 -*-

"""Console script for test_pkg1."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
#from builtins import *

import click


def hello():
    """ Return a Hello, World!"""
    return("Hello, World!")

def say_hello():
    """Print Hello world"""
    print(hello())

def say_hello1():
    print("say_hello1")



@click.command()
def main(args=None):
    """Console script for test_pkg1."""
    click.echo("Replace this message by putting your code into "
               "test_pkg1.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")

if __name__ == "__main__":
    main()
