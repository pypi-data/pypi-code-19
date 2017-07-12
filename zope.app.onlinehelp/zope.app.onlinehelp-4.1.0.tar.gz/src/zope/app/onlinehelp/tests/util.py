##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Onlinehelp test utilities

"""
import os
import zope.app.onlinehelp.tests

here = os.path.dirname(zope.app.onlinehelp.tests.__file__)
input_dir = os.path.join(here, 'input')
output_dir = os.path.join(here, 'output')

def read_output(filename):
    filename = os.path.join(output_dir, filename)
    with open(filename, 'r') as f:
        return f.read()
