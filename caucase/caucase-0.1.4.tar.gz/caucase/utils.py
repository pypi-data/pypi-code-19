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

from caucase.exceptions import BadSignature, CertificateVerificationError
from OpenSSL import crypto, SSL
from pyasn1.codec.der import encoder as der_encoder
from pyasn1.type import tag
from pyasn1_modules import rfc2459

class GeneralNames(rfc2459.GeneralNames):
    """
    rfc2459 has wrong tagset.
    """
    tagSet = tag.TagSet(
        (),
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0),
        )

class DistributionPointName(rfc2459.DistributionPointName):
    """
    rfc2459 has wrong tagset.
    """
    tagSet = tag.TagSet(
        (),
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0),
        )

class ExtensionType():

  CRL_DIST_POINTS = "crlDistributionPoints"
  BASIC_CONSTRAINTS = "basicConstraints"
  KEY_USAGE = "keyUsage"
  NS_CERT_TYPE = "nsCertType"
  NS_COMMENT = "nsComment"
  SUBJECT_KEY_ID = "subjectKeyIdentifier"
  AUTH_KEY_ID = "authorityKeyIdentifier"


class X509Extension(object):

  known_extension_list = [name for (attr, name) in vars(ExtensionType).items()
                      if attr.isupper()]

  def setX509Extension(self, ext_type, critical, value, subject=None, issuer=None):
    if not ext_type in self.known_extension_list:
      raise ValueError('Extension type is not known from ExtensionType class')

    if ext_type == ExtensionType.CRL_DIST_POINTS:
      cdp = self._getCrlDistPointExt(value)
      return crypto.X509Extension(
        b'%s' % ext_type,
        critical,
        'DER:' + cdp.encode('hex'),
        subject=subject,
        issuer=issuer,
      )
    else:
      return crypto.X509Extension(
        ext_type,
        critical,
        value,
        subject=subject,
        issuer=issuer,
      )

  def _getCrlDistPointExt(self, cdp_list):
    cdp = rfc2459.CRLDistPointsSyntax()
    position = 0
    for cdp_type, cdp_value in cdp_list:
      cdp_entry = rfc2459.DistributionPoint()
      general_name = rfc2459.GeneralName()

      if not cdp_type in ['dNSName', 'directoryName', 'uniformResourceIdentifier']:
        raise ValueError("crlDistributionPoints GeneralName '%s' is not valid" % cdp_type)

      general_name.setComponentByName(cdp_type, cdp_value)

      general_names = GeneralNames()
      general_names.setComponentByPosition(0, general_name)

      name = DistributionPointName()
      name.setComponentByName('fullName', general_names)
      cdp_entry.setComponentByName('distributionPoint', name)

      cdp.setComponentByPosition(position, cdp_entry)
      position += 1

    return der_encoder.encode(cdp)

  def setCaExtensions(self, cert_obj):
    """
      extensions for default certificate
    """
    cert_obj.add_extensions([
      self.setX509Extension(ExtensionType.BASIC_CONSTRAINTS, True,
                                                          "CA:TRUE, pathlen:0"),
      self.setX509Extension(ExtensionType.NS_COMMENT,
                                              False, "OpenSSL CA Certificate"),
      self.setX509Extension(ExtensionType.KEY_USAGE,
                                                 True, "keyCertSign, cRLSign"),
      self.setX509Extension(ExtensionType.SUBJECT_KEY_ID,
                                                False, "hash", subject=cert_obj),
    ])
    cert_obj.add_extensions([
      self.setX509Extension(ExtensionType.AUTH_KEY_ID,
                                  False, "keyid:always,issuer", issuer=cert_obj)
    ])

  def setDefaultExtensions(self, cert_obj, subject=None, issuer=None, crl_url=None):
    """
      extensions for default certificate
    """
    cert_obj.add_extensions([
      self.setX509Extension(ExtensionType.BASIC_CONSTRAINTS, False, "CA:FALSE"),
      self.setX509Extension(ExtensionType.NS_COMMENT,
                                        False, "OpenSSL Generated Certificate"),
      self.setX509Extension(ExtensionType.SUBJECT_KEY_ID,
                                                False, "hash", subject=subject),
    ])
    cert_obj.add_extensions([
      self.setX509Extension(ExtensionType.AUTH_KEY_ID,
                                          False, "keyid,issuer", issuer=issuer)
    ])
    if crl_url:
      cert_obj.add_extensions([
        self.setX509Extension(ExtensionType.CRL_DIST_POINTS,
                          False, [("uniformResourceIdentifier", crl_url)])
      ])

  def setDefaultCsrExtensions(self, cert_obj, subject=None, issuer=None):
    """
      extensions for certificate signature request
    """
    cert_obj.add_extensions([
      self.setX509Extension(ExtensionType.BASIC_CONSTRAINTS, False, "CA:FALSE"),
      self.setX509Extension(ExtensionType.KEY_USAGE,
                    False, "nonRepudiation, digitalSignature, keyEncipherment"),
    ])

def getSerialToInt(x509):
  return '{0:x}'.format(int(x509.get_serial_number()))

def validateCertAndKey(cert_pem, key_pem):
  ctx = SSL.Context(SSL.TLSv1_METHOD)
  ctx.use_privatekey(key_pem)
  ctx.use_certificate(cert_pem)
  try:
    ctx.check_privatekey()
  except SSL.Error:
    return False
  else:
    return True

def verifyCertificateChain(cert_pem, trusted_cert_list, crl=None):

  # Create and fill a X509Sore with trusted certs
  store = crypto.X509Store()
  for trusted_cert in trusted_cert_list:
    store.add_cert(trusted_cert)

  if crl:
    store.add_crl(crl)
    store.set_flags(crypto.X509StoreFlags.CRL_CHECK)

  store_ctx = crypto.X509StoreContext(store, cert_pem)
  # Returns None if certificate can be validated
  try:
    result = store_ctx.verify_certificate()
  except crypto.X509StoreContextError, e:
    raise CertificateVerificationError('Certificate verification error: %s' % str(e))
  except crypto.Error, e:
    raise CertificateVerificationError('Certificate verification error: %s' % str(e))

  if result is None:
    return True
  else:
    return False

def checkCertificateValidity(ca_cert_list, cert_pem, key_pem=None):

  if not verifyCertificateChain(cert_pem, ca_cert_list):
    return False
  if key_pem:
    return validateCertAndKey(cert_pem, key_pem)
  return True

def sign(data, key, digest="sha256"):
  """
    Sign a data using digest and return signature.
  """
  pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key)

  sign = crypto.sign(pkey, data, digest)
  #data_base64 = base64.b64encode(sign)

  return sign

def verify(data, cert_string, signature, digest="sha256"):
  """
    Verify the signature for a data string.

    cert_string: is the certificate content as string
    signature: is generate using 'signData' from the data to verify
    data: content to verify
    digest: by default is sha256, set the correct value
  """
  x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert_string)
  return crypto.verify(x509, signature, data, digest.encode("ascii", 'ignore'))

def wrap(payload, key, digest_list):
  """
  Sign payload (json-serialised) with key, using one of the given digests.
  """
  # Choose a digest between the ones supported
  # how to choose the default digest ?
  digest = digest_list[0]
  payload = json.dumps(payload)
  return {
    "payload": payload,
    "digest": digest,
    "signature": sign(payload + digest + ' ', key, digest).encode('base64'),
  }

def unwrap(wrapped, getCertificate, digest_list):
  """
  Raise if signature does not match payload. Returns payload.
  """
  # Check whether given digest is allowed
  if wrapped['digest'] not in digest_list:
    raise BadSignature('Given digest is not supported')
  payload = json.loads(wrapped['payload'])
  crt = getCertificate(payload)
  try:
    verify(wrapped['payload'] + wrapped['digest'] + ' ', crt, wrapped['signature'].decode('base64'), wrapped['digest'])
  except crypto.Error, e:
    raise BadSignature('Signature mismatch: %s' % str(e))
  return payload

