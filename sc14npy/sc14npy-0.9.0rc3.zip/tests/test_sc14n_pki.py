#! python2
# -*- coding: utf8 -*-

"""Some tests for `sc14n.py` the Python interface to SC14N using CryptoSys PKI."""

# test_sc14n_pki.py: version 0.9.0

# ************************** LICENSE *****************************************
# Copyright (C) 2017 David Ireland, DI Management Services Pty Limited.
# <http://www.di-mgt.com.au/contact/> <www.cryptosys.net>
# The code in this module is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>
# ****************************************************************************

# Requires CryptoSys PKI to be installed.
# Get a Trial Edition from http://www.cryptosys.net/pki/.

import context   # test: setup path to module in parent
from sc14n import *  # @UnusedWildImport
import cryptosyspki as pki


# Show some info about the core DLL
print "DLL version =", Gen.version()

######################
# HARD-CODED PKI STUFF
######################
# Alice's PKCS8 encrypted key and X.509 certificate
# from RFC 4134 "Examples of S/MIME Messages"
# Private key password is "password"
myprikey = '''-----BEGIN ENCRYPTED PRIVATE KEY-----
MIICojAcBgoqhkiG9w0BDAEDMA4ECFleZ90vhGrRAgIEAASCAoA9rti16XVH
K4AJVe1CNf61NIpIogu/Xs4Yn4hXflvewiOwe6/9FkxBXLbhKdbQWn1Z4p3C
njVns2VYEO/qpJR3LciHMwp5dsqedUVVia//CqFHtEV9WfvCKWgmlkkT1YEm
1aChZnPP5i6IhwVT9qvFluTZhvVmjW0YyF86OrOp0uxxVic7phPbnPrOMelf
ZPc3A3EGpzDPkxN+o0obw87tUgCL+s0KtUOr3c6Si4KQ3IQjrjZxQF4Se3t/
4PEpqUl5EpYiCx9q5uqb0Lr1kWiiQ5/inZm5ETc+qO+ENcp0KjnX523CATYd
U5iOjl/X9XZeJrMpOCXogEuhmLPRauYP1HEWnAY/hLW93v10QJXY6ALlbkL0
sd5WU8Ces7T04b/p4/12yxqYqV68QePyfHpegdraDq3vRfopSwrUxtL9cisP
jsQcJ5FL/SfloFbmld4CKIjMsromsEWqo6rfo3JqNizgTVIIWExy3jDT9VvK
d9ADH0g3JCbuFzaWVOZMmZ0wlo28PKkLQ8FkW8CG/Lq/Q/bHLPM+sPdLN+ke
gpA6fvL4wpku4ST7hmeN1vWbRLlCfuFijux77hdM7knO9/MawICsA4XdzR78
p0C2hJlc6p46IWZaINQXGstTbJMh+mJ7i1lrbG2kvZ2Twf9R+RaLp2mPHjb1
+P+3f2L3tOoC31oJ18u/L1MXEWxLEZHB0+ANg+N/0/icwImcI0D+wVN2puU4
m58j81sGZUEAB3aFEbPxoX3y+qYlOnt1OfdY7WnNdyr9ZzI09fkrTvujF4LU
nycqE+MXerf0PxkNu1qv9bQvCoH8x3J2EVdMxPBtH1Fb7SbE66cNyh//qzZo
B9Je
-----END ENCRYPTED PRIVATE KEY-----
'''

mycert = '''-----BEGIN CERTIFICATE-----
MIICLDCCAZWgAwIBAgIQRjRrx4AAVrwR024uxBCzsDANBgkqhkiG9w0BAQUFADAS
MRAwDgYDVQQDEwdDYXJsUlNBMB4XDTk5MDkxOTAxMDg0N1oXDTM5MTIzMTIzNTk1
OVowEzERMA8GA1UEAxMIQWxpY2VSU0EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJ
AoGBAOCJczmN2PX16Id2OX9OsAW7U4PeD7er3H3HdSkNBS5tEt+mhibU0m+qWCn8
l+z6glEPMIC+sVCeRkTxLLvYMs/GaG8H2bBgrL7uNAlqE/X3BQWT3166NVbZYf8Z
f8mB5vhs6odAcO+sbSx0ny36VTq5mXcCpkhSjE7zVzhXdFdfAgMBAAGjgYEwfzAM
BgNVHRMBAf8EAjAAMA4GA1UdDwEB/wQEAwIGwDAfBgNVHSMEGDAWgBTp4JAnrHgg
eprTTPJCN04irp44uzAdBgNVHQ4EFgQUd9K00bdMioqjzkWdzuw8oDrj/1AwHwYD
VR0RBBgwFoEUQWxpY2VSU0FAZXhhbXBsZS5jb20wDQYJKoZIhvcNAQEFBQADgYEA
PnBHqEjME1iPylFxa042GF0EfoCxjU3MyqOPzH1WyLzPbrMcWakgqgWBqE4lradw
FHUv9ceb0Q7pY9Jkt8ZmbnMhVN/0uiVdfUnTlGsiNnRzuErsL2Tt0z3Sp0LF6DeK
tNufZ+S9n/n+dO/q+e5jatg/SyUJtdgadq7rm9tJsCI=
-----END CERTIFICATE-----
'''

mypassword = "password"   # Best security practice!!


def sign_string(s):
    # Hard-coded key and password (useful in IDE mode)
    sigval = pki.Sig.sign_data(s, myprikey, mypassword, pki.Sig.Alg.RSA_SHA1)
    return sigval


def sign_digest(digval):
    # Hard-coded key and password (useful in IDE mode)
    sigval = pki.Sig.sign_digest(pki.Cnv.frombase64(digval), myprikey, mypassword, pki.Sig.Alg.RSA_SHA1)
    return sigval


def rsa_key_value():
    """Extract RSAKeyValue from public certificate in XML style"""
    return pki.Rsa.to_xmlstring(pki.Rsa.read_public_key(mycert))


def sha1_from_file_base64(fname):
    """Compute SHA-1 digest of file in base64 encoding"""
    return pki.Cnv.tobase64(pki.Hash.file(fname))


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


def split2len(s, n):
    """Split up string s into lines of length n."""
    def _f(_s, _n):
        while _s:
            yield _s[:_n]
            _s = _s[_n:]
    return "\n".join(_f(s, n))


def make_signed_file_latin1(outfile, basefile, okdigest):
    """
    Compute and replace %digval%, %sigval% and %keyval%
    in a simple XML-DSIG file - expecting here original to be Latin-1 encoded.
    With lots of verbose debugging checks and alternative ways to do things.

    :param outfile: new file to be created
    :param basefile: base XML file Latin-1 encoded with %% parameters
    :param okdigest: expected SHA-1 digest of final file (in base64)
    :return: N/A
    """

    print "FILE:", basefile

    # Read in c14n'd data excluding Signature element
    s = C14n.file2string(basefile, "Signature", Tran.EXCLUDEBYTAG)
    print "EXCLUDE <Signature>:\n", s.decode('utf-8')

    # Check digest of this string (optional)
    print "DIG(string):", pki.Cnv.tobase64(pki.Hash.data(s))

    # Compute required digest directly
    digval = C14n.file2digest(basefile, "Signature", Tran.EXCLUDEBYTAG)
    print "DIG(bytag) :", digval

    # Extract SignedInfo from base file
    s = C14n.file2string(basefile, "SignedInfo", Tran.SUBSETBYTAG)
    print "SUBSET <SignedInfo>:\n", s.decode('utf-8')

    # Insert the digest value into the SignedInfo
    siginfo = s.replace("%digval%", digval)
    print siginfo

    # Compute digest value of this new string (optional)
    print "DIG(string):", pki.Cnv.tobase64(pki.Hash.data(siginfo))
    # Compute digest value directly using SC14N (optional)
    print "DIG(bytag) :", C14n.string2digest(siginfo)

    # Compute the signature value directly over the SignedInfo element
    sigval = sign_string(siginfo)
    print "SIG:\n", sigval

    # Get RSA Key Value in XML form
    keyval = rsa_key_value()
    print "keyval=\n", keyval

    # If we only had the private key, we could get the RSA Key Value from that as well,
    # but be careful not to expose your private key! Two ways to do that:
    print pki.Rsa.to_xmlstring(pki.Rsa.publickey_from_private(pki.Rsa.read_private_key(myprikey, mypassword)))
    print pki.Rsa.to_xmlstring(pki.Rsa.read_private_key(myprikey, mypassword), pki.Rsa.XmlOptions.EXCLPRIVATE)

    # If we needed it we can get the <X509Certificate> value as well
    x509cert = pki.X509.read_string_from_file(mycert)
    print "<X509Certificate>=\n", split2len(x509cert, 80)

    # Substitute the 3 values (digval, sigval and keyval) in the original file (NB Latin-1 encoded)
    s = read_text_file(basefile)
    news = s.replace("%digval%", digval).replace("%sigval%", sigval).replace("%keyval%", keyval)
    print "New XML=\n", news.decode('iso-8859-1')
    write_file(outfile, news)
    print "Created new file", outfile

    # Check digest of final file matches what we expected
    newdig = sha1_from_file_base64(outfile)
    print "SHA1(newfile)=", newdig
    if (len(okdigest) > 0 and newdig != okdigest ):
        print "ERROR: digest values do not match"


def make_signed_xml(outfile, basefile, prikey, password, cert):
    """
    Compute and replace %digval%, %sigval% and %keyval% in XML-DSIG document
    :param outfile: New file to be created
    :param basefile: Base file containing %digval%, %sigval% and %keyval% to be repleaced
    :param prikey: Encrypted private key (either filename or PEM-style string)
    :param password: Password for encrypted private key
    :param cert: Matching X509 certificate (not checked)
    :return: N/A
    """

    # Compute digest value of base XML excluding Signature element
    digval = C14n.file2digest(basefile, "Signature", Tran.EXCLUDEBYTAG)

    # Read in incomplete SignedInfo element that needs the DigestValue filled in
    s = C14n.file2string(basefile, "SignedInfo", Tran.SUBSETBYTAG)

    # Insert the digest value in the SignedInfo string
    siginfo = s.replace("%digval%", digval)

    # Compute the signature value over the completed SignedInfo element
    sigval = pki.Sig.sign_data(siginfo, prikey, password, pki.Sig.Alg.RSA_SHA1)

    # Get RSA Key Value in XML form
    keyval = pki.Rsa.to_xmlstring(pki.Rsa.read_public_key(cert))

    # Substitute these 3 values in the original file
    s = read_text_file(basefile)
    news = s.replace("%digval%", digval).replace("%sigval%", sigval).replace("%keyval%", keyval)
    write_file(outfile, news)


def test_olamundo():
    # File with Latin-1-encoded character (ISO-8859-1)
    # Long-winded way with checks and debugging
    make_signed_file_latin1("olamundo-new.xml", "olamundo-base.xml", "IyaPyNs1fMIR59UfcRQbHY4AZLE=")

    basefile = "olamundo-base.xml"
    newfile = "olamundo-new1.xml"
    make_signed_xml(newfile, basefile, myprikey, mypassword, mycert)
    print "SHA1(" + newfile + ")=" + sha1_from_file_base64(newfile)


def test_daiwei():
    # File with UTF-8-encoded chinese characters
    basefile = "daiwei-base.xml"
    newfile = "diawei-new.xml"
    make_signed_xml(newfile, basefile, myprikey, mypassword, mycert)

    # Compare to reference document
    # Note there can be some differences between valid signed files
    # e.g. whitespace in the Signature element not in SignedInfo
    print "SHA1(" + newfile + ")=" + C14n.file2digest(newfile)
    okfile = "daiwei.xml"
    print "SHA1(" + okfile + ")=" + C14n.file2digest(okfile)
    _print_file(newfile)

def main():
    test_olamundo()
    test_daiwei()

    print "ALL DONE."


if __name__ == "__main__":
    main()
