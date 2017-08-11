#! python2
# -*- coding: latin-1 -*-

"""Some tests for `cryptosyspki` the Python interface to CryptoSys PKI"""

# test_pki.py: version 11.2.0

# ************************** LICENSE *****************************************
# Copyright (C) 2016-17 David Ireland, DI Management Services Pty Limited.
# All rights reserved. <www.di-mgt.com.au> <www.cryptosys.net>
# unless otherwise marked.
# For a copy, see <http://opensource.org/licenses/MIT>
# ****************************************************************************

from cryptosyspki import *  # @UnusedWildImport
import os
import sys
import pytest
import shutil
from glob import iglob
import tempfile

_MIN_PKI_VERSION = 110200

# Show some info about the core CryptoSys PKI DLL
print "PKI version =", Gen.version()
print "module_name =", Gen.module_name()
print "compile_time =", Gen.compile_time()
print "platform =", Gen.core_platform()
print "licence_type =", Gen.licence_type()
# Show some system values
print "sys.getdefaultencoding()=", sys.getdefaultencoding()
print "sys.getfilesystemencoding()=", sys.getfilesystemencoding()
print "sys.platform()=", sys.platform
print "cwd =", os.getcwd()

if Gen.version() < _MIN_PKI_VERSION:
    raise Exception('Require PKI version ' +
                    str(_MIN_PKI_VERSION) + ' or greater')

# GLOBAL VARS
# Remember CWD where we started
start_dir = os.getcwd()
# Temp directory to use as CWD for tests - set by  `setup_temp_dir()`
ourtmp_dir = ""
# Flag to delete tmp directory when finished - used in `reset_start_dir()`
# Change with command-line argument `nodelete` - see `main()`
delete_tmp_dir = True


# JIGGERY-POKERY FOR A TEMP WORKING DIRECTORY
#    start_dir/
#        test_pki.py  # this module
#        work/        # this _must_ exist
#            <all required test files>
#            pki.tmp.XXXXXXXX/    # created by `setup_temp_dir()`
#                <copy of all required test files>
#                <files created by tests>


def setup_temp_dir():
    """Set up a fresh temp directory to work in"""
    global ourtmp_dir
    # `work` should be a sub-directory of the cwd and must exist
    work_dir = os.path.join(start_dir, "work")
    print "\nExpecting to find work dir:", work_dir
    assert os.path.isdir(work_dir)
    # It should contain all the required test files
    # Create a temp sub-directory in `work`
    ourtmp_dir = os.path.join(work_dir, "pki.tmp." + Cnv.tohex(Rng.bytestring(4)))
    os.mkdir(ourtmp_dir)
    assert(os.path.isdir(ourtmp_dir))
    # copy the required temp files
    for f in iglob(os.path.join(work_dir, "*.*")):
        if (os.path.isfile(f) and not f.endswith('.zip')):
            shutil.copy(f, ourtmp_dir)

    # Set CWD to be inside temp
    os.chdir(ourtmp_dir)
    print "Working in new temp directory:", os.getcwd()


def reset_start_dir():
    if not os.path.isdir(start_dir):
        return
    if (ourtmp_dir == start_dir):
        return
    os.chdir(start_dir)
    print ""
    # print "CWD:", os.getcwd()
    # Remove the temp direcory
    if (delete_tmp_dir and 'pki.tmp' in ourtmp_dir):
        print "Removing temp directory:", ourtmp_dir
        shutil.rmtree(ourtmp_dir, ignore_errors=True)


# MORE JIGGERY_POKERY FOR py.test
@pytest.fixture(scope="module", autouse=True)
def divider_module(request):
    print("\n   --- module %s() start ---" % request.module.__name__)
    setup_temp_dir()

    def fin():
        print("\n   --- module %s() done ---" % request.module.__name__)
        reset_start_dir()
    request.addfinalizer(fin)


@pytest.fixture(scope="function", autouse=True)
def divider_function(request):
    print("\n   --- function %s() start ---" % request.function.__name__)
    os.chdir(ourtmp_dir)

    def fin():
        print("\n   --- function %s() done ---" % request.function.__name__)
        os.chdir(start_dir)
    request.addfinalizer(fin)


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


def _print_file_hex(fname):
    b = read_binary_file(fname)
    print Cnv.tohex(b)


def _dump_file(fname):
    """Print contents of text file with filename header and rulers"""
    s = read_text_file(fname)
    ndash = (24 if len(s) > 24 else len(s))  # hack
    print "FILE:", fname
    print "-" * ndash
    print s
    print "-" * ndash


def _dump_and_print_x509(fname):
    dumpfile = '_tmpdump.txt'
    # `fname` can be a filename or a string containing the base64 representation
    if os.path.isfile(fname):
        print "FILE:", fname
    else:
        print "STRING:", fname

    try:
        X509.text_dump(dumpfile, fname)
        _print_file(dumpfile)
    except PKIError as e:
        print "Woops! PKIError:", e


# def _dump_and_print_asn1(fname, opts=0):
#     dumpfile = '_tmpdump.txt'
#     # `fname` can be a filename or a string containing the base64 representation
#     if os.path.isfile(fname):
#         print "FILE:", fname
#     else:
#         print "STRING:", fname
# 
#     try:
#         Asn1.text_dump(dumpfile, fname, opts)
#         _print_file(dumpfile)
#     except PKIError as e:
#         print "Woops! PKIError:", e


def _dump_and_print_asn1(fname, opts=0):
    # `fname` can be a filename or a string containing the base64 representation
    if os.path.isfile(fname):
        print "FILE:", fname
    else:
        print "STRING:", fname

    # Create a secure temp file
    (fd, dumpfile) = tempfile.mkstemp()
    try:
        Asn1.text_dump(dumpfile, fname, opts)
        s = read_text_file(dumpfile)
        print s
        os.close(fd)
    except PKIError as e:
        print "Woops! PKIError:", e
    finally:
        os.remove(dumpfile)

#############
# THE TESTS #
#############


def test_version():
    assert Gen.version() >= _MIN_PKI_VERSION


def test_error_lookup():
    print "\nLOOKUP SOME ERROR CODES..."
    for n in range(10):
        s = Gen.error_lookup(n)
        print "error_lookup(" + str(n) + ")=" + s
        assert(len(s) > 0)


def test_cnv():
    print "\nTEST CNV FUNCTIONS..."

    # hex --> bytes --> base64
    b = Cnv.fromhex("FE DC BA 98 76 54 32 10")
    print "b=0x" + Cnv.tohex(b)
    print "b64(b)=" + Cnv.tobase64(b)
    assert(Cnv.tobase64(b) == "/ty6mHZUMhA=")

    # base64 --> bytes --> hex --> base64
    b = Cnv.frombase64("/ty6mHZUMhA=")
    print "b=0x" + Cnv.tohex(b)
    assert(Cnv.tohex(b) == "FEDCBA9876543210")
    print "b64(b)=" + Cnv.tobase64(b)
    assert(Cnv.tobase64(b) == "/ty6mHZUMhA=")

    # hex --> bytes --> base58
    b = Cnv.fromhex("00010966776006953D5567439E5E39F86A0D273BEED61967F6")
    print "b=0x" + Cnv.tohex(b)
    print "b58(b)=" + Cnv.tobase58(b)
    assert(Cnv.tobase58(b) == "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM")

    # base58 --> bytes --> hex
    h = Cnv.tohex(Cnv.frombase58("16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM"))
    print h
    assert(h == "00010966776006953D5567439E5E39F86A0D273BEED61967F6")

    # reverse bytes
    print "Using Cnv.reverse_bytes()..."
    b = Cnv.fromhex("DEADBEEF01")
    print "INPUT: ", Cnv.tohex(b)
    r = Cnv.reverse_bytes(b)
    print "OUTPUT:", Cnv.tohex(r)
    assert(Cnv.tohex(r) == "01EFBEADDE")

    # Possible corner cases...
    print "Test empty string..."
    b = Cnv.fromhex("")
    print "INPUT: ", Cnv.tohex(b)
    r = Cnv.reverse_bytes(b)
    print "OUTPUT:", Cnv.tohex(r)
    assert(Cnv.tohex(r) == "")

    b = Cnv.fromhex("01")
    print "INPUT: ", Cnv.tohex(b)
    r = Cnv.reverse_bytes(b)
    print "OUTPUT:", Cnv.tohex(r)
    assert(Cnv.tohex(r) == "01")

    b = Cnv.fromhex("0102")
    print "INPUT: ", Cnv.tohex(b)
    r = Cnv.reverse_bytes(b)
    print "OUTPUT:", Cnv.tohex(r)
    assert(Cnv.tohex(r) == "0201")

    print "Using Cnv.num_from_bytes()..."
    b = Cnv.fromhex("DEADBEEF")
    print "INPUT:", Cnv.tohex(b)
    # Default big-endian order
    n = Cnv.num_from_bytes(b)
    print "BE:", hex(n)
    assert(0xdeadbeef == n)
    # Little-endian order
    n = Cnv.num_from_bytes(b, endn=Cnv.EndianNess.LITTLE_ENDIAN)
    print "LE:", hex(n)
    assert(0xEFBEADDE == n)

    # Input shorter than 4 bytes is padded on the right with zeros
    b = b[:3]
    print "INPUT:", Cnv.tohex(b)
    n = Cnv.num_from_bytes(b)
    print "BE:", hex(n)
    assert(0xDEADBE00 == n)
    n = Cnv.num_from_bytes(b, endn=Cnv.EndianNess.LITTLE_ENDIAN)
    print "LE:", hex(n)
    assert(0xBEADDE == n)

    print "Using Cnv.num_to_bytes()..."
    n = 0xDEADBEEF
    b = Cnv.num_to_bytes(n)
    print "BE:", Cnv.tohex(b)
    b = Cnv.num_to_bytes(n, endn=Cnv.EndianNess.LITTLE_ENDIAN)
    print "LE:", Cnv.tohex(b)

    n = 0x01
    b = Cnv.num_to_bytes(n)
    print "BE:", Cnv.tohex(b)
    b = Cnv.num_to_bytes(n, endn=Cnv.EndianNess.LITTLE_ENDIAN)
    print "LE:", Cnv.tohex(b)


def test_cnv_utf8():
    print "\nTEST CNV WITH LATIN-1/UTF-8 CONVERSIONS..."

    # No guarantee these Latin-1/UTF-8 tests will work on all setups. YMMV.
    # This assumes the second line of the test file is
    #     -*- coding: latin-1 -*-
    # otherwise all bets are off

    # A string containing a Latin-1 character, LATIN SMALL LETTER E WITH ACUTE
    print "A string containing a Latin-1 character"
    s = "México"
    print "s='" + s + "'"
    print "s=0x" + Cnv.tohex(s)
    n = Cnv.utf8_check(s)
    print "Cnv.utf8_check(s)=", n, "(expecting 0)"
    print n, '==>', Cnv.utf8_check_to_string(n)
    b = Cnv.utf8_from_latin1(s)
    print "b=Cnv.utf8_from_latin1(s)=0x" + Cnv.tohex(b)
    print "b='" + b + "'"
    n = Cnv.utf8_check(b)
    print "Cnv.utf8_check(b)=", n, "(expecting 2)"
    print n, '==>', Cnv.utf8_check_to_string(n)
    t = Cnv.utf8_to_latin1(b)
    print "t=Cnv.utf8_to_latin1(b)='" + t + "'"
    print "t=0x" + Cnv.tohex(t)

    print "A string of simple ASCII characters"
    s = "abc"
    print "s='" + s + "'"
    print "s=0x" + Cnv.tohex(s)
    n = Cnv.utf8_check(s)
    print "Cnv.utf8_check(s)=", n, "(expecting 1)"
    assert (1 == n)
    print n, '==>', Cnv.utf8_check_to_string(n)
    b = Cnv.utf8_from_latin1(s)
    print "b=Cnv.utf8_from_latin1(s)=0x" + Cnv.tohex(b)
    n = Cnv.utf8_check(b)
    print "Cnv.utf8_check(b)=", n, "(expecting 1)"
    assert (1 == n)
    print n, '==>', Cnv.utf8_check_to_string(n)
    t = Cnv.utf8_to_latin1(b)
    print "t=Cnv.utf8_to_latin1(b)='" + t + "'"
    print "t=0x" + Cnv.tohex(t)

    # A byte array with a valid UTF-8-encoded array of chinese characters:
    # zhong guo (U+4E2D, U+56FD)
    b = Cnv.fromhex('e4b8ade59bbd')
    print "Chinese characters: zhong guo (U+4E2D, U+56FD) encoded in UTF-8"
    print "b=0x" + Cnv.tohex(b)
    n = Cnv.utf8_check(b)
    print "Cnv.utf8_check(b)=", n, "(expecting 3)"
    assert (3 == n)
    print n, '==>', Cnv.utf8_check_to_string(n)
    print "Try Cnv.utf8_to_latin1(b)..."
    try:
        _ = Cnv.utf8_to_latin1(b)
    except PKIError as e:
        print "(Expected) PKIError:", e

    # lookup invalid code
    print "Cnv.utf8_check_to_string(42)=>", Cnv.utf8_check_to_string(42)

    print "Bad UTF-8 (chopped)"
    b = "\xc3\xb3\xc3\xa9\xc3\xad\xc3\xa1\xc3"
    print "b=0x" + Cnv.tohex(b)
    n = Cnv.utf8_check(b)
    print "Cnv.utf8_check(b)=", n, "(expecting 0)"
    assert (0 == n)
    print n, '==>', Cnv.utf8_check_to_string(n)

    print "Bad UTF-8 (illegal)"
    b = "\xef\xbf\xbf"
    print "b=0x" + Cnv.tohex(b)
    n = Cnv.utf8_check(b)
    print "Cnv.utf8_check(b)=", n, "(expecting 0)"
    assert (0 == n)
    print n, '==>', Cnv.utf8_check_to_string(n)

    print "Check some files..."
    fname = 'test-iso88591.xml'
    n = Cnv.utf8_check_file(fname)
    print "Cnv.utf8_check_file('" + fname + "')=", n, "(expecting 0)"
    assert (0 == n)
    print n, '==>', Cnv.utf8_check_to_string(n)
    fname = 'test-utf8.xml'
    n = Cnv.utf8_check_file(fname)
    print "Cnv.utf8_check_file('" + fname + "')=", n, "(expecting 2)"
    assert (2 == n)
    print n, '==>', Cnv.utf8_check_to_string(n)


def test_cipher():
    print "\nTEST BLOCK CIPHER FUNCTIONS..."

    algstr = "Tdea/CBC/PKCS5"
    print algstr
    key = bytearray.fromhex('737C791F25EAD0E04629254352F7DC6291E5CB26917ADA32')
    iv = bytearray.fromhex("B36B6BFB6231084E")
    pt = bytearray.fromhex("5468697320736F6D652073616D706520636F6E74656E742E")

    ct = Cipher.encrypt(pt, key, iv, algstr)
    print Cnv.tohex(ct)
    b = bytearray.fromhex("5468697320736F6D652073616D706520636F6E74656E742E")
    print b
    assert(ct == bytearray.fromhex(
        "D76FD1178FBD02F84231F5C1D2A2F74A4159482964F675248254223DAF9AF8E4"))
    p1 = Cipher.decrypt(ct, key, iv, algstr)
    print p1
    assert(p1 == pt)

    print "Use default ECB mode (IV is ignored)"
    ct = Cipher.encrypt(pt, key, alg=Cipher.Alg.TDEA)
    print Cnv.tohex(ct)
    p1 = Cipher.decrypt(ct, key, alg=Cipher.Alg.TDEA)
    print p1
    assert(p1 == pt)

    ct = Cipher.encrypt(pt, key, iv, mode=Cipher.Mode.CBC,
                        alg=Cipher.Alg.TDEA)
    print Cnv.tohex(ct)
    p1 = Cipher.decrypt(ct, key, iv, mode=Cipher.Mode.CBC,
                        alg=Cipher.Alg.TDEA)
    print p1
    assert(p1 == pt)

    algstr = "Aes128/CBC/pkcs5"
    print algstr
    key = bytearray.fromhex('0123456789ABCDEFF0E1D2C3B4A59687')
    iv = bytearray.fromhex("FEDCBA9876543210FEDCBA9876543210")
    # Note we can pass plaintext as an ASCII string BUT not ciphertext
    pt = "Now is the time for all good men to"
    ct = Cipher.encrypt(pt, key, iv, algstr)
    print Cnv.tohex(ct)
    assert(ct == bytearray.fromhex(
        "C3153108A8DD340C0BCB1DFE8D25D2320EE0E66BD2BB4A313FB75C5638E9E17753C7E8DF5975A36677355F5C6584228B"))
    # Now decrypt using flags instead of alg string
    p1 = Cipher.decrypt(ct, key, iv, alg=Cipher.Alg.AES128,
                        mode=Cipher.Mode.CBC, pad=Cipher.Pad.PKCS5)
    print "P':", p1
    assert(p1 == pt)

    algstr = "Aes128/ECB/OneAndZeroes"
    print algstr
    ct = Cipher.encrypt(pt, key, algmodepad=algstr)
    print "CT:", Cnv.tohex(ct)
    p1 = Cipher.decrypt(ct, key, algmodepad="Aes128/ECB/NoPad")
    print "Pn:", Cnv.tohex(p1)
    p1 = Cipher.decrypt(ct, key, algmodepad=algstr)
    print "P':", Cnv.tohex(p1)
    print "P':", p1
    assert(p1 == pt)


def test_cipher_block():
    print "\nTEST CIPHER FUNCTIONS WITH EXACT BLOCK LENGTHS..."
    key = Cnv.fromhex("0123456789ABCDEFF0E1D2C3B4A59687")
    iv = Cnv.fromhex("FEDCBA9876543210FEDCBA9876543210")
    print "KY:", Cnv.tohex(key)
    print "IV:", Cnv.tohex(iv)
    pt = "Now is the time for all good men"
    print "PT:", pt
    print "PT:", Cnv.tohex(pt)
    okhex = "C3153108A8DD340C0BCB1DFE8D25D2320EE0E66BD2BB4A313FB75C5638E9E177"
    ct = Cipher.encrypt_block(
        pt, key, iv, alg=Cipher.Alg.AES128, mode=Cipher.Mode.CBC)
    print "CT:", Cnv.tohex(ct)
    print "OK:", okhex
    assert(okhex.upper() == Cnv.tohex(ct))
    p1 = Cipher.decrypt_block(
        ct, key, iv, alg=Cipher.Alg.AES128, mode=Cipher.Mode.CBC)
    print "P1:", Cnv.tohex(p1)
    print "P1:", p1

    # Using defaults (TDEA/ECB)
    key = Rng.bytestring(Cipher.keybytes(Cipher.Alg.TDEA))
    print "KY:", Cnv.tohex(key)
    ct = Cipher.encrypt_block(pt, key, iv)
    print "CT:", Cnv.tohex(ct)
    p1 = Cipher.decrypt_block(ct, key, iv)
    print "P1:", Cnv.tohex(p1)
    print "P1:", p1


def test_cipher_file():
    print "\nTEST CIPHER FILE FUNCTIONS..."
    file_pt = "hello.txt"
    write_file(file_pt, "hello world\r\n")
    print file_pt + ":",
    _print_file_hex(file_pt)
    key = Cnv.fromhex("fedcba9876543210fedcba9876543210")
    iv = Rng.bytestring(Cipher.blockbytes(Cipher.Alg.AES128))
    print "IV:", Cnv.tohex(iv)
    file_ct = "hello.aes128.enc.dat"
    n = Cipher.file_encrypt(file_ct, file_pt, key, iv,
                            "aes128-ctr", opts=Cipher.Opts.PREFIXIV)
    assert(n == 0)
    print file_ct + ":",
    _print_file_hex(file_ct)

    file_chk = "hello.aes128.chk.txt"
    n = Cipher.file_decrypt(file_chk, file_ct, key, iv,
                            "aes128-ctr", opts=Cipher.Opts.PREFIXIV)
    assert(n == 0)
    print file_chk + ":",
    _print_file_hex(file_chk)
    # check files are equal
    assert(read_binary_file(file_pt) == read_binary_file(file_chk))


def test_cipher_keywrap():
    print "\nTEST CIPHER KEY WRAP FUNCTIONS..."
    # AES-128
    keydata = Cnv.fromhex("00112233 44556677 8899aabb ccddeeff")
    kek = Cnv.fromhex("c17a44e8 e28d7d64 81d1ddd5 0a3b8914")
    wk = Cipher.key_wrap(keydata, kek, Cipher.Alg.AES128)
    print "WK=", Cnv.tohex(wk)
    assert(Cnv.tohex(wk) == "503D75C73630A7B02ECF51B9B29B907749310B77B0B2E054")

    # Unwrap
    k = Cipher.key_unwrap(wk, kek, Cipher.Alg.AES128)
    print "UNWRAPPED K=", Cnv.tohex(k)
    assert(k == keydata)

    # AES-256
    keydata = Cnv.fromhex(
        "8cbedec4 8d063e1b a46be8e3 69a9c398 d8e30ee5 42bc347c 4f30e928 ddd7db49")
    kek = Cnv.fromhex(
        "9e84ee99 e6a84b50 c76cd414 a2d2ec05 8af41bfe 4bf3715b f894c8da 1cd445f6")
    wk = Cipher.key_wrap(keydata, kek, Cipher.Alg.AES256)
    print "WK=", Cnv.tohex(wk)
    assert(Cnv.tohex(
        wk) == "EAFB901F82B98D37F17497063DE3E5EC7246AB57200AE73EDDDDF24AA403DAFA0C5AE151D1746FA4")

    # Unwrap
    k = Cipher.key_unwrap(wk, kek, Cipher.Alg.AES256)
    print "UNWRAPPED K=", Cnv.tohex(k)
    assert(k == keydata)

    # Triple DES
    print "Using Triple DES the result is always different, but will be 16 bytes longer..."
    keydata = Cnv.fromhex(
        "84e7f2d8 78f89fcc cd2d5eba fc56daf7 3300f27e f771cd68")
    kek = Cnv.fromhex("8ad8274e 56f46773 8edd83d4 394e5e29 af7c4089 e4f8d9f4")
    wk = Cipher.key_wrap(keydata, kek, Cipher.Alg.TDEA)
    print "WK=", Cnv.tohex(wk)
    assert len(wk) == len(keydata) + 16

    # Unwrap
    k = Cipher.key_unwrap(wk, kek, Cipher.Alg.TDEA)
    print "UNWRAPPED K=", Cnv.tohex(k)
    assert(k == keydata)


def test_cipher_pad():
    print "\nTEST CIPHER PAD...."

    data = Cnv.fromhex('FFFFFFFFFF')
    print "Input data :", Cnv.tohex(data)
    padded = Cipher.pad(data, Cipher.Alg.TDEA)
    print "Padded data:", Cnv.tohex(padded)
    unpadded = Cipher.unpad(padded, Cipher.Alg.TDEA)
    print "Unpadded   :", Cnv.tohex(unpadded)
    padded = Cipher.pad(data, Cipher.Alg.TDEA,
                        Cipher.Pad.ONEANDZEROES)
    print "Padded data:", Cnv.tohex(padded)
    unpadded = Cipher.unpad(padded, Cipher.Alg.TDEA,
                            Cipher.Pad.ONEANDZEROES)
    print "Unpadded   :", Cnv.tohex(unpadded)

    # Pad the empty string
    data = Cnv.fromhex('')
    print "Input data :", Cnv.tohex(data)
    padded = Cipher.pad(data, Cipher.Alg.AES128)
    print "Padded data:", Cnv.tohex(padded)
    unpadded = Cipher.unpad(padded, Cipher.Alg.AES128)
    print "Unpadded   :", Cnv.tohex(unpadded)
    # Pass data as hex strings
    datahex = 'aaaaaa'
    print "Input data :", datahex
    paddedhex = Cipher.pad_hex(datahex, Cipher.Alg.TDEA)
    print "Padded data:", paddedhex
    unpaddedhex = Cipher.unpad_hex(paddedhex, Cipher.Alg.TDEA)
    print "Unpadded   :", unpaddedhex
    paddedhex = Cipher.pad_hex(
        datahex, Cipher.Alg.TDEA, Cipher.Pad.ONEANDZEROES)
    print "Padded data:", paddedhex
    unpaddedhex = Cipher.unpad_hex(
        paddedhex, Cipher.Alg.TDEA, Cipher.Pad.ONEANDZEROES)
    print "Unpadded   :", unpaddedhex


def test_rsa_makekeys():
    print "\nTEST RSA KEY FUNCTIONS...."
    print "Making a new 512-bit RSA key pair..."
    rsaprikeyfile = "myrsaprivate.p8"
    rsapubkeyfile = "myrsapublic.p1"
    # We use 512 bits here for speed. In practice 512 bits is insecure. Use at
    # least 1024
    r = Rsa.make_keys(rsapubkeyfile, rsaprikeyfile, 512,
                      Rsa.PublicExponent.RSAEXP_EQ_65537, 'password')
    assert(0 == r)

    # Read from new key file into an "internal" key string
    prikeystr = Rsa.read_private_key(rsaprikeyfile, 'password')
    # Internal key string should be treated as a "blob".
    print "prikeystr =", prikeystr
    assert(len(prikeystr) > 0)
    nbits = Rsa.key_bits(prikeystr)
    print "nbits = ", nbits
    assert(nbits > 0)
    print "hashcode =", Rsa.key_hashcode(prikeystr)

    pubkeystr = Rsa.read_public_key(rsapubkeyfile)
    print "pubkeystr =", pubkeystr
    assert(len(pubkeystr) > 0)
    nbits = Rsa.key_bits(pubkeystr)
    print "nbits = ", nbits
    assert(nbits > 0)
    print "hashcode =", Rsa.key_hashcode(pubkeystr)

    s = Rsa.key_value(pubkeystr, "Exponent")
    print "exponent in base64:", s
    s = Rsa.key_value(pubkeystr, "MODULUS")
    print "modulus in base64:", s

    # Create an XML representation of the internal string - force values in
    # non-standard hex
    s = Rsa.to_xmlstring(pubkeystr, Rsa.XmlOptions.HEXBINARY)
    print "xml (hex):", s

    # Again using standard default base64 values
    s = Rsa.to_xmlstring(pubkeystr)
    print "xml:", s

    # Go back from XML string to a new internal string (this will not be the
    # same as before)
    s = Rsa.from_xmlstring(s)
    print "new keystr:", s
    # But should have the same key hashcode
    print "hashcode =", Rsa.key_hashcode(s)


def test_rsa_errors():
    print "\nTry to use an invalid keystr..."
    try:
        Rsa.key_hashcode('')
    except PKIError as e:
        print "(Expected) PKIError:", e


def test_rsa_savekeys():
    print "\nTEST READING RSA KEYS THEN RE-SAVING IN DIFFERENT FORMAT...."
    # Read in a private key
    fname = "AlicePrivRSASign.p8"
    print "FILE:", fname
    prikeystr = Rsa.read_private_key(fname, "password")
    print "KeyBits:", Rsa.key_bits(prikeystr)
    print "KeyIsPrivate:", Rsa.key_isprivate(prikeystr)
    print "KeyHashCode:", Rsa.key_hashcode(prikeystr)

    print "Save with stronger encryption..."
    fname = "alice-stronger.p8"
    Rsa.save_enc_key(fname, prikeystr, "password123",  # Note stronger password here :-)
                     pbescheme=Rsa.PbeScheme.PBKDF2_AES128, count=5999, fileformat=Rsa.Format.PEM)
    # _dump_and_print_asn1(fname)
    print "FILE:", fname, "-->", Asn1.type(fname)
    # Check we can read and that key is the same
    keystrchk = Rsa.read_private_key(fname, "password123")
    print "KeyHashCode:", Rsa.key_hashcode(keystrchk)
    assert(Rsa.key_hashcode(keystrchk) == Rsa.key_hashcode(prikeystr))

    print "Save without encryption..."
    fname = "alice-noencrypt.p8"
    Rsa.save_key(fname, prikeystr)
    print "FILE:", fname, "-->", Asn1.type(fname)
    # Check we can read and that key is the same
    keystrchk = Rsa.read_private_key(fname)
    print "KeyHashCode:", Rsa.key_hashcode(keystrchk)
    assert(Rsa.key_hashcode(keystrchk) == Rsa.key_hashcode(prikeystr))

    print "Convert private key string to a public key..."
    pubkeystr = Rsa.publickey_from_private(prikeystr)
    print "KeyBits:", Rsa.key_bits(pubkeystr)
    print "KeyIsPrivate:", Rsa.key_isprivate(pubkeystr)
    print "KeyHashCode:", Rsa.key_hashcode(pubkeystr)

    print "Check the public and private key strings are matched..."
    ismatch = Rsa.key_match(prikeystr, pubkeystr)
    print "Rsa.key_match() returns", ismatch
    assert(ismatch)

    print "Save to a new file in Open-SSL format..."
    fname = "alice-ssl.pub"
    Rsa.save_key(fname, pubkeystr, fileformat=Rsa.Format.SSL)
    print "FILE:", fname, "-->", Asn1.type(fname)
    # Check we can read and that key is the same
    keystrchk = Rsa.read_public_key(fname)
    print "KeyHashCode:", Rsa.key_hashcode(keystrchk)
    assert(Rsa.key_hashcode(keystrchk) == Rsa.key_hashcode(pubkeystr))


def test_rsa_sign():
    print "\nTEST RSA SIGN...."
    print "Sign in two parts: encode then do raw RSA with private key..."
    # See also Sig.sign() for a cleaner way

    # Read in a private key
    prikeystr = Rsa.read_private_key("AlicePrivRSASign.p8", "password")
    print prikeystr
    message = 'abc'
    # We need the length of the RSA key modulus in bytes
    keybytes = Rsa.key_bytes(prikeystr)
    print "KEYBYTES =", keybytes
    # 1. Encode the message in a block of the correct size
    #    -- this computes the message digest value automatically
    b = Rsa.encode_msg_for_signature(keybytes, message)
    print "BLK=[" + Cnv.tohex(b) + "]"
    # 2. Encrypt the block using "raw" RSA transform
    sig = Rsa.raw_private(b, prikeystr)
    print "SIG=[" + Cnv.tohex(sig) + "]"

    # To verify the signature we read in the public key
    pubkeystr = Rsa.read_public_key("AliceRSASignByCarl.cer")
    print pubkeystr
    # 1. Decrypt the signature to a block using "raw" RSA transform
    blk = Rsa.raw_public(sig, pubkeystr)
    print "BLK=[" + Cnv.tohex(blk) + "]"

    # 2a. Decode to extract the full digestinfo
    #     -- normally we don't do this, but we test it here
    dig = Rsa.decode_digest_for_signature(blk, True)
    print "DIGINFO=[" + Cnv.tohex(dig) + "]"

    # 2b. Decode to extract the digest
    dig = Rsa.decode_digest_for_signature(blk)
    print "DIG=[" + Cnv.tohex(dig) + "]"

    # Check we got a match
    digvalue = Hash.data('abc')
    print "SHA1('abc')=", Cnv.tohex(digvalue)
    assert(dig == digvalue)

    print "Do again but start with digest value, and use SHA-256..."
    digvalue = Hash.data('abc', Hash.Alg.SHA256)
    print "SHA256('abc')=", Cnv.tohex(digvalue)
    b = Rsa.encode_msg_for_signature(
        keybytes, digvalue, hashalg=Hash.Alg.SHA256, digest_only=True)
    print "BLK=[" + Cnv.tohex(b) + "]"
    sig = Rsa.raw_private(b, prikeystr)
    print "SIG=[" + Cnv.tohex(sig) + "]"
    print "BLK=[" + Cnv.tohex(b) + "]"
    # decode to extract the digest
    dig = Rsa.decode_digest_for_signature(b)
    print "DIG=[" + Cnv.tohex(dig) + "]"


def test_rsa_encrypt():
    print "\nTEST RSA ENCRYPT...."
    print "Encrypt in two parts: encode then do raw RSA with public key..."

    message = 'Hi Bob.'     # Note usually we use RSA to encrypt a session key.
    print "MSG:", message
    # Read in Bob's public key
    pubkeystr = Rsa.read_public_key("BobRSASignByCarl.cer")
    print pubkeystr

    # We need the length of the RSA key modulus in bytes
    keybytes = Rsa.key_bytes(pubkeystr)
    print "KEYBYTES =", keybytes
    blk = Rsa.encode_msg_for_encryption(keybytes, message)
    print "BLK=[" + Cnv.tohex(blk) + "]"

    ct = Rsa.raw_public(blk, pubkeystr)
    print "Note that the ciphertext block will be different each time..."
    print "CT =[" + Cnv.tohex(ct) + "]"

    print "Decrypt in two parts: do raw RSA with private key then decode..."
    # Read in a private key
    prikeystr = Rsa.read_private_key("BobPrivRSAEncrypt.p8", "password")
    print prikeystr
    blk = Rsa.raw_private(ct, prikeystr)
    print "BLK=[" + Cnv.tohex(blk) + "]"
    pt = Rsa.decode_msg_for_encryption(blk)
    print "PT =[" + Cnv.tohex(ct) + "]"
    # in this case we expect plain ASCII text
    print "PT='" + str(pt) + "'"
    assert (pt == message)

    print "Again using one-step encrypt() and decrypt() this time with OEAP method..."
    # Use key strings we read in above
    print "MSG:", message
    ct = Rsa.encrypt(message, pubkeystr, method=Rsa.EME.OAEP)
    print "CT =[" + Cnv.tohex(ct) + "]"
    pt = Rsa.decrypt(ct, prikeystr, method=Rsa.EME.OAEP)
    print "PT='" + str(pt) + "'"
    assert (pt == message)


def test_x509_generate():
    print "\nTEST X509 FUNCTIONS...."
    # For convenience we hard-code the password - DON'T DO THIS IN PRACTICE!
    mypassword = 'password'
    print "Make a self-signed X.509 certificate:"

    # Generate a new RSA key pair for the CA
    # (in practice, do this once)
    print "Generating a new RSA 1024-bit keypair for the CA..."
    ca_prikeyfile = 'thecaprikey.p8'
    ca_pubkeyfile = 'thecapubkey.p1'
    n = Rsa.make_keys(ca_pubkeyfile, ca_prikeyfile, 1024,
                      Rsa.PublicExponent.RSAEXP_EQ_65537, mypassword)
    assert(0 == n)
    assert(os.path.isfile(ca_prikeyfile))
    assert(os.path.isfile(ca_pubkeyfile))

    # Now use these to create a self-signed X.509 certificate (we only need
    # the private key file)
    ca_certfile = 'theca.cer'
    n = X509.make_cert_self(ca_certfile, ca_prikeyfile,
                            mypassword, 0x01, 5, "C=AU;CN=theCA")
    print "X509.make_cert_self() returns:", n
    assert (0 == n)
    assert(os.path.isfile(ca_certfile))
    print "Created new self-signed X.509 certificate '" + ca_certfile + "'"
    # Show its contents...
    _dump_and_print_x509(ca_certfile)

    # Generate a new RSA key pair for the user
    # (in practice, do this once)
    print "Generating a new RSA 512-bit keypair for the USER..."
    user_prikeyfile = 'myuserprikey.p8'
    user_pubkeyfile = 'myuserpubkey.p1'
    n = Rsa.make_keys(user_pubkeyfile, user_prikeyfile, 512,
                      Rsa.PublicExponent.RSAEXP_EQ_65537, mypassword)
    assert(0 == n)
    assert(os.path.isfile(ca_prikeyfile))
    assert(os.path.isfile(ca_pubkeyfile))

    # Use the user's public key as the subject of an X.509 cert issued by the
    # CA
    my_certfile = 'mycert.cer'
    n = X509.make_cert(my_certfile, ca_certfile, user_pubkeyfile, ca_prikeyfile, mypassword, 0x101, 3, "C=AU;CN=me",
                       extns="rfc822name=me@myorg.com;keyusage=digitalSignature,nonRepudiation;")
    print "X509.make_cert() returns:", n
    assert (0 == n)
    assert(os.path.isfile(my_certfile))
    print "Created X.509 certificate '" + my_certfile + "'"
    _dump_and_print_x509(my_certfile)

    # Create a Certificate Signing Request for the user
    my_csrfile = 'mycsr.p10'
    n = X509.cert_request(my_csrfile, user_prikeyfile, mypassword, "C=AU;CN=me;O=myorg",
                          extns="rfc822name=me.again@myorg.com;keyusage=dataEncipherment,keyAgreement;ipaddress=127.0.0.1")
    print "X509.cert_request() returns:", n
    assert (0 == n)
    assert(os.path.isfile(my_csrfile))
    print "Created PKCS#10 certificate signing request '" + my_csrfile + "'"
    _dump_and_print_x509(my_csrfile)

    # Now use this CSR to create another X.509 cert issued by the CA
    # -- set `distname = ""` and pass the CSR file in the `subject_pubkeyfile` parameter
    my_certfilefromcsr = 'mycertfromcsr.cer'
    n = X509.make_cert(my_certfilefromcsr, ca_certfile, my_csrfile, ca_prikeyfile, mypassword, 0x102, 2, "",
                       sigalg=X509.SigAlg.SHA256RSA)
    print "X509.make_cert() returns:", n
    assert (0 == n)
    assert(os.path.isfile(my_certfilefromcsr))
    print "Created X.509 certificate '" + my_certfilefromcsr + "'"
    _dump_and_print_x509(my_certfilefromcsr)

    print "Check the keyUsage flags..."
    n = X509.key_usage_flags(my_certfilefromcsr)
    print "keyUsage bits: n =", format(n, "#08b")
    mask = X509.KeyUsageFlags.DATAENCIPHERMENT
    print "n & KeyUsageFlags.DATAENCIPHERMENT =", bool(n & mask)
    mask = X509.KeyUsageFlags.KEYAGREEMENT
    print "n & KeyUsageFlags.KEYAGREEMENT =", bool(n & mask)
    mask = X509.KeyUsageFlags.CRLSIGN
    print "n & KeyUsageFlags.CRLSIGN =", bool(n & mask)

    # Create a Certificate Revocation List (CRL) revoking the cert made above with serial number 0x101
    # (Dates need to be hardcoded)
    ca_crlfile = 'theca.crl'
    revokedcertlist = "#x101,2020-04-25"
    n = X509.make_crl(ca_crlfile, ca_certfile, ca_prikeyfile, mypassword, revokedcertlist,
                      extns="thisUpdate=2020-04-25T00:01;nextUpdate=2020-12-31",
                      sigalg=X509.SigAlg.SHA256RSA,
                      opts=X509.Opts.FORMAT_PEM)
    print "X509.make_crl() returns:", n
    assert (0 == n)
    assert(os.path.isfile(ca_crlfile))
    print "Created CRL file '" + ca_crlfile + "'"
    _dump_and_print_x509(ca_crlfile)

    # Query the certificates we made above
    fname = ca_certfile
    query = 'subjectName'
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + fname + ", " + query + "):", res

    query = 'isCA'
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + fname + ", " + query + "):", res

    fname = my_certfile
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + fname + ", " + query + "):", res

    fname = my_certfilefromcsr
    query = 'keyUsageString'
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + fname + ", " + query + "):", res

    print "\nTry an invalid query string..."
    try:
        res = X509.query_cert(fname, 'badquery')
    except PKIError as e:
        print "(Expected) PKIError:", e

    print "\nSee if our certificates have been revoked at any time..."
    # This cert has not been revoked
    fname = my_certfilefromcsr
    isrevoked = X509.cert_is_revoked(fname, ca_crlfile)
    print "X509.cert_is_revoked('" + fname + "') returns", isrevoked
    assert(not isrevoked)

    # This cert was revoked on 2020-04-25 (yes, we can work in the future!)
    fname = my_certfile
    isrevoked = X509.cert_is_revoked(fname, ca_crlfile)
    print "X509.cert_is_revoked('" + fname + "') returns", isrevoked
    assert(isrevoked)

    print "See if certificate was revoked on a certain date..."
    fname = my_certfile
    isodate = "2016-01-01"
    isrevoked = X509.cert_is_revoked(fname, ca_crlfile, isodate=isodate)
    print "X509.cert_is_revoked('" + fname + ", " + isodate + "') returns", isrevoked
    assert(not isrevoked)

    print "\nRead in X.509 cert as a base64 string"
    s = X509.read_string_from_file(my_certfile)
    print s
    print "Now save from this string to a new file in PEM textual format..."
    fname = 'newcert.cer'
    n = X509.save_file_from_string(fname, s, in_pem_format=True)
    print "Created new cert file '" + fname + "'"
    assert(os.path.isfile(fname))
    _dump_file(fname)

    print "\nCheck if certs are valid now..."
    fname = 'AliceRSASignByCarl.cer'
    print "FILE:", fname
    isvalid = X509.cert_is_valid_now(fname)
    s = X509.query_cert(fname, "NotAfter")
    print s

    print "X509.cert_is_valid_now('" + fname + "')=", isvalid
    assert(isvalid)  # CAUTION: will not work after year 2039!
    fname = 'dims.cer'
    isvalid = X509.cert_is_valid_now(fname)
    print "X509.cert_is_valid_now('" + fname + "')=", isvalid
    assert(not isvalid)

    print "\nCompute cert thumbprints..."
    fname = 'AliceRSASignByCarl.cer'
    print "FILE:", fname
    thumb = X509.cert_thumb(fname)
    print "X509.cert_thumb(SHA-1):", thumb
    assert(thumb == 'b30c48855055c2e64ce3196492d4b83831a6b3cb')

    thumb = X509.cert_thumb(fname, X509.HashAlg.SHA256)
    print "X509.cert_thumb(SHA-256):", thumb


def test_x509_analyze():
    print "\nTESTING X.509 ANALYZE..."

    fname = 'AliceRSASignByCarl.cer'
    print "FILE:", fname
    query = "serialNumber"
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + query + "):", res
    print "Use `opts=X509.Opts.DECIMAL`..."
    res = X509.query_cert(fname, query, opts=X509.Opts.DECIMAL)
    print "X509.query_cert(" + query + "):", res
    h = X509.cert_thumb(fname)
    print "cert_thumb():", h
    h = X509.cert_hashissuersn(fname)
    print "hash(issuer+serialnumber):", h

    fname = 'dims.cer'
    print "FILE:", fname
    query = "issuerName"
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + query + "):", res
    print "Use `opts=X509.Opts.LDAP`..."
    res = X509.query_cert(fname, query, opts=X509.Opts.LDAP)
    print "X509.query_cert(" + query + "):", res

    fname = 'smallca.cer'
    print "FILE:", fname
    query = "notAfter"
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + query + "):", res
    query = "cRLDistributionPointsURI"
    res = X509.query_cert(fname, query)
    print "X509.query_cert(" + query + "):", res

    # Extract the public key from the X.509 cert
    keystr = Rsa.read_public_key(fname)
    print "Public key bits:", Rsa.key_bits(keystr)
    hcode = Rsa.key_hashcode(keystr)
    print "Rsa.key_hashcode():", hcode
    h = X509.cert_thumb(fname, X509.HashAlg.MD5)
    print "X509.cert_thumb(MD5):", h
    h = X509.cert_hashissuersn(fname)
    print "hash(issuer+serialnumber):", h


def test_x509_validate():
    print "\nTESTING X.509 VALIDATE..."

    print "1. A valid certificate and its issuer:"
    certfile = "AliceRSASignByCarl.cer"
    issuerfile = "CarlRSASelf.cer"
    print "CERTFILE:", certfile
    print "ISSUERFILE:", issuerfile

    print "Is cert valid now?"
    isok = X509.cert_is_valid_now(certfile)
    print "cert_is_valid_now:", isok
    # This will fail in the year 2040 :-)
    assert(isok)

    print "Was cert signed by issuer?"
    isok = X509.cert_is_verified(certfile, issuerfile)
    print "cert_is_verified:", isok
    assert(isok)

    print "Validate the certificate path..."
    certlist = certfile + ";" + issuerfile
    print "CERTLIST:", certlist
    isok = X509.cert_path_is_valid(certlist)
    print "cert_path_is_valid:", isok
    assert(isok)

    print "2. A valid but expired certificate and its issuer:"
    certfile = "dims.cer"
    issuerfile = "UTNUSERFirst-Object.cer"
    print "CERTFILE:", certfile
    print "ISSUERFILE:", issuerfile

    print "Is cert valid now?"
    d = X509.query_cert(certfile, "notAfter")
    print "  X509.query_cert('notAfter'):", d
    isok = X509.cert_is_valid_now(certfile)
    print "cert_is_valid_now:", isok, "(expected False)"
    # This will fail if you go back in time to before Nov 2011 :-)
    assert(not isok)

    print "Was cert signed by issuer?"
    isok = X509.cert_is_verified(certfile, issuerfile)
    print "cert_is_verified:", isok
    assert(isok)

    print "Validate the certificate path..."
    certlist = certfile + ";" + issuerfile
    print "CERTLIST:", certlist

    print "a) This will fail because a cert has expired..."
    try:
        isok = X509.cert_path_is_valid(certlist)
    except PKIError as e:
        print "(Expected):", e

    print "b) Now try again with X509.Opts.NO_TIMECHECK..."
    isok = X509.cert_path_is_valid(certlist, no_timecheck=True)
    print "cert_path_is_valid(NO_TIMECHECK):", isok

    print "3. A valid certificate but the wrong issuer:"
    certfile = "AliceRSASignByCarl.cer"
    issuerfile = "UTNUSERFirst-Object.cer"
    print "CERTFILE:", certfile
    print "ISSUERFILE:", issuerfile

    print "Was cert signed by issuer?"
    isok = X509.cert_is_verified(certfile, issuerfile)
    print "cert_is_verified:", isok, "(expected False)"
    assert(not isok)


def test_x509_extract():
    print "\nTESTING X.509 EXTRACT..."

    print "Extract cert files from a P7 chain file"
    p7file = "bob.p7b"
    print "P7 FILE:", p7file
    n = X509.get_cert_count_from_p7(p7file)
    print "X509.get_cert_count_from_p7()=", n
    assert(n > 0)
    # Extract each cer file from p7 file
    for i in range(1, n + 1):
        print "Count:", i
        fname = "bobcert" + str(i) + ".cer"
        print " OUTFILE:", fname
        r = X509.get_cert_from_p7(fname, p7file, i)
        print " X509.get_cert_from_p7() returns:", r
        assert (r > 0)
        print " X509_thumb():", X509.cert_thumb(fname)

    print "Extract cert files from a PFX (p12) file"
    pfxfile = "alice.pfx"
    print "PFX FILE:", pfxfile
    fname = 'alice_cert.cer'
    print " OUTFILE:", fname
    r = X509.get_cert_from_pfx(fname, pfxfile, "password")
    assert (r > 0)
    print " ASN1 TYPE(" + fname + ")=" + Asn1.type(fname)
    print " X509_thumb():", X509.cert_thumb(fname)
    # Show thumbprints of known certificate files...
    print "X509_thumb(Carl): ", X509.cert_thumb("CarlRSASelf.cer")
    print "X509_thumb(Alice):", X509.cert_thumb("AliceRSASignByCarl.cer")
    print "X509_thumb(Bob):  ", X509.cert_thumb("BobRSASignByCarl.cer")

    print "Extract all cert files as P7 chain from a PFX file"
    pfxfile = "alice.pfx"
    print "PFX FILE:", pfxfile
    fname = 'alice_certs.p7'
    print " OUTFILE:", fname
    r = X509.get_p7chain_from_pfx(fname, pfxfile, "password")
    assert (r > 0)
    print " ASN1 TYPE(" + fname + ")=" + Asn1.type(fname)


def test_rng():
    print "\nTESTING RANDOM NUMBER GENERATOR..."

    # Initialize from seed file. File is created if it does not exist.
    # Optional but recommended for extra security
    seedfile = 'myseedfile.dat'
    n = Rng.initialize(seedfile)
    assert(0 == n)
    print 'Rng.initialize() returns', n, ". Contents of seed file:"
    sd = read_binary_file(seedfile)
    print Cnv.tohex(sd)
    assert(len(sd) == Rng.SEED_BYTES)

    print "5 random byte arrays"
    for i in range(5):
        b = Rng.bytestring((i + 2) * 2)
        print Cnv.tohex(b).lower()

    print "5 random numbers in the range [-1 million, +1 million]"
    for i in range(5):
        r = Rng.number(-1000000, 1000000)
        print r
        assert(-1000000 <= r and r <= 1000000)

    print "5 random octet values"
    s = ""  # fudge to do in one line
    for i in range(5):
        r = Rng.octet()
        assert(0 <= r and r <= 255)
        s += str(r) + " "
    print s

    # Update seedfile
    n = Rng.update_seedfile(seedfile)
    assert(0 == n)
    print 'Rng.update_seedfile() returns', n, ". Contents of seed file:"
    sd = read_binary_file(seedfile)
    print Cnv.tohex(sd)
    assert(len(sd) == Rng.SEED_BYTES)


def test_hash():
    print "\nTESTING HASH..."
    # write a file containing the 3 bytes 'abc'
    write_file('abc.txt', 'abc')
    _dump_file('abc.txt')
    abc_hex = Cnv.tohex('abc')
    print "'abc' in hex:", abc_hex

    # Use default SHA-1 algorithm
    print "Using default SHA-1..."
    b = Hash.data('abc')
    print "Hash.data('abc'):", Cnv.tohex(b)
    h = Hash.hex_from_data('abc')
    print "Hash.hex_from_data('abc'):", h
    h = Hash.hex_from_data(bytearray.fromhex('616263'))
    print "Hash.hex_from_data('abc'):", h
    h = Hash.hex_from_hex(abc_hex)
    print "Hash.hex_from_hex(abc_hex):", h
    b = Hash.file('abc.txt')
    print "Hash.file('abc.txt'):", Cnv.tohex(b)
    h = Hash.hex_from_file('abc.txt')
    print "Hash.hex_from_file('abc.txt'):", h

    print "Using SHA-256..."
    b = Hash.data('abc', Hash.Alg.SHA256)
    print "Hash.data('abc'):", Cnv.tohex(b)
    h = Hash.hex_from_hex(abc_hex, Hash.Alg.SHA256)
    print "Hash.hex_from_hex(abc_hex):", h
    b = Hash.file('abc.txt', Hash.Alg.SHA256)
    print "Hash.file('abc.txt'):", Cnv.tohex(b)
    h = Hash.hex_from_file('abc.txt', Hash.Alg.SHA256)
    print "Hash.hex_from_file('abc.txt'):", h

    # compute SHA256(SHA256('abc')) using Hash.double()
    b = Hash.double('abc', Hash.Alg.SHA256)
    print "Hash.double('abc',SHA256):", Cnv.tohex(b)
    # and again by composition
    b2 = Hash.data(Hash.data('abc', Hash.Alg.SHA256),
                   Hash.Alg.SHA256)
    print "SHA256(SHA256('abc')):    ", Cnv.tohex(b2)


def test_hmac():
    print "\nTESTING HMAC..."
    print "Test case 4 from RFC 2202 and RFC 4231"
    key = Cnv.fromhex('0102030405060708090a0b0c0d0e0f10111213141516171819')
    print "key: ", Cnv.tohex(key)
    # data = 0xcd repeated 50 times
    data = bytearray([0xcd] * 50)
    print "data:", Cnv.tohex(data)

    b = Hmac.data(data, key)
    print "HMAC-SHA-1:  ", Cnv.tohex(b)
    assert(b == Cnv.fromhex('4c9007f4026250c6bc8414f9bf50c86c2d7235da'))

    b = Hmac.data(data, key, Hmac.Alg.MD5)
    print "HMAC-MD5:    ", Cnv.tohex(b)
    assert(b == Cnv.fromhex('697eaf0aca3a3aea3a75164746ffaa79'))

    b = Hmac.data(data, key, Hmac.Alg.SHA256)
    print "HMAC-SHA-256:", Cnv.tohex(b)
    assert(b == Cnv.fromhex(
        '82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b'))

    h = Hmac.hex_from_data(data, key, Hmac.Alg.SHA256)
    print "HMAC-SHA-256:", h
    assert(h == '82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b')

    b = Hmac.data(data, key, Hmac.Alg.SHA512)
    print "HMAC-SHA-512:", Cnv.tohex(b)
    assert(b == Cnv.fromhex(
        'b0ba465637458c6990e5a8c5f61d4af7 e576d97ff94b872de76f8050361ee3db a91ca5c11aa25eb4d679275cc5788063 a5f19741120c4f2de2adebeb10a298dd'))

    print "Test case 7 from RFC 4231"
    key = bytearray([0xaa] * 131)
    print "key: ", Cnv.tohex(key).lower()
    data = "This is a test using a larger than block-size key and a larger than block-size data. The key needs to be hashed before being used by the HMAC algorithm."
    print "data:", data
    b = Hmac.data(data, key, Hmac.Alg.SHA224)
    print "HMAC-SHA-224:", Cnv.tohex(b)
    assert(b == Cnv.fromhex(
        '3a854166ac5d9f023f54d517d0b39dbd946770db9c2b95c9f6f565d1'))

    # HMAC hex <-- hex
    print "Test case 1 from RFC 2202 and RFC 4231"
    keyhex = "0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b"  # (20 bytes)
    datahex = "4869205468657265"    # ("Hi There")
    print "key: ", keyhex
    print "data:", datahex, '("' + Cnv.fromhex(datahex) + '")'
    h = Hmac.hex_from_hex(datahex, keyhex)
    print "HMAC-SHA-1:", h
    assert(h == "b617318655057264e28bc0b6fb378c8ef146be00")
    h = Hmac.hex_from_hex(datahex, keyhex, Hmac.Alg.SHA256)
    print "HMAC-SHA-256:", h
    assert(h == "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7")


def test_wipe():
    print "\nTESTING WIPE..."

    print "Note that Wipe.data() just zeroizes the data, it does not change the length"

    b = Cnv.fromhex('3a854166ac5d9f023f54d517d0b39dbd946770db9c2b95c9f6f565d1')
    print "BEFORE            b=", Cnv.tohex(b)
    Wipe.data(b)
    print "AFTER Wipe.data() b=", Cnv.tohex(b)
    print [ord(c) for c in b]
    assert all([ord(c) == 0 for c in b])

    s = "a string"
    print "BEFORE            s='" + s + "'"
    print [ord(c) for c in s]
    Wipe.data(s)
    print "AFTER Wipe.data() s='" + s + "'"
    print [ord(c) for c in s]
    assert all([ord(c) == 0 for c in s])

    # write a file containing some text
    fname = 'tobedeleted.txt'
    write_file(fname, 'Some secret text in this file.')
    _dump_file(fname)
    assert(os.path.isfile(fname))
    Wipe.file(fname)
    print "After Wipe.file(), isfile() returns",  os.path.isfile(fname)
    assert(not os.path.isfile(fname))


def test_asn1():
    print "\nTESTING ASN.1..."
    fname = "smallca.cer"
    print "FILE:", fname
    t = Asn1.type(fname)
    print "Asn1.type():", t
    dumpfile = 'asn1dump.txt'
    Asn1.text_dump(dumpfile, fname, opts=Asn1.Opts.ADDLEVELS)
    print "Asn1.text_dump():"
    _print_file(dumpfile)


def test_ocsp():
    print "\nTESTING OCSP..."
    # Create an OCSP request to check a code-signing certificate issued by the holder
    # of certificate in the file `UTNUSERFirst-Object.cer`
    issuercert = "UTNUSERFirst-Object.cer"
    print "Issuer Cert=", issuercert
    certfile = "dims.cer"
    print "Cert File to check=", certfile
    req = Ocsp.make_request(issuercert, certfile)
    print "OCSPRequest=", req
    assert len(req) > 0
    # We can analyze the ASN.1 data structure from the base64 string
    _dump_and_print_asn1(req)

    # Pass a hex serial number instead of filename
    serialnum = "#x 00 FB C7 23 22 8C 8C 80 22 D8 85 92 23 DE E7 06 60"
    print "Cert SerialNumber=", serialnum
    req1 = Ocsp.make_request(issuercert, serialnum)
    print "OCSPRequest=", req1
    # These should be the same
    assert (req1 == req)

    # Now read a response
    responsefile = "ocsp_response_ok_dims.dat"
    print "ResponseFile=", responsefile
    resp = Ocsp.read_response(responsefile, issuercert)
    print "OCSPResponse:", resp


def test_ecc():
    print "\nTESTING ECC..."
    pubkeyfile = "myeckeyp256.pub"
    prikeyfile = "myeckeyp256.p8"
    password = "password"
    curvename = "P-256"
    # Create a new pair of ECC keys, saved as DER-encoded files
    n = Ecc.make_keys(pubkeyfile, prikeyfile, curvename, password)
    assert(0 == n)
    _dump_and_print_asn1(pubkeyfile)
    print pubkeyfile + ": " + Asn1.type(pubkeyfile)
    print prikeyfile + ": " + Asn1.type(prikeyfile)

    # Read in private key to an internal key string
    intpristr = Ecc.read_private_key(prikeyfile, password)
    # This will be different each time, even for the same key
    print intpristr
    # But the key hash code will be the same
    print "key_hash_code=" + Ecc.key_hashcode(intpristr)

    # Query this string for info
    query = "keyBits"
    r = Ecc.query_key(intpristr, query)
    print "Ecc.query_key(" + query + ")=", r
    query = "curveName"
    r = Ecc.query_key(intpristr, query)
    print "Ecc.query_key(" + query + ")=", r
    query = "privateKey"
    r = Ecc.query_key(intpristr, query)
    print "Ecc.query_key(" + query + ")=", r

    # Read in a key from its hex representation
    print "A NIST P-192 public key in X9.63 uncompressed format"
    keyhex = "0496C248BE456192FA1380CCF615D171452F41FF31B92BA733524FD77168DEA4425A3EA8FD79B98DC7AFE83C86DCC39A96"
    curvename = "prime192v1"    # A synonym for "P-192"
    print "KEYHEX:", keyhex
    print "CURVE: ", curvename
    intpubstr = Ecc.read_key_by_curve(keyhex, curvename)
    print "keyBits=", Ecc.query_key(intpubstr, "keyBits")
    f = Ecc.query_key(intpubstr, "isPrivate")
    print "isPrivate=", f
    assert(not f)

    print "A Bitcoin private key in base58 form"
    keyb58 = "6ACCbmy9qwiFcuVgvxNNwMPfoghobzznWrLs3v7t3RmN"
    curvename = "secp256k1"
    print "KEYB58:", keyb58
    print "CURVE: ", curvename
    intpristr = Ecc.read_key_by_curve(
        Cnv.tohex(Cnv.frombase58(keyb58)), curvename)
    print "keyBits=", Ecc.query_key(intpristr, "keyBits")
    f = Ecc.query_key(intpristr, "isPrivate")
    print "isPrivate=", f
    assert(f)
    print "key_hash_code=" + Ecc.key_hashcode(intpristr)

    print "Extract the public key in hex form from the internal private key string"
    pubkey = Ecc.query_key(intpristr, 'publicKey')
    print "publicKey=", pubkey
    assert pubkey == '04654bacc2fc7a3bde0f8eb95dc5aac9ba1df732255cf7f2eb7e1e8e6edbb1f4188ff3752ac4bdf1e3a31a488747745dddcbabd33a10c3b52d737c092851da13c0'

    print "Extract the public key as an internal key string"
    intpubstr = Ecc.publickey_from_private(intpristr)
    print "intpubstr=", intpubstr
    print "key_hash_code=" + Ecc.key_hashcode(intpubstr)

    print "Query this internal public key string..."
    query = "keybits"
    print "Ecc.query_key(" + query + ")=", Ecc.query_key(intpubstr, query)
    query = "curvename"
    print "Ecc.query_key(" + query + ")=", Ecc.query_key(intpubstr, query)
    query = "isPrivate"
    print "Ecc.query_key(" + query + ")=", Ecc.query_key(intpubstr, query)

    print "Save keys in various new file forms..."
    # Note we must save from the internal key string forms
    # Default unencrypted key files...
    newkeyfile = 'myecpublic.key'
    n = Ecc.save_key(newkeyfile, intpubstr)
    # Show what type of file we made
    print "File:", newkeyfile, "-->", Asn1.type(newkeyfile)
    # and read it back in to check it's really OK...
    s = Ecc.read_public_key(newkeyfile)
    assert(Ecc.query_key(s, 'keyBits') == 256)

    newkeyfile = 'myecprivate.key'
    n = Ecc.save_key(newkeyfile, intpristr)
    print "File:", newkeyfile, "-->", Asn1.type(newkeyfile)
    s = Ecc.read_private_key(newkeyfile)
    assert(Ecc.query_key(s, 'keyBits') == 256)

    # Alternative PKCS#8 key type (unencrypted)
    newkeyfile = 'myecprivate.p8'
    n = Ecc.save_key(newkeyfile, intpristr,
                     keytype=Ecc.KeyType.PKCS8, fileformat=Ecc.Format.PEM)
    print "File:", newkeyfile, "-->", Asn1.type(newkeyfile)
    s = Ecc.read_private_key(newkeyfile)
    assert(Ecc.query_key(s, 'keyBits') == 256)

    # Encrypted private key (always PKCS#8)
    newkeyfile = 'myecprivate_enc.p8'
    n = Ecc.save_enc_key(newkeyfile, intpristr, 'password')
    print "File:", newkeyfile, "-->", Asn1.type(newkeyfile)
    s = Ecc.read_private_key(newkeyfile, 'password')
    assert(Ecc.query_key(s, 'keyBits') == 256)

    # with stronger encryption
    newkeyfile = 'myecprivate_encx.p8'
    # TODO: prf does not work for ECC_SaveEncKey
    n = Ecc.save_enc_key(newkeyfile, intpristr, 'password',
                         pbescheme=Ecc.PbeScheme.PBKDF2_AES256,
                         params="count=5999;prf=hmacWithSHA256;")
    print "File:", newkeyfile, "-->", Asn1.type(newkeyfile)
    s = Ecc.read_private_key(newkeyfile, 'password')
    assert(Ecc.query_key(s, 'keyBits') == 256)
    # Dump this
    _dump_and_print_asn1(newkeyfile)


def test_pbe():
    print "\nTESTING PASSWORD-BASED ENCRYPTION (PBE)..."
    password = 'password'
    salt = Cnv.fromhex('78 57 8E 5A 5D 63 CB 06')
    count = 2048
    print "password = '" + password + "'"
    print "salt = 0x" + Cnv.tohex(salt)
    print "count =", count

    dklen = 24
    print "dklen =", dklen
    dk = Pbe.kdf2(dklen, password, salt, count)
    print "dk =", Cnv.tohex(dk)
    assert Cnv.tohex(dk) == "BFDE6BE94DF7E11DD409BCE20A0255EC327CB936FFE93643"

    # Same params but derive a longer key (CAUTION: never use the same salt in
    # practice)
    dklen = 64
    print "dklen =", dklen
    dk = Pbe.kdf2(dklen, password, salt, count)
    print "dk =", Cnv.tohex(dk)
    assert Cnv.tohex(dk) == \
        "BFDE6BE94DF7E11DD409BCE20A0255EC327CB936FFE93643C4B150DEF77511224479994567F2E9B4E3BD0DF7AEDA3022B1F26051D81505C794F8940C04DF1144"

    # Use different HMAC algorithms
    dklen = 24
    dk = Pbe.kdf2(dklen, password, salt, count, prfalg=Pbe.PrfAlg.HMAC_SHA1)
    print "dk(HMAC-SHA-1)   =", Cnv.tohex(dk)
    assert Cnv.tohex(dk) == "BFDE6BE94DF7E11DD409BCE20A0255EC327CB936FFE93643"
    dk = Pbe.kdf2(dklen, password, salt, count, prfalg=Pbe.PrfAlg.HMAC_SHA256)
    print "dk(HMAC-SHA-256) =", Cnv.tohex(dk)
    assert Cnv.tohex(dk) == "97B5A91D35AF542324881315C4F849E327C4707D1BC9D322"
    dk = Pbe.kdf2(dklen, password, salt, count, prfalg=Pbe.PrfAlg.HMAC_SHA224)
    print "dk(HMAC-SHA-224) =", Cnv.tohex(dk)
    assert Cnv.tohex(dk) == "10CFFEDFB13503519969151E466F587028E0720B387F9AEF"


def test_pfx():
    print "\nTESTING PFX (PKCS#12) FILE FUNCTIONS..."
    pfxfile = "bob1.pfx"
    certlist = "BobRSASignByCarl.cer"
    prikeyfile = "BobPrivRSAEncrypt.p8"
    n = Pfx.make_file(pfxfile, certlist, prikeyfile, 'password', "Bob's ID")
    assert(0 == n)
    print "Created new PKCS#12 file:", pfxfile
    print "Asn1.Type(" + pfxfile + ") -->", Asn1.type(pfxfile)

    print "Check signature is valid against password..."
    isvalid = Pfx.sig_is_valid(pfxfile, 'password')
    print "isvalid=", isvalid
    assert(isvalid)

    print "Use the wrong password..."
    isvalid = Pfx.sig_is_valid(pfxfile, 'passwordXXX')
    print "isvalid=", isvalid
    assert(not isvalid)


def test_pem():
    print "\nTESTING PEM/BINARY FILE CONVERSIONS..."
    binfile = "smallca.cer"
    pemfile = "smallca.pem"

    print "Create a PEM-format CERTIFICATE file from binary file..."
    print "Binary file:", binfile
    n = Pem.from_binfile(pemfile, binfile, "CERTIFICATE", Pem.EOL.UNIX)
    assert(0 == n)
    print "Created file:", pemfile
    print "Check certificate thumbprints..."
    thumb_bin = X509.cert_thumb(binfile)
    thumb_pem = X509.cert_thumb(pemfile)
    print "X509.cert_thumb(" + binfile + ")=" + thumb_bin
    print "X509.cert_thumb(" + pemfile + ")=" + thumb_pem
    assert(thumb_bin == thumb_pem)

    print "Convert PEM to binary..."
    binfile2 = "smallca-copy.bin"
    n = Pem.to_binfile(binfile2, pemfile)
    assert(0 == n)
    print "Created file:", binfile2
    print "Binary files should be identical..."
    hash_bin1 = Hash.hex_from_file(binfile)
    hash_bin2 = Hash.hex_from_file(binfile2)
    print "Hash.hex_from_file(" + binfile + ")=\t" + hash_bin1
    print "Hash.hex_from_file(" + binfile2 + ")=\t" + hash_bin2
    assert(hash_bin1 == hash_bin2)
    # Note that the *hash* of the PEM file is not the same as the hash of the binary,
    # but the X509.cert_thumb() is the same for both.


def test_cms_envdata():
    print "\nTESTING CMS ENV-DATA..."
    print "Creating an enveloped-data message for Bob and Carl, using file-->file mode"
    # Create a file
    mytext = 'This is some sample content.'
    myfile = "mycontent.txt"
    write_file(myfile, mytext)
    envdatafile = 'cms2bobandcarl.p7m'
    certlist = "BobRSASignByCarl.cer;CarlRSASelf.cer"
    n = Cms.make_envdata(envdatafile, myfile, certlist)
    print "Cms.make_envdata() returns " + str(n) + " (expected 2 = # of recipients)"
    assert(n > 0)
    _dump_and_print_asn1(envdatafile)
    print "Asn1.type('" + envdatafile + "')-->" + Asn1.type(envdatafile)

    # Query this CMS object file
    fname = envdatafile
    query = "recipientIssuerName"
    res = Cms.query_envdata(envdatafile, query)
    print "Cms.query_envdata(" + fname + ", " + query + "):", res
    query = "iv"
    res = Cms.query_envdata(envdatafile, query)
    print "Cms.query_envdata(" + fname + ", " + query + "):", res

    print "Bob reads the message, outputting to a new file"
    outputfile = "bobsdata.txt"
    # Bob reads in his private key to a secure "internal" key string
    prikeystr = Rsa.read_private_key('BobPrivRSAEncrypt.p8', 'password')
    n = Cms.read_envdata_to_file(outputfile, envdatafile, prikeystr)
    print "Cms.read_envdata_to_file() returns " + str(n) + " (expected 0)"
    assert(0 == n)
    _dump_file(outputfile)

    # Check we got the same as we started
    assert(read_text_file(outputfile) == mytext)

    print "\nDo the same but using string-->file mode..."
    print "DATA:", mytext
    envdatafile = 'cms2bobandcarl1.p7m'
    n = Cms.make_envdata_from_string(envdatafile, mytext, certlist)
    print "Cms.make_envdata_from_string() returns " + str(n) + " (expected 2 = # of recipients)"
    assert(n > 0)
    print "Asn1.type('" + envdatafile + "')-->" + Asn1.type(envdatafile)
    s = Cms.read_envdata_to_string(envdatafile, prikeystr)
    print s

    # clean up
    Wipe.data(prikeystr)
    prikeystr = None


def test_smime():
    print "\nTESTING S/MIME..."
    print "First create an enveloped-data message for Bob and Carl..."
    # Create a file
    mytext = 'This is some sample content.'
    myfile = "mycontent.txt"
    write_file(myfile, mytext)
    envdatafile = 'cms2bobandcarl.p7m'
    certlist = "BobRSASignByCarl.cer;CarlRSASelf.cer"
    n = Cms.make_envdata(envdatafile, myfile, certlist)
    print "Cms.make_envdata() returns " + str(n) + " (expected 2 = # of recipients)"
    assert(n > 0)
    print "Asn1.type('" + envdatafile + "')-->" + Asn1.type(envdatafile)
    print "Now wrap in S/MIME headers..."
    smimefile = 'cms2bobandcarl-smime-env.txt'
    n = Smime.wrap(smimefile, envdatafile)
    print "Smime.wrap() returns ", n, " (expected +ve)"
    _dump_file(smimefile)

    print "Query this S/MIME entity for info..."
    query = "content-type"
    r = Smime.query(smimefile, query)
    print "Smime.query('%s')=[%s]" % (query, r)
    query = "smime-type"
    r = Smime.query(smimefile, query)
    print "Smime.query('%s')=[%s]" % (query, r)

    print "Extract the original CMS env-data object in base64"
    extractedfile = 'cms2bobandcarl-extracted.txt'
    n = Smime.extract(extractedfile, smimefile, Smime.Opts.ENCODE_BASE64)
    print "Smime.extract() returns ", n, " (expected +ve)"
    # _dump_file(extractedfile)
    # Read base64 data into a string then analyze
    s = read_text_file(extractedfile)
    print "Asn1.type('" + extractedfile + "')-->" + Asn1.type(s)


def test_cms_sigdata():
    print "\nTESTING CMS SIG-DATA..."
    print "Create an signed-data message from Alice, using file-->file mode"
    # Create a file
    mytext = 'This is some sample content.'
    myfile = "mycontent.txt"
    write_file(myfile, mytext)
    # Alice reads in her private key to a secure "internal" key string
    prikeystr = Rsa.read_private_key('AlicePrivRSASign.p8', 'password')
    certlist = "AliceRSASignByCarl.cer"
    sigdatafile = 'cms_signedbyalice.p7m'
    n = Cms.make_sigdata(sigdatafile, myfile, certlist, prikeystr)
    print "Cms.make_sigdata() returns " + str(n) + " (expected 0)"
    assert(n == 0)
    print "Asn1.type('" + sigdatafile + "')-->" + Asn1.type(sigdatafile)

    print "\nQuery this CMS object file..."
    fname = sigdatafile
    query = "signatureAlgorithm"
    res = Cms.query_sigdata(sigdatafile, query)
    print "Cms.query_sigdata(" + fname + ", " + query + "):", res
    query = "CountOfSignerInfos"
    res = Cms.query_sigdata(sigdatafile, query)
    print "Cms.query_sigdata(" + fname + ", " + query + "):", res

    print "\nRead in the content from the signed-data file..."
    outputfile = "alicesdata.txt"
    n = Cms.read_sigdata_to_file(outputfile, sigdatafile)
    print "Cms.read_sigdata_to_file() returns " + str(n) + " (expected 0)"
    assert(0 == n)
    _dump_file(outputfile)

    print "\nVerify the signature in the sigdata file..."
    isok = Cms.verify_sigdata(sigdatafile)
    print "Cms.verify_sigdata() returns", isok
    assert isok

    print "\nUse string-->file mode..."
    print "DATA:", mytext
    sigdatafile1 = 'cms_signedbyalice1.p7m'
    n = Cms.make_sigdata_from_string(sigdatafile1, mytext, certlist, prikeystr)
    print "Cms.make_sigdata_from_string() returns " + str(n) + " (expected 0)"
    assert(n == 0)
    print "Asn1.type('" + sigdatafile1 + "')-->" + Asn1.type(sigdatafile1)

    s = Cms.read_sigdata_to_string(sigdatafile)
    print s

    print "signed-data files should be identical..."
    print "SHA1('" + sigdatafile + "')=\t" + Hash.hex_from_file(sigdatafile)
    print "SHA1('" + sigdatafile1 + "')=\t" + Hash.hex_from_file(sigdatafile1)
    assert(Hash.hex_from_file(sigdatafile) == Hash.hex_from_file(sigdatafile1))

    print "\nMake a 'detached signature' signed-data object using the message digest of the content..."
    hexdigest = Hash.hex_from_data(mytext, Hash.Alg.SHA256)
    print "SHA256('%s')=%s" % (mytext, hexdigest)
    sigdatafile_det = 'cms_signedbyalice_det.p7m'
    n = Cms.make_detached_sig(
        sigdatafile_det, hexdigest, certlist, prikeystr, Hash.Alg.SHA256)
    print "Cms.make_detached_sig() returns " + str(n) + " (expected 0)"
    assert(n == 0)
    print "Verify the signature in the detached sigdata file against the digest value..."
    print "First try verifying against the eContent (which is missing)..."
    try:
        isok = Cms.verify_sigdata(sigdatafile_det)
    except PKIError as e:
        print "Woops! PKIError:", e
    print "Now pass the digest we expect..."
    isok = Cms.verify_sigdata(sigdatafile_det, hexdigest=hexdigest)
    print "Cms.verify_sigdata(file,hexdigest) returns", isok
    assert isok

    print "\nCreate signed-data from a pre-computed signature value..."
    # Example 4.2 from [SMIME-EX]
    # Data to be signed
    datahex = ("54:68:69:73:20:69:73:20:73:6f:6d:65:20:73:61:6d"
               "70:6c:65:20:63:6f:6e:74:65:6e:74:2e")
    data = Cnv.fromhex(datahex)
    print "DATA:", Cnv.tohex(data)
    # Signature value generated by smartcard using rsa-sha1 (our default)
    sighex = ("2F:23:82:D2:F3:09:5F:B8:0C:58:EB:4E:9D:BF:89:9A"
              "81:E5:75:C4:91:3D:D3:D0:D5:7B:B6:D5:FE:94:A1:8A"
              "AC:E3:C4:84:F5:CD:60:4E:27:95:F6:CF:00:86:76:75"
              "3F:2B:F0:E7:D4:02:67:A7:F5:C7:8D:16:04:A5:B3:B5"
              "E7:D9:32:F0:24:EF:E7:20:44:D5:9F:07:C5:53:24:FA"
              "CE:01:1D:0F:17:13:A7:2A:95:9D:2B:E4:03:95:14:0B"
              "E9:39:0D:BA:CE:6E:9C:9E:0C:E8:98:E6:55:13:D4:68"
              "6F:D0:07:D7:A2:B1:62:4C:E3:8F:AF:FD:E0:D5:5D:C7")
    sig = Cnv.fromhex(sighex)
    print "SIG:", Cnv.tohex(sig)
    sigdatafile2 = 'cms_signedbyalice2.p7m'
    n = Cms.make_sigdata_from_sigvalue(sigdatafile2, sig, data, certlist)
    print "Cms.make_sigdata_from_sigvalue() returns " + str(n) + " (expected 0)"
    # Compare resulting file to expected `4.2.bin`
    print "SHA1(outputfile)=", Hash.hex_from_file(sigdatafile2)
    print "SHA1('4.2.bin' )=", Hash.hex_from_file('4.2.bin')
    assert(Hash.hex_from_file(sigdatafile2) == Hash.hex_from_file('4.2.bin'))


def test_cms_comprdata():
    print "\nTESTING CMS COMPRESSED-DATA..."
    print "Creating an compressed-data object..."
    basefile = "sonnets.txt"
    compfile = 'sonnets.p7z'
    print "INPUT:", basefile, os.path.getsize(basefile), "bytes"
    n = Cms.make_comprdata(compfile, basefile)
    print "Cms.make_comprdata() returns " + str(n) + " (expected 0)"
    assert(n == 0)
    print "COMPR:", compfile, os.path.getsize(compfile), "bytes"
    print "Asn1.type('" + compfile + "')-->" + Asn1.type(compfile)

    print "Reading an compressed-data object..."
    chkfile = "sonnets-uncompr.txt"
    n = Cms.read_comprdata(chkfile, compfile)
    print "Cms.read_comprdata() returns " + str(n) + " (expected +ve)"
    assert(n > 0)
    print "UNCPR:", chkfile, os.path.getsize(chkfile), "bytes"
    # Compare base file to final uncompressed
    print "SHA1(basefile)=", Hash.hex_from_file(basefile)
    print "SHA1(uncmfile)=", Hash.hex_from_file(chkfile)
    assert(Hash.hex_from_file(basefile) == Hash.hex_from_file(chkfile))

    print "Read with no-inflate option..."
    chkfile = "sonnets-noinflate.txt"
    n = Cms.read_comprdata(chkfile, compfile, Cms.ComprDataOpts.NO_INFLATE)
    assert(n > 0)
    print "NOINF:", chkfile, os.path.getsize(chkfile), "bytes"


def test_sig_rsa():
    print "\nTESTING SIG FUNCTIONS USING RSA..."

    print "Sign the string 'abc' using Alice's private RSA key..."
    keyfile = "AlicePrivRSASign.p8"
    password = "password"   # !!!
    alg = Sig.Alg.RSA_SHA1

    # Sign data
    data = "abc"
    sig = Sig.sign_data(data, keyfile, password, alg)
    print "sign_data:  ", sig

    # Sign the digest value of the data
    digest = Cnv.fromhex("a9993e364706816aba3e25717850c26c9cd0d89d")
    sig1 = Sig.sign_digest(digest, keyfile, password, alg)
    print "sign_digest:", sig1
    assert(sig1 == sig)

    # Encode the signature differently
    print "Different encodings..."
    sig2 = Sig.sign_data(data, keyfile, password, alg,
                         encoding=Sig.Encoding.BASE64URL)
    print "sign_data:  ", sig2
    sig3 = Sig.sign_data(data, keyfile, password, alg,
                         encoding=Sig.Encoding.HEX)
    print "sign_data:  ", sig3

    print "Verify the signature over the data"
    cert = "AliceRSASignByCarl.cer"
    isok = Sig.data_is_verified(sig, data, cert, alg)
    print "Sig.data_is_verified() returns", isok
    assert(isok)

    print "Use the wrong cert..."
    wrongcert = "BobRSASignByCarl.cer"
    isok = Sig.data_is_verified(sig, data, wrongcert, alg)
    print "Sig.data_is_verified() returns", isok, "(expected False)"
    assert(not isok)

    print "Verify the signature over the message digest value"
    isok = Sig.digest_is_verified(sig, digest, cert, alg)
    print "Sig.digest_is_verified() returns", isok
    assert(isok)

    print "Sign a file containing 'abc' using Alice's private RSA key..."
    datafile = "abc.txt"
    write_file(datafile, 'abc')
    sig = Sig.sign_file(datafile, keyfile, password, alg)
    print "sign_file:  ", sig
    # Verify it
    isok = Sig.file_is_verified(sig, datafile, cert, alg)
    print "Sig.file_is_verified() returns", isok
    assert(isok)


def test_sig_ecc():
    print "\nTESTING SIG FUNCTIONS USING ECC..."

    # Ref: [RFC6979] "Deterministic Usage of the DSA and ECDSA"
    # A.2.3.  ECDSA, 192 Bits (Prime Field)

    # Read in private key using (hex,curvename) form
    keyhex = "6FAB034934E4C0FC9AE67F5B5659A9D7D1FEFD187EE09FD4"
    curvename = Ecc.CurveName.P_192
    print "KEYHEX:", keyhex
    print "CURVE:", curvename
    keystr = Ecc.read_key_by_curve(keyhex, curvename)
    print "NBITS=", Ecc.query_key(keystr, "keyBits")

    # Sign data
    alg = Sig.Alg.ECDSA_SHA1
    data = "test"
    sig = Sig.sign_data(data, keystr, "", alg,
                        opts=Sig.Opts.DETERMINISTIC, encoding=Sig.Encoding.HEX)
    print "SIG:", sig

    print "Verify the signature over the data..."
    # Derive the EC public key from the private key
    pubkeystr = Ecc.publickey_from_private(keystr)
    # And use it to verify the signature
    isok = Sig.data_is_verified(sig, data, pubkeystr, alg)
    print "Sig.data_is_verified() returns", isok
    assert(isok)


# Explicity call this function to test the Pwd dialog class
# Note this does not begin with `test_` because we don't want it firing in
# py.test
def do_pwd():
    print "\nTESTING PWD DIALOG..."
    pwd = Pwd.prompt()
    print "[" + pwd + "]"
    pwd = Pwd.prompt("Demo of Pwd.prompt()", "Type secret phrase:")
    print "[" + pwd + "]"


def quick_version():
    print "\nDETAILS OF CORE DLL..."
    print "DLL Version=" + str(Gen.version()) \
          + " [" + Gen.core_platform() + "] Lic=" \
          + Gen.licence_type() \
          + " Compiled=[" \
          + Gen.compile_time() + "]"
    print "[" + Gen.module_name() + "]"


def main():
    do_all = True
    for arg in sys.argv:
        global delete_tmp_dir
        if (arg == 'nodelete'):
            delete_tmp_dir = False
        elif (arg == 'some'):
            do_all = False
    setup_temp_dir()

    # DO THE TESTS - EITHER SOME OR ALL
    if (do_all):
        test_version()
        test_error_lookup()
        test_cnv()
        test_cnv_utf8()
        test_cipher()
        test_cipher_block()
        test_cipher_file()
        test_cipher_keywrap()
        test_cipher_pad()
        test_rsa_makekeys()
        test_rsa_errors()
        test_rsa_savekeys()
        test_rsa_sign()
        test_rsa_encrypt()
        test_rng()
        test_hash()
        test_hmac()
        test_x509_generate()
        test_x509_analyze()
        test_x509_validate()
        test_x509_extract()
        test_wipe()
        test_asn1()
        test_ocsp()
        test_ecc()
        test_pbe()
        test_pfx()
        test_pem()
        test_cms_envdata()
        test_cms_sigdata()
        test_cms_comprdata()
        test_smime()
        test_sig_rsa()
        test_sig_ecc()

    else:   # just do some tests: comment out as necessary
        # test_version()
        # test_error_lookup()
        # test_cnv()
        # test_cnv_utf8()
        # test_cipher()
        # test_cipher_block()
        # test_cipher_file()
        # test_cipher_keywrap()
        # test_cipher_pad()
        # test_rsa_makekeys()
        # test_rsa_errors()
        # test_rsa_savekeys()
        # test_rsa_sign()
        # test_rsa_encrypt()
        # test_rng()
        # test_hash()
        # test_hmac()
        # test_x509_generate()
        test_x509_analyze()
        test_x509_validate()
        test_x509_extract()
        # test_wipe()
        # test_asn1()
        # test_ocsp()
        # test_ecc()
        # test_pbe()
        # test_pfx()
        # test_pem()
        # test_cms_envdata()
        # test_cms_sigdata()
        # test_cms_comprdata()
        # test_smime()
        # test_sig_rsa()
        # test_sig_ecc()

        # Uncomment the next line to test the Pwd dialog procedure
        # Do not do in py.test (unless you want to interact!)
#         ##do_pwd()

    reset_start_dir()
    quick_version()
    print "ALL DONE."


if __name__ == "__main__":
    main()
