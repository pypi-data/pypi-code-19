# Direct connection with microcontroller
from __future__ import print_function
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Mara server emulator"
    )
    parser.add_argument('-p', '--port', default=9761, type=int)
    parser.add_argument('-a', '--address', default='0', type=str)


if __name__ == '__main__':
    main()
