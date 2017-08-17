#!/usr/bin/env python
# encoding: utf-8

import click
from .app import recopytex

@click.group()
#@click.version_option(version=__version__)
def main():
    """ Recopytex - Managing your tribes

    Recopytex is a html app to manage tribe, students and scores.
    """
    pass

@main.command()
def start():
    """Start the application 

    """
    recopytex.config['BUNDLE_ERRORS'] = True
    recopytex.run(host="localhost")#, debug=True)


if __name__ == "__main__":
    main()

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
