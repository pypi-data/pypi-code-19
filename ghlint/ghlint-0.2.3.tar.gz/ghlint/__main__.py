# encoding=utf8
import sys
from inspect import getsourcefile
from os import path


CURRENT_DIR = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, CURRENT_DIR[: CURRENT_DIR.rfind(path.sep)])


from ghlint import config # pylint: disable=wrong-import-position
from ghlint import lint # pylint: disable=wrong-import-position


def main():
    settings = config.settings()
    lint.run(settings)

if __name__ == "__main__":
    main()
