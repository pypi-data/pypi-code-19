#!/usr/bin/env python
# Author: Jingyu Wang <badpasta@gmail.com>
# 
# Environment:
# -*- coding=utf-8 -*-
# Python by version 2.7.


from contextlib import contextmanager
from subprocess import call

import os


def vimFile(context, the_file):

    editor = os.environ.get('EDITOR', 'vim')
    with _underline(the_file) as sketch:
        sketch.write(context)
        sketch.flush()
        status = call([editor, sketch.name])
        sketch.flush()


def writeFile(context, the_file):

    with _underline(the_file) as sketch:
        sketch.write(context)
        sketch.flush()


def openFile(the_file):

    the_file = open(the_file)
    the_context = the_file.read()
    the_file.close()

    return the_context


def readFile(the_file):

    the_file = open(the_file)
    the_context = the_file.readlines()
    the_file.close()

    return the_context


@contextmanager    
def _underline(the_file):

    f =  open(the_file, 'w')
    yield f
    f.close()
    assert  os.path.exists(f.name)
