# coding:utf-8
from enum import Enum

class Colour(Enum):
    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    NC = '\033[0m'

def cprint(content, colour=Colour.RED):
    print "{colour}{content}{nc}".format(colour=colour.value, content=content, nc=Colour.NC.value)
