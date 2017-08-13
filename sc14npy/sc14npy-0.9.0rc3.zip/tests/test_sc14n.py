#! python2
# -*- coding: utf8 -*-

"""Some tests for `sc14n.py` the Python interface to SC14N."""

# test_sc14n_t.py: version 0.9.0

# ************************** LICENSE *****************************************
# Copyright (C) 2017 David Ireland, DI Management Services Pty Limited.
# <http://www.di-mgt.com.au/contact/> <www.cryptosys.net>
# The code in this module is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>
# ****************************************************************************

import context   # Setup path to module in parent
from sc14n import *  # @UnusedWildImport
import cryptosyspki as pki
import os
import sys

_MIN_DLL_VERSION = 100

# Show some info about the core DLL
print "DLL version =", Gen.version()
print "cwd =", os.getcwd()

if Gen.version() < _MIN_DLL_VERSION:
    raise Exception('Require DLL version ' +
                    str(_MIN_DLL_VERSION) + ' or greater')


# FILE-RELATED UTILITIES
def read_binary_file(fname):
    with open(fname, "rb") as f:
        return bytearray(f.read())


def read_text_file(fname):
    with open(fname, "rb") as f:
        return str(f.read())


def write_file(fname, data):
    with open(fname, "wb") as f:
        f.write(data)


def _print_file(fname):
    """Print contents of text file"""
    s = read_text_file(fname)
    print s


# ERROR
def disp_error(n):
    """Display details of last error."""
    s = Err.last_error()
    print "ERROR %d: %s: %s" % (n, Err.error_lookup(n), "\n" + s if s else "")


###################
# THE TESTS PROPER
###################

def test_version():
    print "VERSION:", Gen.version()
    print "module_name =", Gen.module_name()
    print "compile_time =", Gen.compile_time()
    print "platform =", Gen.core_platform()
    print "licence_type =", Gen.licence_type()


def test_olamundo():
    # Compute digest value of entire file (after transforming)
    fname = "olamundo.xml"
    print "FILE:", fname
    digval = C14n.file2digest(fname)
    print "DIG:", digval
    fname = "olamundo-utf8.xml"
    print "FILE:", fname
    digval = C14n.file2digest(fname)
    print "DIG:", digval
    fname = "olamundo-utf8bom.xml"
    print "FILE:", fname
    digval = C14n.file2digest(fname)
    print "DIG:", digval

    fname = "olamundo-base.xml"
    print "FILE:", fname
    s = C14n.file2string(fname, "Signature", Tran.EXCLUDEBYTAG)
    print "EXCLUDE <Signature>:\n", s.decode('utf-8')


def test_input_examples():
    print "Testing input examples..."

    # Example 1. Excludes the first element with the tag name <Signature>
    r = C14n.file2file("c14nfile1.txt", "input.xml", "Signature", Tran.EXCLUDEBYTAG)
    assert(r)

    # Example 2. Finds and transforms the first element with the tag name <SignedInfo>
    r = C14n.file2file("c14nfile2.txt", "input.xml", "SignedInfo", Tran.SUBSETBYTAG)
    assert(r)

    # Example 3. Finds and transforms the third element with the tag name <Data>
    r = C14n.file2file("c14nfile3.txt", "input.xml", "Data[3]", Tran.SUBSETBYTAG)
    assert(r)

    # Example 4. Finds and transforms the element with attribute Id="foo"
    r = C14n.file2file("c14nfile4.txt", "input.xml", "foo", Tran.SUBSETBYID)
    assert(r)

    # Example 5. Finds and transforms the element with attribute ID="bar"
    r = C14n.file2file("c14nfile5.txt", "input.xml", "ID=bar", Tran.SUBSETBYID)
    assert(r)

    # Example 6. Excludes element with attribute Id="thesig"
    r = C14n.file2file("c14nfile6.txt", "input.xml", "thesig", Tran.EXCLUDEBYID)
    assert(r)

    print "...done input examples."


def test_input_to_digest():
    print "Testing input examples to digest..."

    # Same as test_input_examples() except output diget value directly...

    # Example 1. Excludes the first element with the tag name <Signature>
    digval = C14n.file2digest("input.xml", "Signature", Tran.EXCLUDEBYTAG)
    print "DIG1 =", digval
    assert(len(digval) > 0)

    # Example 2. Finds and transforms the first element with the tag name <SignedInfo>
    digval = C14n.file2digest("input.xml", "SignedInfo", Tran.SUBSETBYTAG)
    print "DIG2 =", digval
    assert(len(digval) > 0)

    # Example 3. Finds and transforms the third element with the tag name <Data>
    digval = C14n.file2digest("input.xml", "Data[3]", Tran.SUBSETBYTAG)
    print "DIG3 =", digval
    assert(len(digval) > 0)

    # Example 4. Finds and transforms the element with attribute Id="foo"
    digval = C14n.file2digest("input.xml", "foo", Tran.SUBSETBYID)
    print "DIG4 =", digval
    assert(len(digval) > 0)

    # Example 5. Finds and transforms the element with attribute ID="bar"
    digval = C14n.file2digest("input.xml", "ID=bar", Tran.SUBSETBYID)
    print "DIG5 =", digval
    assert(len(digval) > 0)

    # Example 6. Excludes element with attribute Id="thesig"
    digval = C14n.file2digest("input.xml", "thesig", Tran.EXCLUDEBYID)
    print "DIG6 =", digval
    assert(len(digval) > 0)

    print "Expecting DIG3==DIG4 and DIG1==DIG6 in above results."


def main():
    test_version()
    test_olamundo()
    test_input_examples()
    test_input_to_digest()

    print "ALL DONE."


if __name__ == "__main__":
    main()
