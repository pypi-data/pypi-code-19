# This file is part of caucase
# Copyright (C) 2017  Nexedi
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# caucase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caucase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caucase.  If not, see <http://www.gnu.org/licenses/>.


import os, time
import shutil
import tempfile
import unittest
import json
from datetime import datetime
from caucase import app, db
from OpenSSL import crypto, SSL
from caucase.exceptions import (NoStorage, NotFound, Found, BadSignature,
                                BadCertificateSigningRequest,
                                BadCertificate,
                                CertificateVerificationError,
                                ExpiredCertificate)
from caucase.ca import CertificateAuthority, DEFAULT_DIGEST_LIST, MIN_CA_RENEW_PERIOD
from caucase import utils

class CertificateAuthorityTest(unittest.TestCase):

  def setUp(self):
    self.ca_dir = tempfile.mkdtemp()
    self.db_file = os.path.join(self.ca_dir, 'ca.db')
    self.max_request_amount = 3
    self.default_digest = "sha256"
    self.crt_keep_time = 0

    app.config.update(
      DEBUG=True,
      CSRF_ENABLED=True,
      SECRET_KEY = 'This is an UNSECURE Secret. Please CHANGE THIS for production environments.',
      TESTING=True,
      SQLALCHEMY_DATABASE_URI='sqlite:///%s' % self.db_file
    )
    from caucase.storage import Storage
    self._storage = Storage(db)

  def make_ca(self, crt_life_time, auto_sign_csr=False):
    return CertificateAuthority(
      storage=self._storage,
      ca_life_period=4,
      ca_renew_period=2,
      crt_life_time=crt_life_time,
      crl_renew_period=0.1,
      crl_base_url='http://crl.url.com',
      ca_subject='/C=XX/ST=State/L=City/OU=OUnit/O=Company/CN=CAAuth/emailAddress=xx@example.com',
      max_csr_amount=self.max_request_amount,
      crt_keep_time=self.crt_keep_time,
      auto_sign_csr=auto_sign_csr
    )

  def generateCSR(self, cn="toto.example.com", email="toto@example.com"):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    req = crypto.X509Req()
    subject = req.get_subject()
    subject.CN = cn
    subject.C = "CC"
    subject.ST = "ST"
    subject.L = "LOU"
    subject.O = "OOU"
    subject.OU = "OU"
    subject.emailAddress = email
    req.set_pubkey(key)
    utils.X509Extension().setDefaultCsrExtensions(req)
    req.sign(key, self.default_digest)

    return (req, key)

  def csr_tostring(self, csr):
    return crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr)

  def get_fake_cert_key(self):
    cert_string = """-----BEGIN CERTIFICATE-----
MIID6DCCAtCgAwIBAwIBBDANBgkqhkiG9w0BAQsFADCBljEiMCAGA1UEAwwZVGhl
IENlcnRpZmljYXRlIEF1dGhvcml0eTELMAkGA1UEBhMCWFgxDjAMBgNVBAgMBVN0
YXRlMREwDwYDVQQKDAhDb21wYWdueTENMAsGA1UECwwEVW5pdDENMAsGA1UEBwwE
Q2l0eTEiMCAGCSqGSIb3DQEJARYTY2EuYXV0aEBleGFtcGxlLmNvbTAeFw0xNzA0
MTYyMTQyNDVaFw0xODA0MTYyMTQyNDVaMBsxGTAXBgNVBAMMEGRhbmRAZXhhbXBs
ZS5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDrJNil62fkNm1j
UgEZ33hg5qYiLeNOEUgKaINCqhfQDuH7tTho+nRNxY2FSpv7ooyMckLYojNm+XEl
lUREE8hgIBiBWgiXazvoaxKFW2BIm7kpfxSC0t4pxwjehftm0Ny/nvms6SiE0ruL
3u+oUI9VVvgofra7mvhX3OZuZNb2QADaPnmyfB8VYGfzYAl0QgyFkrWzPflb/UXD
LdIP/niTpUHMgDTChQ+jf3tHm0pbsRZTxXISJY2+O5qpEgumW+Qcw5sKpjdfMYvH
hoM0IzMofBSfmQCZOjJRcisVLTASj5qN5+GFJi6Pz7oih203Ur8elq+iA0hRisA7
g37LNGXTAgMBAAGjgbowgbcwCQYDVR0TBAIwADAsBglghkgBhvhCAQ0EHxYdT3Bl
blNTTCBHZW5lcmF0ZWQgQ2VydGlmaWNhdGUwHQYDVR0OBBYEFPOBwIfuP8mulzmk
MgC1VGLCkwEDMB8GA1UdIwQYMBaAFGXLZo/7QINvcowfmpUEllOAJ6I5MDwGA1Ud
HwQ1MDMwMaAvoC2GK2h0dHBzOi8vWzIwMDE6NjdjOjEyNTQ6ZTpjNDo6Yzc0OF06
ODAwOS9jcmwwDQYJKoZIhvcNAQELBQADggEBAKarSr7WKXznFjbLfbedrci9mtwo
TYVpOUt/nt6lCiJ2wTGQea/e4KQ3WRwlUUHCX/K+G4QEV8OeDIA4uXnx24fclj35
hCYQCaJfIM96Z+elYIisOX3eFZ9cuo4fkODnry+vQNkYuOn/mFe0sVxoBK+oqSl5
/tN7pTFB2CaSBnRrNHquEc6YFoglCjQW4fXzHdQCdx5B7oOg/yloIst2WagXbyvE
zQvWKm6jjB5/xdT5mpxHB/lanSZMGXFnITh8qXrlTxd/tSa3ic6+k1WC++5brUvE
MtldUnSV++fZh9C4xsXyi26ytr2KkwcJcXQbU2PF4iuV6L0eYO2xOgpDCoQ=
-----END CERTIFICATE-----"""

    key_string = """-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDrJNil62fkNm1j
UgEZ33hg5qYiLeNOEUgKaINCqhfQDuH7tTho+nRNxY2FSpv7ooyMckLYojNm+XEl
lUREE8hgIBiBWgiXazvoaxKFW2BIm7kpfxSC0t4pxwjehftm0Ny/nvms6SiE0ruL
3u+oUI9VVvgofra7mvhX3OZuZNb2QADaPnmyfB8VYGfzYAl0QgyFkrWzPflb/UXD
LdIP/niTpUHMgDTChQ+jf3tHm0pbsRZTxXISJY2+O5qpEgumW+Qcw5sKpjdfMYvH
hoM0IzMofBSfmQCZOjJRcisVLTASj5qN5+GFJi6Pz7oih203Ur8elq+iA0hRisA7
g37LNGXTAgMBAAECggEASMRxSv9LekMhnN/OuWv/e7VE6kTbF9ifO6FWJXYvwlIo
utU87Le88ChXgE0zci6+YeQmLZYcZByDWEcWBh89Hgowqy7qg7lKo8UmySAa7r1K
Er5h4Y5R9AnFA9/gidPOzHns+AZ7ZIc2RLWr4qFzicxNJXL5J5twiPgyUy1fnHpg
Ktk3ccgtIe8IJNYS9hGW40X6DZfbiNqnUlGxS0Nsk7RQhEowcuAob7sBf2k6tSAx
qaaB3PYBwGsfgF6Zkq81/ZmzZPoD0vSLURAlglTWgGljqXOqXVnqUFbcyaZeKwqX
4b5MlQMZ09puOz5CGG0HhnTFmt+N1rU3Vsx74G5hWQKBgQD4wHt9WL6DQPQ2/i0l
o6afSd0+DV5HldHGCRt4aF3//bGU3OugNvHVK2ijXEUIDHcpvEW1vwjbqmkFI3Sn
wANCr8YAmu/51uYYyeUP4V35SKBtBBdhUvFOGE3MThJQusAdEYg65T9STQvmpRnJ
Yv5QRlX/jawEtS2H9pZo+WvZpQKBgQDx/tuiU2isBfOrT5MAVxtu/VEZvafwRcHe
0EmRCyW6+rHSA3o2/3f43t6x63qvvk6NYY9rSz/0TZkZ/Y3QihPNqGwGuuzSvsG+
yDfnv6YmtcnBPv2kXHwEeIsd9DdjqT4D3MIHGHo05cu9Ta7oTHVAo8OSQbEqkGwj
oYpuQTz4FwKBgQCxuo1A9OxByWHz/M1zDCdbviHGWTTYftH/5bfr4t3urmt4ChSM
R1WoUjiUJ7Pm2Uk2158TCSgiEvKwSjHqPUXXGtGk0w7M+l8yrOXt378OAnclDPxL
fECO5MyJQerSJWxoGIO2WN9SRVxQcfwnqIQ+BNMjIS0bu/uJHoU/AZ6uRQKBgQC5
FT9Oa5TG3NZ806OOwxCMVtpMYa2sKu4YSB27/VaiJ1MRWO+EWOedRHf2hC+VcmwJ
3fAfE7KaWy8Znb91G+YBiSr2CslOde8gx2laqk2dlbP1RQQhTUrc8IUWJ86lPq/b
rGAJpULyaj7lTiDUMoYLJjVSC0RBVawfpFGH+gVziQKBgQDI+dgmgFv3ULUUTBtP
iPwYrGFWmzcKwevPaIQqrsjJ0TY2INmQZi6pn4ogelUtcRMFjzpBGHrsxJM0RkSy
3A855c5gfp60XOQB3ab0OS0X5/gzDZHThN7wvspUFnZ9i6LhSEOHMEAxwSklCtPq
m4DpuP4nL0ixQJWZuV+qrx6Tow==
-----END PRIVATE KEY-----"""

    return (cert_string, key_string)

  def check_cert_equal(self, first, second):
    if isinstance(first, crypto.X509):
      first_string = crypto.dump_certificate(crypto.FILETYPE_PEM, first)
    else:
      first_string = first
    second_string = crypto.dump_certificate(crypto.FILETYPE_PEM, second)
    return first_string == second_string

  def check_key_equal(self, first, second):
    if isinstance(first, crypto.PKey):
      first_string = crypto.dump_privatekey(crypto.FILETYPE_PEM, first)
    else:
      first_string = first
    second_string = crypto.dump_privatekey(crypto.FILETYPE_PEM, second)
    return first_string == second_string

  def check_csr_equal(self, first, second):
    if isinstance(first, crypto.X509Req):
      first_string = crypto.dump_certificate_request(crypto.FILETYPE_PEM, first)
    else:
      first_string = first
    second_string = crypto.dump_certificate_request(crypto.FILETYPE_PEM, second)
    return first_string == second_string

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    if os.path.exists(self.ca_dir):
      shutil.rmtree(self.ca_dir)

  def test_createCAKeyPair(self):
    # initials keypair are generated when instanciating ca
    ca = self.make_ca(160)
    self.assertEquals(len(ca._ca_key_pairs_list), 1)

  def renewCAKetPair(self):
    ca = self.make_ca(2)
    self.assertEquals(len(ca._ca_key_pairs_list), 1)
    first = ca._ca_key_pairs_list

    # No renew possible
    self.assertFalse(ca.renewCAKeyPair())
    time.sleep(5)
    # ca Certificate should be renewed
    self.assertTrue(ca.renewCAKeyPair())

    self.assertEquals(len(ca._ca_key_pairs_list), 2)
    self.assertTrue(self.check_cert_equal(ca._ca_key_pairs_list[0]['crt'], first['crt']))
    self.assertTrue(self.check_key_equal(ca._ca_key_pairs_list[0]['key'], first['key']))

  def test_getPendingCertificateRequest(self):
    ca = self.make_ca(190)
    csr, key = self.generateCSR()
    csr_string = self.csr_tostring(csr)
    csr_id = ca.createCertificateSigningRequest(csr_string)

    stored = ca.getPendingCertificateRequest(csr_id)
    self.assertEquals(csr_string, stored)

  def test_deletePendingCertificateRequest(self):
    ca = self.make_ca(190)
    csr, key = self.generateCSR()
    csr_string = self.csr_tostring(csr)
    csr_id = ca.createCertificateSigningRequest(csr_string)
    stored = ca.getPendingCertificateRequest(csr_id)
    self.assertEquals(csr_string, stored)

    ca.deletePendingCertificateRequest(csr_id)
    with self.assertRaises(NotFound):
       ca.getPendingCertificateRequest(csr_id)

  def test_createCertificate(self):
    ca = self.make_ca(190)
    csr, key = self.generateCSR()
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))

    # sign certificate with default ca keypair
    cert_id = ca.createCertificate(csr_id)

    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))
    subj_dict = {'CN': 'toto.example.com', 
                 'C': 'CC',
                 'ST': 'ST',
                 'L': 'LOU',
                 'O': 'OOU',
                 'OU': 'OU',
                 'emailAddress': 'toto@example.com'}
    for attr in ['C', 'ST', 'L', 'OU', 'O', 'CN', 'emailAddress']:
      self.assertEqual(getattr(x509.get_subject(), attr), subj_dict[attr])

    with self.assertRaises(NotFound):
       ca.getPendingCertificateRequest(csr_id)

  def test_createCertificate_custom_subject(self):
    ca = self.make_ca(190)
    csr, key = self.generateCSR(cn="test certificate", email="some@test.com")
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))

    # sign certificate with default ca keypair
    subject_dict = dict(CN="real cn", emailAddress="caucase@email.com")
    # sign certificate but change subject
    cert_id = ca.createCertificate(csr_id, subject_dict=subject_dict)

    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))
    self.assertEqual(x509.get_subject().CN, subject_dict['CN'])
    self.assertEqual(x509.get_subject().emailAddress, subject_dict['emailAddress'])
    # Others attributes are empty
    for attr in ['C', 'ST', 'L', 'OU', 'O']:
      self.assertEqual(getattr(x509.get_subject(), attr), None)

    with self.assertRaises(NotFound):
       ca.getPendingCertificateRequest(csr_id)

  def test_createCertificate_custom_subject2(self):
    ca = self.make_ca(190)
    csr, key = self.generateCSR(cn="test certificate", email="some@test.com")
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))

    subject_dict = {'CN': 'some.site.com', 
                   'C': 'FR',
                   'O': 'My Organisation',
                   'L': 'Localisation',
                   'OU': 'Organisation U',
                   'ST': 'State',
                   'emailAddress': 'toto@example.com'}
    # sign certificate but change subject
    cert_id = ca.createCertificate(csr_id, subject_dict=subject_dict)

    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    # certificate is still valid
    self.assertTrue(utils.validateCertAndKey(x509, key))
    # check that all attributes are set
    for attr in ['C', 'ST', 'L', 'OU', 'O']:
      self.assertEqual(getattr(x509.get_subject(), attr), subject_dict[attr])

    with self.assertRaises(NotFound):
       ca.getPendingCertificateRequest(csr_id)

  def test_createCertificate_custom_subject_no_cn(self):
    ca = self.make_ca(190)
    csr, key = self.generateCSR(cn="test certificate", email="some@test.com")
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))

    subject_dict = dict(C="FR", emailAddress="caucase@email.com")

    # CN is missing, will raise
    with self.assertRaises(AttributeError):
      ca.createCertificate(csr_id, subject_dict=subject_dict)

  def test_getCAKeypairForCertificate(self):
    csr, key = self.generateCSR()
    ca = self.make_ca(3)
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))
    # sign certificate with default ca keypair
    cert_id = ca.createCertificate(csr_id)
    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))
    cert_keypair = ca._ca_key_pairs_list[0]

    # 2 crt_life_time cycles + 1s
    time.sleep(7)
    # Create new CA keypair
    self.assertTrue(ca.renewCAKeyPair())

    # get keypair which should be used to renew this cert
    calculated = ca.getCAKeypairForCertificate(x509)
    self.assertTrue(self.check_cert_equal(cert_keypair['crt'], calculated['crt']))
    self.assertTrue(self.check_key_equal(cert_keypair['key'], calculated['key']))
    self.assertEquals(len(ca._ca_key_pairs_list), 2)
    new_keypair = ca._ca_key_pairs_list[-1]

    time.sleep(3)
    # the first ca keypair cannot be used to renew cert (7+3 -12 = 2 < crt_life_time)
    calculated = ca.getCAKeypairForCertificate(x509)
    self.assertTrue(self.check_cert_equal(new_keypair['crt'], calculated['crt']))
    self.assertTrue(self.check_key_equal(new_keypair['key'], calculated['key']))

  def test_renewCertificate(self):
    ca = self.make_ca(158)
    csr, key = self.generateCSR()
    csr_string = self.csr_tostring(csr)
    csr_id = ca.createCertificateSigningRequest(csr_string)
    # sign certificate with default ca keypair
    cert_id = ca.createCertificate(csr_id)
    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))

    payload = dict(
      renew_csr=csr_string,
      crt=cert
    )
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key), [self.default_digest])
    new_csr_id = ca.renew(wrapped)
    new_cert_id = '%s.crt.pem' % new_csr_id[:-8]
    new_cert = ca.getCertificate(new_cert_id)
    new_x509 = crypto.load_certificate(crypto.FILETYPE_PEM, new_cert)
    self.assertTrue(utils.validateCertAndKey(new_x509, key))
    self.assertEquals(new_x509.get_subject().CN, x509.get_subject().CN)
    # current certificate is not revoked
    self.assertTrue(utils.validateCertAndKey(x509, key))

  def test_renewCertificate_bad_cert(self):
    ca = self.make_ca(158)
    csr, key = self.generateCSR()
    csr_string = self.csr_tostring(csr)
    csr_id = ca.createCertificateSigningRequest(csr_string)
    # sign certificate with default ca keypair
    cert_id = ca.createCertificate(csr_id)
    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))

    # second certificate
    csr2, key2 = self.generateCSR()
    csr_id2 = ca.createCertificateSigningRequest(self.csr_tostring(csr2))
    cert_id2 = ca.createCertificate(csr_id2)
    cert2 = ca.getCertificate(cert_id2)
    x509_2 = crypto.load_certificate(crypto.FILETYPE_PEM, cert2)
    self.assertTrue(utils.validateCertAndKey(x509_2, key2))

    payload = dict(
      renew_csr=csr_string,
      crt=cert
    )
    # sign with bad key
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key2), [self.default_digest])
    with self.assertRaises(BadSignature):
      ca.renew(wrapped)

    # payload with invalid PEM certificate 
    payload = dict(
      renew_csr=csr_string,
      crt="BAD PEM CERTIFICATE"
    )
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key), [self.default_digest])
    with self.assertRaises(BadSignature):
      ca.renew(wrapped)

    # payload with invalid PEM certificate request content
    payload = dict(
      renew_csr="BAD PEM CERTIFICATE REQUEST",
      crt=cert
    )
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key), [self.default_digest])
    with self.assertRaises(BadCertificateSigningRequest):
      ca.renew(wrapped)

    # payload with Fake certificate 
    fcert, fkey = self.get_fake_cert_key()
    payload = dict(
      renew_csr=csr_string,
      crt=cert
    )
    wrapped = utils.wrap(payload, fkey, [self.default_digest])
    with self.assertRaises(BadSignature):
      ca.renew(wrapped)

    payload = dict(
      renew_csr=csr_string,
      crt=fcert
    )
    wrapped = utils.wrap(payload, fkey, [self.default_digest])
    with self.assertRaises(BadCertificateSigningRequest):
      # Fake certificate and renew_csr has not the same csr
      ca.renew(wrapped)

  def test_revokeCertificate(self):
    ca = self.make_ca(158)
    csr, key = self.generateCSR()
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))
    # sign certificate with default ca keypair
    cert_id = ca.createCertificate(csr_id)
    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))

    payload = dict(
      reason='',
      revoke_crt=cert
    )
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key), [self.default_digest])
    ca.revokeCertificate(wrapped)
    with self.assertRaises(NotFound):
      ca.getCertificate(cert_id)

    revocation_list = self._storage.getRevocationList()
    self.assertEquals(len(revocation_list), 1)
    self.assertEquals(revocation_list[0].serial, utils.getSerialToInt(x509))

  def test_revokeCertificate_expired(self):
    ca = self.make_ca(2)
    csr, key = self.generateCSR()
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))
    # sign certificate with default ca keypair
    cert_id = ca.createCertificate(csr_id)
    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))

    # wait until certificate expire
    time.sleep(3)

    payload = dict(
      reason='',
      revoke_crt=cert
    )
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key), [self.default_digest])
    with self.assertRaises(CertificateVerificationError):
      # if certificate expire, verification fail
      ca.revokeCertificate(wrapped)

  def test_revokeCertificate_bad_cert(self):
    ca = self.make_ca(158)
    csr, key = self.generateCSR()
    csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))
    # sign certificate with default ca keypair
    cert_id = ca.createCertificate(csr_id)
    cert = ca.getCertificate(cert_id)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    self.assertTrue(utils.validateCertAndKey(x509, key))

    # second certificate
    csr2, key2 = self.generateCSR()
    csr_id2 = ca.createCertificateSigningRequest(self.csr_tostring(csr2))
    cert_id2 = ca.createCertificate(csr_id2)
    cert2 = ca.getCertificate(cert_id2)
    x509_2 = crypto.load_certificate(crypto.FILETYPE_PEM, cert2)
    self.assertTrue(utils.validateCertAndKey(x509_2, key2))

    payload = dict(
      reason="",
      revoke_crt=cert
    )
    # sign with bad key
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key2), [self.default_digest])
    with self.assertRaises(BadSignature):
      ca.revokeCertificate(wrapped)

    # payload with invalid PEM certificate 
    payload = dict(
      reason="",
      revoke_crt="BAD PEM CERTIFICATE"
    )
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key), [self.default_digest])
    with self.assertRaises(BadSignature):
      ca.revokeCertificate(wrapped)

    # payload with Fake certificate 
    fcert, fkey = self.get_fake_cert_key()
    payload = dict(
      reason="",
      revoke_crt=cert
    )
    wrapped = utils.wrap(payload, fkey, [self.default_digest])
    with self.assertRaises(BadSignature):
      ca.revokeCertificate(wrapped)

    payload = dict(
      reason="",
      revoke_crt=fcert
    )
    wrapped = utils.wrap(payload, fkey, [self.default_digest])
    with self.assertRaises(CertificateVerificationError):
      ca.revokeCertificate(wrapped)

  def test_getCertificateRevocationList(self):
    ca = self.make_ca(158)
    def signcert():
      csr, key = self.generateCSR()
      csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))
      # sign certificate with default ca keypair
      cert_id = ca.createCertificate(csr_id)
      cert = ca.getCertificate(cert_id)
      x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
      self.assertTrue(utils.validateCertAndKey(x509, key))
      return x509, key

    cert_1, key_1 = signcert()
    cert_2, key_2 = signcert()
    cert2_string = crypto.dump_certificate(crypto.FILETYPE_PEM, cert_2)
    cert_3, key_3 = signcert()
    cert3_string = crypto.dump_certificate(crypto.FILETYPE_PEM, cert_3)
    cert_4, key_4 = signcert()

    crl = ca.getCertificateRevocationList()
    crl_obj = crypto.load_crl(crypto.FILETYPE_PEM, crl)
    self.assertEquals(crl_obj.get_revoked(), None)

    payload = dict(
      reason="",
      revoke_crt=cert2_string
    )
    # sign with bad key
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key_2), [self.default_digest])
    ca.revokeCertificate(wrapped)

    crl2_string = ca.getCertificateRevocationList()
    crl2 = crypto.load_crl(crypto.FILETYPE_PEM, crl2_string)
    self.assertEquals(len(crl2.get_revoked()), 1)
    serial = utils.getSerialToInt(cert_2)
    self.assertEquals(crl2.get_revoked()[0].get_serial(), serial.upper())

    payload = dict(
      reason="",
      revoke_crt=cert3_string
    )
    # sign with bad key
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key_3), [self.default_digest])
    ca.revokeCertificate(wrapped)

    crl3_string = ca.getCertificateRevocationList()
    crl3 = crypto.load_crl(crypto.FILETYPE_PEM, crl3_string)
    self.assertEquals(len(crl3.get_revoked()), 2)
    matches = 0
    for revoked in crl3.get_revoked():
      if revoked.get_serial() == utils.getSerialToInt(cert_3).upper():
        matches += 1
      elif revoked.get_serial() == utils.getSerialToInt(cert_2).upper():
        matches += 1

    self.assertEquals(matches, 2)
    crl4_string = ca.getCertificateRevocationList()
    # nothing changed, crl not expired
    self.assertEquals(crl3_string, crl4_string)

  def test_getCertificateRevocationList_with_expire(self):
    ca = self.make_ca(2)
    def signcert():
      csr, key = self.generateCSR()
      csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))
      # sign certificate with default ca keypair
      cert_id = ca.createCertificate(csr_id)
      cert = ca.getCertificate(cert_id)
      x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
      self.assertTrue(utils.validateCertAndKey(x509, key))
      return x509, key

    cert_1, key_1 = signcert()
    cert_2, key_2 = signcert()
    cert2_string = crypto.dump_certificate(crypto.FILETYPE_PEM, cert_2)

    crl_string = ca.getCertificateRevocationList()
    crl = crypto.load_crl(crypto.FILETYPE_PEM, crl_string)
    self.assertEquals(crl.get_revoked(), None)

    payload = dict(
      reason="",
      revoke_crt=cert2_string
    )
    # sign with bad key
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key_2), [self.default_digest])
    ca.revokeCertificate(wrapped)

    crl2_string = ca.getCertificateRevocationList()
    crl2 = crypto.load_crl(crypto.FILETYPE_PEM, crl2_string)
    self.assertEquals(len(crl2.get_revoked()), 1)
    serial = utils.getSerialToInt(cert_2)
    self.assertEquals(crl2.get_revoked()[0].get_serial(), serial.upper())

    # wait until cert_2 expire
    time.sleep(3)

    cert_3, key_3 = signcert()
    cert3_string = crypto.dump_certificate(crypto.FILETYPE_PEM, cert_3)

    payload = dict(
      reason="",
      revoke_crt=cert3_string
    )
    # sign with bad key
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key_3), [self.default_digest])
    ca.revokeCertificate(wrapped)

    crl3_string = ca.getCertificateRevocationList()
    crl3 = crypto.load_crl(crypto.FILETYPE_PEM, crl3_string)

    # cert_2 is not longer into crl (expired)
    self.assertEquals(len(crl3.get_revoked()), 1)
    serial = utils.getSerialToInt(cert_3)
    self.assertEquals(crl3.get_revoked()[0].get_serial(), serial.upper())

  def test_getCertificateRevocationList_with_validation(self):
    ca = self.make_ca(158)
    def signcert():
      csr, key = self.generateCSR()
      csr_id = ca.createCertificateSigningRequest(self.csr_tostring(csr))
      # sign certificate with default ca keypair
      cert_id = ca.createCertificate(csr_id)
      cert = ca.getCertificate(cert_id)
      x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
      self.assertTrue(utils.validateCertAndKey(x509, key))
      return x509, key
  
    cert_1, key_1 = signcert()
    cert_2, key_2 = signcert()
    cert2_string = crypto.dump_certificate(crypto.FILETYPE_PEM, cert_2)
    cert_3, key_3 = signcert()
  
    payload = dict(
      reason="",
      revoke_crt=cert2_string
    )
    # sign with bad key
    wrapped = utils.wrap(payload, crypto.dump_privatekey(crypto.FILETYPE_PEM, key_2), [self.default_digest])
    ca.revokeCertificate(wrapped)
  
    crl_string = ca.getCertificateRevocationList()
    crl = crypto.load_crl(crypto.FILETYPE_PEM, crl_string)
    self.assertEquals(len(crl.get_revoked()), 1)
    serial = utils.getSerialToInt(cert_2)
    self.assertEquals(crl.get_revoked()[0].get_serial(), serial.upper())
  
    with self.assertRaises(CertificateVerificationError):
      utils.verifyCertificateChain(cert_2,
                              [x['crt'] for x in ca._ca_key_pairs_list], crl)
    utils.verifyCertificateChain(cert_3,
                              [x['crt'] for x in ca._ca_key_pairs_list], crl)
    utils.verifyCertificateChain(cert_1,
                              [x['crt'] for x in ca._ca_key_pairs_list], crl)

