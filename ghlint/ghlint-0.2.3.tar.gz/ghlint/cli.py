# encoding=utf8
import sys
from inspect import getsourcefile
from os import path


CURRENT_DIR = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, CURRENT_DIR[: CURRENT_DIR.rfind(path.sep)])


import click # pylint: disable=wrong-import-position
from ghlint import config # pylint: disable=wrong-import-position
from ghlint import lint # pylint: disable=wrong-import-position


@click.command()
def main():
    settings = config.settings()
    lint.run(settings)
    return

if __name__ == '__main__':
    main()
