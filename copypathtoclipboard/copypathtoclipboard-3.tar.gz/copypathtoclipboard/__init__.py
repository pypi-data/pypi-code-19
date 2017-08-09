#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os, sys
import pyperclip

def main():
    pyperclip.copy(os.path.abspath(sys.argv[1]))

if __name__ == '__main__':
    main()