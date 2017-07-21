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
from datetime import datetime, timedelta
from caucase import app, db
from caucase.storage import Storage, Config
from OpenSSL import crypto, SSL
from caucase.exceptions import (NoStorage, NotFound, Found)
from sqlite3 import IntegrityError
from caucase import utils
import uuid

class StorageTest(unittest.TestCase):

  def setUp(self):
    self.ca_dir = tempfile.mkdtemp()
    self.db_file = os.path.join(self.ca_dir, 'ca.db')
    #os.mkdir(self.ca_dir)
    self.max_request_amount = 3
    self.default_digest = "sha256"

    app.config.update(
      DEBUG=True,
      CSRF_ENABLED=True,
      SECRET_KEY = 'This is an UNSECURE Secret. Please CHANGE THIS for production environments.',
      TESTING=True,
      SQLALCHEMY_DATABASE_URI='sqlite:///%s' % self.db_file
    )
    
    self._storage = Storage(db)

  def setConfig(self, key, value):
    entry = self._storage._getConfig(key)
    if not entry:
      entry = Config(key=key, value='%s' % value)
      db.session.add(entry)
    else:
      # update value
      entry.value = value
    db.session.commit()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    if os.path.exists(self.ca_dir):
      shutil.rmtree(self.ca_dir)

  def createCAKeyPair(self, life_time=60):
    key_pair = {}
    key = crypto.PKey()
    # Use 2048 bits key size
    key.generate_key(crypto.TYPE_RSA, 2048)

    key_pair['key'] = key

    ca = crypto.X509()
    ca.set_version(3)
    ca.set_serial_number(int(time.time()))
    ca.get_subject().CN = "CA Cert %s" % int(time.time())
    ca.get_subject().C = "FR"
    ca.get_subject().ST = "XX"
    ca.get_subject().O = "ORG"
    ca.get_subject().OU = "OU"
    ca.get_subject().L = "LL"
    ca.get_subject().emailAddress = "xxx@exemple.com"
    ca.gmtime_adj_notBefore(0)
    ca.gmtime_adj_notAfter(life_time)
    ca.set_issuer(ca.get_subject())
    ca.set_pubkey(key)
    utils.X509Extension().setCaExtensions(ca)
    ca.sign(key, self.default_digest)
    key_pair['crt'] = ca

    return key_pair

  def generateCSR(self, cn="toto.example.com"):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    req = crypto.X509Req()
    subject = req.get_subject()
    subject.CN = cn
    subject.C = "CC"
    subject.ST = "ST"
    subject.L = "LL"
    subject.O = "ORG"
    subject.OU = "OU"
    subject.emailAddress = "toto@example.com"
    req.set_pubkey(key)
    utils.X509Extension().setDefaultCsrExtensions(req)
    req.sign(key, self.default_digest)

    return (req, key)

  def createCertificate(self, ca_key_pair, req, expire_sec=180):
    serial = uuid.uuid1().int
    cert = crypto.X509()
    # 3 = v3
    cert.set_version(3)
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(expire_sec)
    cert.set_issuer(ca_key_pair['crt'].get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    utils.X509Extension().setDefaultExtensions(
      cert,
      subject=cert,
      issuer=ca_key_pair['crt'],
      crl_url="http://ca.crl.com")
    cert.sign(ca_key_pair['key'], self.default_digest)
    return cert

  def generateCRL(self, ca_key_pair, revocation_list, version_number):
    now = datetime.now()
    crl = crypto.CRL()
    num_crl_days = 1

    for revocation in revocation_list:
      revoked = crypto.Revoked()
      revoked.set_rev_date(
          revocation.creation_date.strftime("%Y%m%d%H%M%SZ").encode("ascii")
        )
      revoked.set_serial(revocation.serial.encode("ascii"))
      revoked.set_reason(None) #b'%s' % revocation.reason)
      crl.add_revoked(revoked)

    crl.set_version(version_number)
    # XXX - set how to get the cacert here
    cert = ca_key_pair['crt']
    key = ca_key_pair['key']

    return crypto.load_crl(
        crypto.FILETYPE_PEM,
        crl.export(
          cert,
          key,
          type=crypto.FILETYPE_PEM,
          days=num_crl_days,
          digest=self.default_digest)
      )

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

  def test_db_exists(self):
    self.assertTrue(os.path.exists(self.db_file))

  def test_config(self):
    # no config exists
    self.assertEquals(self._storage.getConfig('config-sample'), None)
    # with default value
    self.assertEquals(self._storage.getConfig('config-sample', "tototo"), "tototo")
    # set config (stored as string)
    self.setConfig('config-test', 1458)
    self.setConfig('test-dict', dict(first=23, second="sec"))
    # values are string
    self.assertEquals(self._storage.getConfig('config-test'), "1458")
    self.assertEquals(self._storage.getConfig('test-dict'), str(dict(first=23, second="sec")))

  def test_store_CAKeypair(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)

    # check stored keypair
    stored = self._storage.getCAKeyPairList()
    self.assertEquals(len(stored), 1)
    
    self.assertTrue(self.check_cert_equal(stored[0]['crt'], keypair['crt']))
    self.assertTrue(self.check_key_equal(stored[0]['key'], keypair['key']))

  def test_store_same_keypair(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)

    # check stored keypair
    stored = self._storage.getCAKeyPairList()
    self.assertEquals(len(stored), 1)
    
    self.assertTrue(self.check_cert_equal(stored[0]['crt'], keypair['crt']))
    self.assertTrue(self.check_key_equal(stored[0]['key'], keypair['key']))

    # store again the same keypair
    with self.assertRaises(Found):
      self._storage.storeCAKeyPair(keypair)

  def test_store_keypair_multiple(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)

    # check stored keypair
    stored = self._storage.getCAKeyPairList()
    self.assertEquals(len(stored), 1)
    
    self.assertTrue(self.check_cert_equal(stored[0]['crt'], keypair['crt']))
    self.assertTrue(self.check_key_equal(stored[0]['key'], keypair['key']))

    time.sleep(1)
    keypair2 = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair2)
    stored2 = self._storage.getCAKeyPairList()
    self.assertEquals(len(stored2), 2)
    # check that order of keypair is good
    first = stored2[0]
    self.assertTrue(self.check_cert_equal(first['crt'], keypair['crt']))
    self.assertTrue(self.check_key_equal(first['key'], keypair['key']))

    second = stored2[1]
    self.assertTrue(self.check_cert_equal(second['crt'], keypair2['crt']))
    self.assertTrue(self.check_key_equal(second['key'], keypair2['key']))

  def test_storeCertificateSigningRequest(self):
    csr, key = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)

    stored = self._storage.getPendingCertificateRequest(csr_id)
    self.assertTrue(self.check_csr_equal(stored, csr))
  
  def test_deletePendingCertificateRequest(self):
    csr, key = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)

    stored = self._storage.getPendingCertificateRequest(csr_id)
    self.assertTrue(self.check_csr_equal(stored, csr))

    self._storage.deletePendingCertificateRequest(csr_id)
    with self.assertRaises(NotFound):
       self._storage.getPendingCertificateRequest(csr_id)

  def test_storeCertificateSigningRequest_no_storage(self):
    self.setConfig('max-csr-amount', self.max_request_amount)
    self.assertEquals(int(self._storage.getConfig('max-csr-amount')), self.max_request_amount)

    for i in range(0, self.max_request_amount):
      csr, _ = self.generateCSR()
      self._storage.storeCertificateSigningRequest(csr)

    # will raise NoStorage now
    csr, _ = self.generateCSR()
    with self.assertRaises(NoStorage):
      self._storage.storeCertificateSigningRequest(csr)

    csr_list = self._storage.getPendingCertificateRequestList()
    self.assertEquals(len(csr_list), self.max_request_amount)

  def store_storeCertificateSigningRequest_same(self):
    csr, key = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)

    stored = self._storage.getPendingCertificateRequest(csr_id)
    self.assertTrue(self.check_csr_equal(stored, csr))

    # store a second time the same csr
    csr2_id = self._storage.storeCertificateSigningRequest(csr)
    self.assertEquals(csr2_id, csr_id)
    stored2 = self._storage.getPendingCertificateRequest(csr2_id)
    self.assertEquals(stored2, stored)

    csr_list = self._storage.getPendingCertificateRequestList()
    # there is only on csr in the list
    self.assertEquals(len(csr_list), 1)

  def test_storeCertificate(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    csr, _ = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)
    cert = self.createCertificate(keypair, csr)

    cert_id = self._storage.storeCertificate(csr_id, cert)

    stored = self._storage.getCertificate(cert_id)
    self.assertTrue(self.check_cert_equal(stored, cert))

  def test_storeCertificate_wrong_csr(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    csr, _ = self.generateCSR()
    cert = self.createCertificate(keypair, csr)
    csr_id="1234"

    # csr_id not exists
    with self.assertRaises(NotFound):
      self._storage.storeCertificate(csr_id, cert)

    csr_id = self._storage.storeCertificateSigningRequest(csr)
    self._storage.deletePendingCertificateRequest(csr_id)
    # csr was deleted
    with self.assertRaises(NotFound):
      self._storage.storeCertificate(csr_id, cert)

  def test_storeCertificate_same(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    csr, _ = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)
    cert = self.createCertificate(keypair, csr)

    cert_id = self._storage.storeCertificate(csr_id, cert)

    stored = self._storage.getCertificate(cert_id)
    self.assertTrue(self.check_cert_equal(stored, cert))

    with self.assertRaises(NotFound):
      # CSR not found
      self._storage.storeCertificate(csr_id, cert)

  def test_storeCertificate_same_csr(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    csr, _ = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)
    cert = self.createCertificate(keypair, csr)

    cert_id = self._storage.storeCertificate(csr_id, cert)

    stored = self._storage.getCertificate(cert_id)
    self.assertTrue(self.check_cert_equal(stored, cert))

    with self.assertRaises(NotFound):
      # CSR not found
      self._storage.storeCertificate(csr_id, cert)

    csr2_id = self._storage.storeCertificateSigningRequest(csr)
    self.assertNotEquals(csr2_id, csr_id)

    #with self.assertRaises(IntegrityError):
      # cannot store 2 certificate with same serial
    #  self._storage.storeCertificate(csr2_id, cert)

    # can store new certificate, using a different csr2_id from csr
    cert2 = self.createCertificate(keypair, csr)
    cert2_id = self._storage.storeCertificate(csr2_id, cert2)
    self.assertNotEquals(cert2_id, cert_id)

  def test_revokeCertificate(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    csr, _ = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)
    cert = self.createCertificate(keypair, csr)

    cert_id = self._storage.storeCertificate(csr_id, cert)
    expiration_date = datetime.strptime(cert.get_notAfter(), '%Y%m%d%H%M%SZ')
    
    self._storage.revokeCertificate(utils.getSerialToInt(cert), expiration_date)

    with self.assertRaises(NotFound):
      # certificate was revoked
      self._storage.getCertificate(cert_id)

    revocation_list = self._storage.getRevocationList()
    self.assertEquals(len(revocation_list), 1)
    self.assertEquals(revocation_list[0].serial, utils.getSerialToInt(cert))
    self.assertEquals(revocation_list[0].crt_expire_after, expiration_date)

  def test_revokeCertificate_not_exists(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    csr, _ = self.generateCSR()
    csr_id = self._storage.storeCertificateSigningRequest(csr)
    cert = self.createCertificate(keypair, csr)

    cert_id = self._storage.storeCertificate(csr_id, cert)
    expiration_date = datetime.strptime(cert.get_notAfter(), '%Y%m%d%H%M%SZ')

    revocation_list = self._storage.getRevocationList()
    self.assertEquals(revocation_list, [])

    self._storage.revokeCertificate(utils.getSerialToInt(cert), expiration_date)

    with self.assertRaises(NotFound):
      # certificate was revoked
      self._storage.revokeCertificate(utils.getSerialToInt(cert), expiration_date)

  def test_storeCertificateRevocation_with_expired(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    def store_cert(expire_sec):
      csr, _ = self.generateCSR()
      csr_id = self._storage.storeCertificateSigningRequest(csr)
      cert = self.createCertificate(keypair, csr, expire_sec=expire_sec)
  
      cert_id = self._storage.storeCertificate(csr_id, cert)
      return cert_id, cert
    
    id1, cert1 = store_cert(5)
    id2, cert2 = store_cert(260)
    id3, cert3 = store_cert(180)

    expiration_date1 = datetime.strptime(cert1.get_notAfter(), '%Y%m%d%H%M%SZ')
    expiration_date3 = datetime.strptime(cert3.get_notAfter(), '%Y%m%d%H%M%SZ')
    self._storage.revokeCertificate(utils.getSerialToInt(cert1), expiration_date1)
    self._storage.revokeCertificate(utils.getSerialToInt(cert3), expiration_date3)

    revocation_list = self._storage.getRevocationList()
    self.assertEquals(len(revocation_list), 2)

    stored_cert = self._storage.getCertificate(id2)
    self.assertTrue(self.check_cert_equal(stored_cert, cert2))

    for i in [0, 1]:
      if revocation_list[0].serial == utils.getSerialToInt(cert1):
        self.assertEquals(revocation_list[0].crt_expire_after, expiration_date1)
        revocation_list.pop(0)
      elif revocation_list[0].serial == utils.getSerialToInt(cert3):
        self.assertEquals(revocation_list[0].crt_expire_after, expiration_date3)
        revocation_list.pop(0)

    # All items was removed with pop(0)
    self.assertEquals(revocation_list, [])

    time.sleep(5)
    revocation_list = self._storage.getRevocationList()
    # revoked cert1 certificate has expired notAfter
    self.assertEquals(len(revocation_list), 1)
    self.assertEquals(revocation_list[0].serial, utils.getSerialToInt(cert3))

    with self.assertRaises(NotFound):
      self._storage.getCertificate(id1)

  def test_getNextCRLVersionNumber(self):
    serial = self._storage.getNextCRLVersionNumber()
    self.assertEquals(serial, 1)

  

  def test_storeCertificateRevocationList(self):
    keypair = self.createCAKeyPair()
    self._storage.storeCAKeyPair(keypair)
    def store_cert(expire_sec):
      csr, _ = self.generateCSR()
      csr_id = self._storage.storeCertificateSigningRequest(csr)
      cert = self.createCertificate(keypair, csr, expire_sec=expire_sec)
  
      cert_id = self._storage.storeCertificate(csr_id, cert)
      return cert_id, cert
    
    id1, cert1 = store_cert(60)
    id2, cert2 = store_cert(260)
    id3, cert3 = store_cert(180)

    expiration_date1 = datetime.strptime(cert1.get_notAfter(), '%Y%m%d%H%M%SZ')
    expiration_date3 = datetime.strptime(cert3.get_notAfter(), '%Y%m%d%H%M%SZ')
    self._storage.revokeCertificate(utils.getSerialToInt(cert1), expiration_date1)
    self._storage.revokeCertificate(utils.getSerialToInt(cert3), expiration_date3)
    revocation_list = self._storage.getRevocationList()
    self.assertEquals(len(revocation_list), 2)

    crl = self.generateCRL(keypair, revocation_list, 1)
    self._storage.storeCertificateRevocationList(
            crl,
            expiration_date=(datetime.utcnow() + timedelta(0, 160))
          )

    stored = self._storage.getCertificateRevocationList()
    self.assertNotEqual(stored, None)
    crl_string = crypto.dump_crl(crypto.FILETYPE_PEM, crl)
    self.assertEquals(crl_string, stored)

  def test_getCertificateRevocationList_empty(self):
    keypair = self.createCAKeyPair()
    crl = self._storage.getCertificateRevocationList()
    self.assertEqual(crl, None)

    crl = self.generateCRL(keypair, [], 1)
    self._storage.storeCertificateRevocationList(
            crl,
            expiration_date=(datetime.utcnow() + timedelta(0, 3))
          )

    stored = self._storage.getCertificateRevocationList()
    self.assertNotEqual(stored, None)
    crl_string = crypto.dump_crl(crypto.FILETYPE_PEM, crl)
    self.assertEquals(crl_string, stored)

    time.sleep(4)
    stored = self._storage.getCertificateRevocationList()
    # crl is not valid anymore
    self.assertEqual(stored, None)
    
  def test_housekeep(self):
    from caucase.storage import CertificateRequest, Certificate, CAKeypair, CertificateRevocationList, Revocation
    self.setConfig('crt-keep-time', 5)
    self.setConfig('csr-keep-time', 5)
    # ca cert expire after 4 seconds
    keypair = self.createCAKeyPair(5)
    self._storage.storeCAKeyPair(keypair)

    time.sleep(1)
    keypair2 = self.createCAKeyPair(15)
    self._storage.storeCAKeyPair(keypair2)
    self.assertEquals(len(self._storage.getCAKeyPairList()), 2)
    def store_cert(expire_sec):
      csr, _ = self.generateCSR()
      csr_id = self._storage.storeCertificateSigningRequest(csr)
      cert = self.createCertificate(keypair, csr, expire_sec=expire_sec)

      cert_id = self._storage.storeCertificate(csr_id, cert)
      return cert_id, cert

    id1, cert1 = store_cert(4)
    id2, cert2 = store_cert(4)
    id3, cert3 = store_cert(8)

    expiration_date1 = datetime.strptime(cert2.get_notAfter(), '%Y%m%d%H%M%SZ')

    self._storage.revokeCertificate(utils.getSerialToInt(cert2), expiration_date1)
    revocation_list = self._storage.getRevocationList()
    self.assertEquals(len(revocation_list), 1)
    crl = self.generateCRL(keypair, revocation_list, 2)
    self._storage.storeCertificateRevocationList(
            crl,
            expiration_date=(datetime.utcnow() + timedelta(0, 4))
          )

    time.sleep(2)
    id_4, cert4 = store_cert(10)
    id_5, cert5 = store_cert(10)
    expiration_date3 = datetime.strptime(cert4.get_notAfter(), '%Y%m%d%H%M%SZ')

    self._storage.revokeCertificate(utils.getSerialToInt(cert4), expiration_date3)
    revocation_list = self._storage.getRevocationList()
    self.assertEquals(len(revocation_list), 2)
    crl2 = self.generateCRL(keypair, revocation_list, 3)
    self._storage.storeCertificateRevocationList(
            crl,
            expiration_date=(datetime.utcnow() + timedelta(0, 10))
          )

    time.sleep(3)
    crl_list = CertificateRevocationList.query.filter().all()
    self.assertEquals(len(crl_list), 2)
    revocation_list = Revocation.query.filter().all()
    self.assertEquals(len(revocation_list), 2)

    self._storage.housekeep()
    # One key_pair is expired
    stored = self._storage.getCAKeyPairList()
    self.assertEquals(len(stored), 1)
    self.assertTrue(self.check_cert_equal(stored[0]['crt'], keypair2['crt']))
    self.assertTrue(self.check_key_equal(stored[0]['key'], keypair2['key']))

    csr_count = CertificateRequest.query.filter().count()
    # 3 csr should be removed
    self.assertEquals(csr_count, 2)
    with self.assertRaises(NotFound):
      self._storage.getCertificate(id1)
      self._storage.getCertificate(id2)
      self._storage.getCertificate(id3)

    with self.assertRaises(NotFound):
      # this certificate is revoked
      self._storage.getCertificate(id_4)

    # content still exists (keep-time not expired)
    self._storage.getCertificate(id_5)
    # certificate informations are not remove
    cert_count = Certificate.query.filter().count()
    self.assertEquals(cert_count, 5)

    revocation_list = Revocation.query.filter().all()
    self.assertEquals(len(revocation_list), 1)
    self.assertTrue(revocation_list[0].serial == utils.getSerialToInt(cert4))

    # one crl is removed
    crl_list = CertificateRevocationList.query.filter().all()
    self.assertEquals(len(crl_list), 1)


