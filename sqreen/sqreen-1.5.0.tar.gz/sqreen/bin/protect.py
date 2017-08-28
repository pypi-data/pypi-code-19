# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Script modifying the env to run our sitecustomize script before everyone else
"""
from __future__ import print_function

import sys
import os

from copy import copy
from os.path import dirname


def where_sitecustomize():
    """ Returns the path of the sitecustomize package
    """
    current_file = os.path.split(__file__)[0]
    path = os.path.join(dirname(current_file), 'sitecustomize')

    return path


def protect():
    """ Call the passed binary passed in argument with the right PYTHONPATH
    """
    # Check that we have all mandatory arguments
    if len(sys.argv) <= 1:
        print("Usage: sqreen-start ...", file=sys.stderr)
        print("You can check https://doc.sqreen.io/v1.1/docs/python-agent-installation"
              " for more informations.", file=sys.stderr)
        sys.exit(1)

    new_env = copy(os.environ)
    if 'PYTHONPATH' in new_env:
        new_env['PYTHONPATH'] = os.pathsep.join([where_sitecustomize(), new_env['PYTHONPATH']])
    else:
        new_env['PYTHONPATH'] = where_sitecustomize()

    new_args = sys.argv[1:]
    os.execvpe(new_args[0], new_args, new_env)
