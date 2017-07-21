# -*- coding: utf-8 -*-
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


import json
import os
import sys
import subprocess
import re
import time
import uuid
import errno
import tempfile
from OpenSSL import crypto, SSL
import traceback
from pyasn1.codec.der import encoder as der_encoder
from pyasn1.type import tag
from pyasn1_modules import rfc2459
from datetime import datetime, timedelta
from caucase.exceptions import (ExpiredCertificate, NotFound,
                      BadCertificateSigningRequest, CertificateVerificationError)

from caucase import utils

MIN_CA_RENEW_PERIOD = 2
DEFAULT_DIGEST_LIST = ['sha256', 'sha384', 'sha512']
SUBJECT_KEY_LIST = ['C', 'ST', 'L', 'OU', 'O', 'CN', 'emailAddress']

def getX509NameFromDict(**name_dict):
  """
  Return a new X509Name with the given attributes.
  """
  # XXX There's no other way to get a new X509Name.
  name = crypto.X509().get_subject()

  for key, value in name_dict.items():
    setattr(name, key, value)
  return name

class CertificateAuthority(object):
  def __init__(self, storage, ca_life_period, ca_renew_period,
                crt_life_time, crl_renew_period, digest_list=None,
                crl_base_url=None, ca_subject='',
                max_csr_amount=50, crt_keep_time=0,
                auto_sign_csr_amount=0):
    self._storage = storage
    self.ca_life_period = ca_life_period
    self.digest_list = digest_list
    self.crt_life_time = crt_life_time
    self.crl_renew_period = crl_renew_period
    self.ca_renew_period = ca_renew_period
    self.default_digest = 'sha256'
    self.crl_base_url = crl_base_url
    self.auto_sign_csr_amount = auto_sign_csr_amount
    self.extension_manager = utils.X509Extension()

    self.mandatory_subject_key_list = ['CN']

    self.ca_subject_dict = self._getCASubjectDict(ca_subject)
    # XXX - ERR_SSL_SERVER_CERT_BAD_FORMAT on browser
    # Because if two certificate has the same serial from a CA with the same CN
    # self.ca_subject_dict['CN'] = '%s %s' % (self.ca_subject_dict['CN'], int(time.time()))

    if not self.digest_list:
      self.digest_list = DEFAULT_DIGEST_LIST

    if self.ca_life_period < MIN_CA_RENEW_PERIOD:
      raise ValueError("'ca_life_period' value should be upper than %s" % MIN_CA_RENEW_PERIOD)
    if self.crl_renew_period > 1:
      raise ValueError("'crl_renew_period' is too high and should be less than a certificate life time.")

    self.crl_life_time = int(self.crt_life_time * self.crl_renew_period)
    self.ca_life_time = int(self.crt_life_time * self.ca_life_period)
    self.ca_renew_time = int(self.crt_life_time * self.ca_renew_period)

    self._ca_key_pairs_list = self._storage.getCAKeyPairList()
    if not self._ca_key_pairs_list:
      self.createCAKeyPair()

  def _getCASubjectDict(self, ca_subject):
    """
      Parse CA Subject from provided sting format
      
      Ex: /C=XX/ST=State/L=City/OU=OUnit/O=Company/CN=CA Auth/emailAddress=xx@example.com
    """
    ca_subject_dict = {}

    regex = r"\/([C|ST|L|O|OU|CN|emailAddress]+)=([\w\s\@\.\d\-_\(\)\,\+:']+)"

    matches = re.finditer(regex, ca_subject)
    for match in matches:
      key = match.group(1)
      if not key in SUBJECT_KEY_LIST:
        raise ValueError("Item %r is not a valid CA Subject key, please" \
                          "Check that the provided key is in %s" % (key,
                            SUBJECT_KEY_LIST))
      ca_subject_dict[key] = match.group(2)

    for key in self.mandatory_subject_key_list:
      if key not in ca_subject_dict:
        raise ValueError("The subject key '%r' is mandatory." % key)

    return ca_subject_dict

  def renewCAKeyPair(self):
    """
    Refresh instance's knowledge of database content
    (as storage house-keeping may/will happen outside our control)
    """

    cert = self._ca_key_pairs_list[-1]['crt']
    expire_date = datetime.strptime(cert.get_notAfter(), '%Y%m%d%H%M%SZ')
    renew_date = expire_date - timedelta(0, self.ca_renew_time)

    if renew_date > datetime.now():
      # The ca certificat should not be renewed now
      return False

    self.createCAKeyPair()
    return True

  def createCAKeyPair(self):
    """
    Create a new ca key + certificate pair
    """
    key_pair = {}
    key = crypto.PKey()
    # Use 2048 bits key size
    key.generate_key(crypto.TYPE_RSA, 2048)

    key_pair['key'] = key

    ca = crypto.X509()
    # 3 = v3
    ca.set_version(3)
    ca.set_serial_number(int(time.time()))
    subject = ca.get_subject()
    for name, value in self.ca_subject_dict.items():
      setattr(subject, name, value)

    ca.gmtime_adj_notBefore(0)
    ca.gmtime_adj_notAfter(self.ca_life_time)
    ca.set_issuer(ca.get_subject())
    ca.set_pubkey(key)
    self.extension_manager.setCaExtensions(ca)
    ca.sign(key, self.default_digest)
    key_pair['crt'] = ca

    self._storage.storeCAKeyPair(key_pair)
    self._ca_key_pairs_list = self._storage.getCAKeyPairList()
    assert self._ca_key_pairs_list

  def getPendingCertificateRequest(self, csr_id):
    """
    Retrieve the content of a pending signing request.
    
    @param csr_id: The id of CSR returned by the storage
    """
    return self._storage.getPendingCertificateRequest(csr_id)

  def createCertificateSigningRequest(self, csr):
    """
    Sanity-check CSR, stores it and generates a unique signing request
    identifier (crt_id).
    
    @param csr: CSR string in PEM format
    """
    # Check number of already-pending signing requests
    # Check if csr is self-signed
    # Check it has a CN (?)
    # Check its extensions
    # more ?
    try:
      csr_pem = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr)
    except crypto.Error, e:
      raise BadCertificateSigningRequest(str(e))

    if not hasattr(csr_pem.get_subject(), 'CN')  or not csr_pem.get_subject().CN:
      raise BadCertificateSigningRequest("CSR has no common name set")

    # XXX check extensions

    csr_id = self._storage.storeCertificateSigningRequest(csr_pem)
    if self._storage.getCertificateSigningRequestAmount() <=  \
            self.auto_sign_csr_amount:
      # if allowed to sign this certificate automaticaly
      self.createCertificate(csr_id)
    return csr_id

  def deletePendingCertificateRequest(self, csr_id):
    """
    Reject a pending certificate signing request.
    
    @param csr_id: The id of CSR returned by the storage
    """
    self._storage.deletePendingCertificateRequest(csr_id)

  def getPendingCertificateRequestList(self, limit=0, with_data=False):
    """
      Return list of pending certificate signature request
      
      @param limit: number of element to fetch, 0 is not limit (int)
      @param with_data: True or False, say if return csr PEM string associated
        to others informations (bool).
    """
    return self._storage.getPendingCertificateRequestList(limit, with_data)

  def createCertificate(self, csr_id, ca_key_pair=None, subject_dict=None):
    """
      Generate new signed certificate. `ca_key_pair` is the CA key_pair to use
        if None, use the latest CA key_pair
      
      @param csr_id: CSR ID returned by storage, csr should be linked to the 
          new certificate (string).
      @param ca_key_pair: The CA key_pair to used for signature. If None, the
          latest key_pair is used.
      @param subject_dict: dict of subject attributes to use in x509 subject,
          if None, csr subject is used (dict).
    """
    # Apply extensions (ex: "not a certificate", ...)
    # Generate a certificate from the CSR
    # Sign the certificate with the current CA key

    csr_pem = crypto.load_certificate_request(crypto.FILETYPE_PEM,
                    self._storage.getPendingCertificateRequest(csr_id))

    # Certificate serial is the csr_id without extension .csr.pem
    serial = int(csr_id[:-8], 16)
    subject = None
    if ca_key_pair is None:
      ca_key_pair = self._ca_key_pairs_list[-1]
    if subject_dict:
      if subject_dict.has_key('C') and len(subject_dict['C']) != 2:
        # Country code size is 2
        raise ValueError("Country Code size in subject should be equal to 2.")
      if not subject_dict.has_key('CN'):
        raise AttributeError("Attribute 'CN' is required in subject.")
      try:
        subject = getX509NameFromDict(**subject_dict)
      except AttributeError:
        raise AttributeError("X509Name attribute not found. Subject " \
                         "keys should be in %r" % SUBJECT_KEY_LIST)
    cert_pem = self._generateCertificateObjects(ca_key_pair,
                                                csr_pem,
                                                serial,
                                                subject=subject)

    crt_id = self._storage.storeCertificate(csr_id, cert_pem)
    return crt_id

  def getCertificate(self, crt_id):
    """
      Return a Certificate string in PEM format
      
      @param crt_id: Certificate ID returned by storage during certificate creation
    """
    return self._storage.getCertificate(crt_id)

  def getCertificateFromSerial(self, serial):
    """
      Return a Certificate string in PEM format
      
      @param serial: serial of the certificate (string)
    """
    cert =  self._storage.getCertificateFromSerial(serial)
    if not cert.content:
      raise NotFound('Content certificate with serial %r is not found.' % (
                      serial,
                    ))
    return cert.content

  def getSignedCertificateList(self, limit=0, with_data=False):
    """
      Return list of signed certificate
      
      @param limit: number of element to fetch, 0 is not limit (int)
      @param with_data: True or False, say if return cert PEM string associated
        to others informations (bool).
    """
    return self._storage.getSignedCertificateList(limit, with_data)

  def getCACertificate(self):
    """
    Return current CA certificate
    """
    return self._dumpCertificate(self._ca_key_pairs_list[-1]['crt'])

  def getValidCACertificateChain(self):
    """
      Return the ca certificate chain for all valid certificates with key
    """
    result = []
    iter_key_pair = iter(self._ca_key_pairs_list)
    previous_key_pair = iter_key_pair.next()
    for key_pair in iter_key_pair:
      result.append(utils.wrap({
        'old': self._dumpCertificate(previous_key_pair['crt']),
        'new': self._dumpCertificate(key_pair.crt),
      }, self._dumpPrivatekey(previous_key_pair['key']), self.digest_list))
    return result

  def getCAKeypairForCertificate(self, cert):
    """
      Return the nearest CA key_pair to the next extension date of the cert
      
      @param cert: X509 certificate
    """
    cert_valid_date = datetime.strptime(cert.get_notAfter(), '%Y%m%d%H%M%SZ')
    next_valid_date =  datetime.utcnow() + timedelta(0, self.crt_life_time)
    # check which ca certificate should be used to renew the cert
    selected_keypair = None
    selected_date = None
    for key_pair in self._ca_key_pairs_list:
      expiration_date = datetime.strptime(key_pair['crt'].get_notAfter(), '%Y%m%d%H%M%SZ')
      if expiration_date < next_valid_date:
        continue
      if selected_date and selected_date < expiration_date:
        # Only get the lowest expiration_date which cover the renew notbefore date
        continue
      selected_keypair = key_pair
      selected_date = expiration_date

    if selected_keypair is None:
      raise ValueError("No valid CA key_pair found with validity date upper than %r certificate lifetime" % 
          next_valid_date)

    return selected_keypair

  def revokeCertificate(self, wrapped_crt):
    """
      Revoke a certificate
      
      @param wrapped_crt: The revoke request dict containing certificate to
        revoke and signature algorithm used to sign the request.
        {
          "signature": "signature string for payload",
          "digest": "Signature algorithm (ex: SHA256"),
          "payload": dict of data: {
              "revoke_crt": "Certificate to revoke",
              "reason": "Revoke reason"
            }
        }
    """
    payload = utils.unwrap(wrapped_crt, lambda x: x['revoke_crt'], self.digest_list)

    try:
      x509 = self._loadCertificate(payload['revoke_crt'])
    except crypto.Error, e:
      raise BadCertificate(str(e))

    if not utils.verifyCertificateChain(x509,
                                  [x['crt'] for x in self._ca_key_pairs_list]):
      raise CertificateVerificationError("Certificate verification failed:" \
                "The CA couldn't reconize the certificate to revoke.")

    crt = self._loadCertificate(payload['revoke_crt'])
    reason = payload['reason']
    return self._storage.revokeCertificate(
              utils.getSerialToInt(crt),
              reason)

  def revokeCertificateFromID(self, crt_id):
    """
      Directly revoke a certificate from crt_id
      
      @param crt_id: The ID of the certificate (string)
    """
    
    return self._storage.revokeCertificate(
              crt_id=crt_id,
              reason="")

  def renew(self, wrapped_csr):
    """
      Renew a certificate
      
      @param wrapped_csr: The revoke request dict containing certificate to
        revoke and signature algorithm used to sign the request.
        {
          "signature": "signature string for payload",
          "digest": "Signature algorithm (ex: SHA256"),
          "payload": dict of data: {
              "crt": "Old certificate to renew",
              "renew_csr": "New CSR to sign"
            }
        }
    """
    payload = utils.unwrap(wrapped_csr, lambda x: x['crt'], self.digest_list)
    csr = payload['renew_csr']

    try:
      x509 = self._loadCertificate(payload['crt'])
    except crypto.Error, e:
      raise BadCertificate(str(e))

    try:
      csr_pem = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr)
    except crypto.Error, e:
      raise BadCertificateSigningRequest(str(e))

    if csr_pem.get_subject().CN != x509.get_subject().CN:
      raise BadCertificateSigningRequest(
              "Request common name does not match replaced certificate.")

    if not self._storage.getCertificateFromSerial(utils.getSerialToInt(x509)):
      raise NotFound('No Certificate with serial %r and Common Name %r found.' % (
                      x509.get_serial_number(),
                      x509.get_subject().CN,
                    ))

    if not utils.verifyCertificateChain(x509,
                                  [x['crt'] for x in self._ca_key_pairs_list]):
      raise CertificateVerificationError("Certificate verification failed:" \
                "The CA couldn't reconize signed certificate.")

    csr_id = self.createCertificateSigningRequest(csr)
    # sign the new certificate using a specific ca key_pair
    ca_key_pair = self.getCAKeypairForCertificate(x509)
    self.createCertificate(csr_id, ca_key_pair)
    return csr_id

  def getCertificateRevocationList(self):
    """
    Generate certificate revocation list PEM
    """
    crl = self._storage.getCertificateRevocationList()
    if not crl:
      # Certificate revocation list needs to be regenerated
      return self._createCertificateRevocationList()

    return crl

  def _loadCertificate(self, cert_string):
    """
      Load certificate in PEM format
    """
    return crypto.load_certificate(crypto.FILETYPE_PEM, cert_string)

  def _dumpCertificate(self, cert_object):
    """
      Dump certificate in PEM format
    """
    return crypto.dump_certificate(crypto.FILETYPE_PEM, cert_object)

  def _loadPrivatekey(self, pkey):
    """
      Load private key in PEM format
    """
    return crypto.load_privatekey(crypto.FILETYPE_PEM, pkey)

  def _dumpPrivatekey(self, pkey_object):
    """
      Load private key in PEM format
    """
    return crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey_object)

  def _generateCertificateObjects(self, ca_key_pair, req, serial, subject=None):
    """
      Generate certificate from CSR PEM Object.
      This method set default certificate extensions, later will allow to set custom extensions
      
      ca_key_pair: ca_key_pair which should be used to sign certificate
      req: csr object to sign
      serial: serial to apply to the new signed certificate
      subject: give a dict containing new subject to apply on signed certificate
      
      if subject is None, req.get_subject() is used.
    """

    if subject is None:
      subject = req.get_subject()
    # Here comes the actual certificate
    cert = crypto.X509()
    # version v3
    cert.set_version(2)
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(self.crt_life_time)
    cert.set_issuer(ca_key_pair['crt'].get_subject())
    cert.set_subject(subject)
    cert.set_pubkey(req.get_pubkey())
    self.extension_manager.setDefaultExtensions(
      cert,
      subject=cert,
      issuer=ca_key_pair['crt'],
      crl_url=self.crl_base_url)
    cert.sign(ca_key_pair['key'], self.default_digest)

    return cert

  def _createCertificateRevocationList(self):
    """
      Create CRL from certification revocation_list and return a PEM string content
    """

    revocation_list = self._storage.getRevocationList()
    now = datetime.utcnow()
    crl = crypto.CRL()

    # XXX - set_nextUpdate() doesn't update Next Update in generated CRL,
    #        So we have used export() which takes the number of days in param
    #
    # next_date = now + timedelta(0, 864000) #self.crl_life_time)
    # crl.set_lastUpdate(now.strftime("%Y%m%d%H%M%SZ").encode("ascii"))
    # crl.set_nextUpdate(next_date.strftime("%Y%m%d%H%M%SZ").encode("ascii"))

    num_crl_days = int(round(self.crl_life_time/(24.0*60*60), 0))
    if num_crl_days == 0:
      # At least one day
      num_crl_days = 1

    for revocation in revocation_list:
      revoked = crypto.Revoked()
      revoked.set_rev_date(
          revocation.creation_date.strftime("%Y%m%d%H%M%SZ").encode("ascii")
        )
      revoked.set_serial(revocation.serial.encode("ascii"))
      revoked.set_reason(None) #b'%s' % revocation.reason)
      crl.add_revoked(revoked)

    version_number = self._storage.getNextCRLVersionNumber()
    crl.set_version(version_number)
    # XXX - set how to get the cacert here
    cert = self._ca_key_pairs_list[-1]['crt']
    key = self._ca_key_pairs_list[-1]['key']

    #crl.sign(cert, key, self.default_digest)
    dumped_crl = crl.export(
          cert,
          key,
          type=crypto.FILETYPE_PEM,
          days=num_crl_days,
          digest=self.default_digest)

    return self._storage.storeCertificateRevocationList(
                    crypto.load_crl(crypto.FILETYPE_PEM, dumped_crl),
                    expiration_date=(now + timedelta(num_crl_days, 0))
                  )


