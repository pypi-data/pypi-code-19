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

import os, errno
import time
import ConfigParser
import logging
import requests
import argparse
import traceback
import pem
import json
import subprocess
import hashlib
from OpenSSL import crypto
from caucase import utils
from datetime import datetime, timedelta

CSR_KEY_FILE = 'csr.key.txt'
RENEW_CSR_KEY_FILE = 'renew_csr.key.txt'

def popenCommunicate(command_list):
  subprocess_kw = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  popen = subprocess.Popen(command_list, **subprocess_kw)
  result = popen.communicate()[0]
  if popen.returncode is None:
    popen.kill()
  if popen.returncode != 0:
    raise ValueError('Issue during calling %r, result was:\n%s' % (
      command_list, result))
  return result

def parseArguments():
  """
  Parse arguments for Certificate Authority Request.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--ca-url',
                      required=True,
                      help='Certificate Authority URL')
  parser.add_argument('-c', '--ca-crt-file',
                      default='ca.crt.pem',
                      help='Path for CA Cert file. default: %(default)s')
  parser.add_argument('-x', '--crt-file',
                      default='crt.pem',
                      help='Path for Certificate file. default: %(default)s')
  parser.add_argument('-k', '--key-file',
                      default='key.pem',
                      help='Path of key file. default: %(default)s')
  parser.add_argument('-s', '--csr-file',
                      default='csr.pem',
                      help='Path where to store csr file. default: %(default)s')
  parser.add_argument('-r', '--crl-file',
                      default='crl.pem',
                      help='Path where to store crl file. default: %(default)s')
  parser.add_argument('--digest',
                      default="sha256",
                      help='Digest used to sign data. default: %(default)s')

  parser.add_argument('--cn',
                      help='Common name to use when request new certificate.')

  parser.add_argument('--threshold',
                      help='The minimum remaining certificate validity time in' \
                        ' seconds after which renew of certificate can be triggered.',
                      type=int)
  parser.add_argument('--on-renew',
                      help='Path of an executable file to call after certificate'\
                          ' renewal.')
  parser.add_argument('--on-crl-update',
                      help='Path of an executable file to call after CRL '\
                          'file update.')

  parser.add_argument('--no-check-certificate',
                      action='store_false', default=True, dest='verify_certificate',
                      help='When connecting to CA on HTTPS, disable certificate verification.')

  group = parser.add_mutually_exclusive_group()
  group.add_argument('--request', action='store_true',
                      help='Request a new Certificate.')
  group.add_argument('--revoke', action='store_true',
                      help='Revoke existing certificate.')
  group.add_argument('--renew', action='store_true',
                      help='Renew current certificate and and replace with existing files.')
  group.add_argument('--update-crl', action='store_true',
                      help='Download and store the new CRL file if there was a new revocation.')

  return parser



def requestCertificate(ca_request, config):

  # download or update ca crt file
  ca_request.getCACertificateChain()

  if os.path.exists(config.crt_file):
    return

  if not os.path.exists(config.csr_file):
      csr = ca_request.generateCertificateRequest(config.key_file,
          cn=config.cn, csr_file=config.csr_file)
  else:
    csr = open(config.csr_file).read()

  ca_request.signCertificate(csr)


def revokeCertificate(ca_revoke, config):

  os.close(os.open(config.key_file, os.O_RDONLY))
  os.close(os.open(config.crt_file, os.O_RDONLY))

  # download or update ca crt file
  ca_revoke.getCACertificateChain()

  ca_revoke.revokeCertificate()

def renewCertificate(ca_renew, config, backup_dir):

  os.close(os.open(config.key_file, os.O_RDONLY))
  os.close(os.open(config.crt_file, os.O_RDONLY))

  # download or update ca crt file
  ca_renew.getCACertificateChain()

  ca_renew.renewCertificate(config.csr_file,
                            backup_dir,
                            config.threshold,
                            after_script=config.on_renew)
  

def main():
  parser = parseArguments()
  config = parser.parse_args()

  base_dir = os.path.dirname(config.crt_file)
  os.chdir(os.path.abspath(base_dir))

  if not config.ca_url:
    parser.error('`ca-url` parameter is required. Use --ca-url URL')
    parser.print_help()
    exit(1)

  ca_client = CertificateAuthorityRequest(config.key_file, config.crt_file,
          config.ca_crt_file, config.ca_url, digest=config.digest,
          verify_certificate=config.verify_certificate)

  if config.request:
    if not config.cn:
      parser.error('Option --cn is required for request.')
      parser.print_help()
      exit(1)

    requestCertificate(ca_client, config)

  elif config.revoke:
    revokeCertificate(ca_client, config)
  
  elif config.renew:
    if not config.threshold:
      parser.error('`threshold` parameter is required with renew. Use --threshold VALUE')
      parser.print_help()
      exit(1)
    backup_dir = os.path.join('.',
                      'backup-%s' % datetime.now().strftime('%Y-%m-%d-%H%M%S'))

    # cleanup
    if os.path.exists(CSR_KEY_FILE):
      os.unlink(CSR_KEY_FILE)
    if os.path.exists(config.csr_file):
      os.unlink(config.csr_file)

    renewCertificate(ca_client, config, backup_dir)
  elif config.update_crl:
    ca_client.updateCertificateRevocationList(config.crl_file,
                                              after_script=config.on_crl_update)
  else:
    parser.error('Please set one of options: --request | --revoke | --renew | --update-crl.')
    parser.print_help()
    exit(1)

class CertificateAuthorityRequest(object):

  def __init__(self, key, certificate, cacertificate, ca_url,
               max_retry=10, digest="sha256", sleep_time=5,
               verify_certificate=False, logger=None):

    self.key = key
    self.certificate = certificate
    self.cacertificate = cacertificate
    self.ca_url = ca_url
    self.logger = logger
    # maximum retry number of post/put request
    self.max_retry = max_retry
    # time to sleep before retry failed request
    self.sleep_time = sleep_time
    self.digest = digest
    self.extension_manager = utils.X509Extension()
    self.ca_certificate_list = []
    self.verify_certificate = verify_certificate

    while self.ca_url.endswith('/'):
      # remove all / at end or ca_url
      self.ca_url = self.ca_url[:-1]

    if os.path.exists(self.cacertificate):
      self.ca_certificate_list = [
          crypto.load_certificate(crypto.FILETYPE_PEM, x._pem_bytes) for x in
          pem.parse_file(self.cacertificate)
        ]
      

    if self.logger is None:
      self.logger = logging.getLogger('Caucase Client')
      self.logger.setLevel(logging.DEBUG)
      handler = logging.StreamHandler()
      handler.setLevel(logging.DEBUG)
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      handler.setFormatter(formatter)

      self.logger.addHandler(handler)

    self.generatePrivatekey(self.key)

  def _request(self, method, url, data=None):
    try:
      req = getattr(requests, method)
      kw = {}
      if data:
        kw['data'] = data
      kw['verify'] = self.verify_certificate
      return req(url, **kw)
    except requests.ConnectionError, e:
      self.logger.error("Got ConnectionError while sending request to CA. Url is %s\n%s" % (
          url, str(e)))
      return None

  def _checkCertEquals(self, first_cert, second_cert):
    """
      Say if two certificate PEM object are the same
      
      XXX - more checks should be done ?
    """

    return first_cert.set_subject().CN == second_cert.get_subject().CN and \
              first_cert.get_serial_number() == second_cert.get_serial_number()

  def _writeNewFile(self, file_path, content, mode=0644):
    fd = os.open(file_path,
                  os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_TRUNC, mode)
    try:
      os.write(fd, content)
    finally:
      os.close(fd)

  def _sendCertificateSigningRequest(self, csr_string):
    request_url = '%s/csr' % self.ca_url
    data = {'csr': csr_string}
    retry = 0
    response = self._request('put', request_url, data=data)

    while (not response or response.status_code != 201) and retry < self.max_retry:

      self.logger.error("%s: Failed to sent CSR. \n%s" % (
          response.status_code, response.text))
      self.logger.info("will retry in %s seconds..." % self.sleep_time)
      time.sleep(self.sleep_time)
      retry += 1
      response = self._request('put', request_url, data=data)

    if not response or response.status_code != 201:
      raise Exception("ERROR: failed to send CSR after %s retry." % retry)

    self.logger.info("CSR succefully sent.")
    # Get csr Location from request header: http://xxx.com/csr/key
    self.logger.debug("CSR location is: %s" % response.headers['Location'])

    csr_key = response.headers['Location'].split('/')[-1]
    with open(CSR_KEY_FILE, 'w') as fkey:
      fkey.write(csr_key)

    return csr_key

  def _sendCertificateRenewal(self, cert, csr):
    payload = dict(renew_csr=csr, crt=cert)
    pkey = open(self.key).read()
    wrapped = utils.wrap(payload, pkey, [self.digest])
    request_url = '%s/crt/renew' % self.ca_url
    data = {'payload': json.dumps(wrapped)}

    self.logger.info("Sending Certificate Renewal request...")

    response = self._request('put', request_url, data=data)
    break_code = [201, 404, 500, 404]
    retry = 1

    while response is None or response.status_code not in break_code:
      self.logger.error("%s: Failed to send renewal request. \n%s" % (
          response.status_code, response.text))
      self.logger.info("will retry in %s seconds..." % self.sleep_time)
      time.sleep(self.sleep_time)

      response = self._request('put', request_url, data=data)
      retry += 1
      if retry > self.max_retry:
        break

    if not response or response.status_code != 201:
      raise Exception("ERROR: failed to send certificate renewal request "\
                        "after %s retry.\n%s" % (
                        retry, response.text))

    csr_key = response.headers['Location'].split('/')[-1]
    with open(RENEW_CSR_KEY_FILE, 'w') as fkey:
      fkey.write(csr_key)

    return csr_key

  def _getSignedCertificate(self, crt_id):
    reply_url = '%s/crt/%s' % (self.ca_url, crt_id)
    response = self._request('get', reply_url)

    while not response or response.status_code != 200:
      time.sleep(self.sleep_time)
      response = self._request('get', reply_url)

    return response.text


  def generateCertificateRequest(self, key_file, cn,
      country='', state='', locality='', email='', organization='',
      organization_unit='', csr_file=None):
    """
      Generate certificate Signature request.
      
      Parameter `cn` is mandatory
    """

    with open(key_file) as fkey:
      key = crypto.load_privatekey(crypto.FILETYPE_PEM, fkey.read())

    req = crypto.X509Req()
    subject = req.get_subject()
    subject.CN = cn
    if country:
      subject.C = country
    if state:
      subject.ST = state
    if locality:
      subject.L = locality
    if organization:
      subject.O = organization
    if organization_unit:
      subject.OU = organization_unit
    if email:
      subject.emailAddress = email
    req.set_pubkey(key)
    self.extension_manager.setDefaultCsrExtensions(req)
    req.sign(key, self.digest)

    csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)

    if csr_file is not None:
      with open(csr_file, 'w') as req_file:
        req_file.write(csr)

      os.chmod(csr_file, 0640)

    return csr

  def generatePrivatekey(self, output_file, size=2048):
    """
      Generate private key into `output_file`
    """

    try:
      key_fd = os.open(output_file,
                       os.O_CREAT|os.O_WRONLY|os.O_EXCL|os.O_TRUNC,
                       0600)
    except OSError, e:
      if e.errno != errno.EEXIST:
        raise
    else:
      key = crypto.PKey()
      key.generate_key(crypto.TYPE_RSA, size)
      os.write(key_fd, crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
      os.close(key_fd)

  def checkCertificateValidity(self, cert):
    """
      validate the certificate PEM string with the CA Certificate and private key
    """
    cert_pem = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    pkey = open(self.key).read()
    key_pem = crypto.load_privatekey(crypto.FILETYPE_PEM, pkey)

    return utils.checkCertificateValidity(
              self.ca_certificate_list,
              cert_pem,
              key_pem)

  def isCertExpirationDateValid(self, x509, threshold):
    """
      Return True if remaning certificate valid time is second is lower than 
      the threshold value
    """
    expiration_date = datetime.strptime(
        x509.get_notAfter(), '%Y%m%d%H%M%SZ'
    )
    now_date = datetime.utcnow()
    limit_date = now_date + timedelta(0, threshold)
    expire_in = expiration_date - limit_date
    if expire_in.days > 0.0:
      return True
    return False

  def updateCACertificateChain(self):
    """
      Request to CA all valid certificates an update in to cacertificate file
      
      @note: if the CA has more that one valid certificate, the cacertificate
        file will be updated contain concatenated cert them like:
          CA_1
          CA_2
          ...
          CA_N
    """
    ca_cert_url = '%s/crt/ca.crt.json' % self.ca_url
    self.logger.info("Updating CA certificate file from %s" % ca_cert_url)
    cert_list = response_json = []
    cert_list_chain = ""
    response = self._request('get', ca_cert_url)
    while not response or response.status_code != 200:
      # sleep a bit then try again until  ca cert is ready
      time.sleep(10)
      response = self._request('get', ca_cert_url)

    response_json = json.loads(response.text)

    if len(response_json) > 0:
      iter_ca_cert = iter(response_json)
      is_valid = False
      payload = utils.unwrap(iter_ca_cert.next(), lambda x: x['old'], [self.digest])
      # check that old certificate is known
      old_x509 = crypto.load_certificate(crypto.FILETYPE_PEM, payload['old'])
      for x509 in self.ca_certificate_list:
        if self._checkCertEquals(x509, old_x509):
          is_valid = True

      if not is_valid:
        # no local certificate matches
        raise CertificateVerificationError("Updated CA Certificate chain could " \
            "not be validated using local CA Certificate at %r. \nYou can " \
            "try removing your local ca file if it was not updated for more " \
            "that a year." % self.cacertificate)

      # if not old_x509.has_expired():
      # XXX - TODO: check if expired old_x509 can break certificate validation
      cert_list.append(old_x509)
      cert_list.append(
          crypto.load_certificate(crypto.FILETYPE_PEM, payload['new'])
        )
      cert_list_chain = "%s\n%s" % (payload['old'], payload['new'])

      for next_item in iter_ca_cert:
        payload = utils.unwrap(next_item, lambda x: x['old'], [self.digest])
        old_x509 = crypto.load_certificate(crypto.FILETYPE_PEM, payload['old'])
        if self._checkCertEquals(cert_list[-1], old_x509):
          cert_list.append(
              crypto.load_certificate(crypto.FILETYPE_PEM, payload['new'])
            )
          cert_list_chain += "\n%s" % payload['new']
        else:
          raise CertificateVerificationError("Get CA Certificate chain " \
              "retourned %s \n\nbut validation of data failed" % response_json)

    # dump into file
    if not cert_list:
      # Nothing to do...
      return
    self.ca_certificate_list = cert_list
    fd = os.open(self.cacertificate, os.O_CREAT|os.O_WRONLY, 0640)
    try:
      os.write(fd, cert_list_chain)
    finally:
      os.close(fd)

  def getCACertificateChain(self):
    """
      Get CA certificate file.
      If it's the first download, get the latest valid certificate at ca.crt.pem
      else, update current cacertificate with list of valid ca certificat chain
    """

    # If cert file exists exist
    if os.path.exists(self.cacertificate) and os.stat(self.cacertificate).st_size > 0:
      # Get all valids CA certificate
      return self.updateCACertificateChain()

    ca_cert_url = '%s/crt/ca.crt.pem' % self.ca_url
    self.logger.info("getting CA certificate file %s" % ca_cert_url)
    response = None
    while not response or response.status_code != 200:
      response = self._request('get', ca_cert_url)
      if response is not None:
        try:
          x509 = crypto.load_certificate(crypto.FILETYPE_PEM, response.text)
        except crypto.Error, e:
          # XXX - we got a bad certificate, break here ?
          traceback.print_exc()
          response = None
        else:
          self.ca_certificate_list = [x509]
          break
      # sleep a bit then try again until  ca cert is ready
      time.sleep(10)

    fd = os.open(self.cacertificate,
                  os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_TRUNC, 0640)
    try:
      os.write(fd, response.text)
    finally:
      os.close(fd)

  def signCertificate(self, csr):
    """
      Send certificate signature request and wait until the certificate is
      signed.
      csr parameter is string in PEM format
    """

    if os.path.exists(self.certificate) and os.stat(self.certificate).st_size > 0:
      # exit because the certificate exists
      return

    csr_key = ""
    self.logger.info("Request signed certificate from CA...")
    if os.path.exists(CSR_KEY_FILE):
      with open(CSR_KEY_FILE) as fkey:
        csr_key = fkey.read()

    if csr_key:
      self.logger.info("Csr was already sent to CA, using csr : %s" % csr_key)
    else:
      csr_key = self._sendCertificateSigningRequest(csr)

    self.logger.info("Waiting for signed certificate...")

    # csr is xxx.csr.pem so cert is xxx.cert.pem
    certificate = self._getSignedCertificate('%s.crt.pem' % csr_key[:-8])

    self.logger.info("Validating signed certificate...")
    if not self.checkCertificateValidity(certificate):
      # certificate verification failed, should raise ?
      self.logger.warn("Certificate validation failed.\n" \
        "Please double check the signed certificate before use. Also consider" \
        "revoke it and request a new signed certificate.")

    fd = os.open(self.certificate,
                  os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_TRUNC, 0644)
    try:
      os.write(fd, certificate)
    finally:
      os.close(fd)
    self.logger.info("Certificate correctly saved at %s." % self.certificate)

  def revokeCertificate(self, message=""):
    """
      Revoke the current certificate on CA.
    """
    retry = 1

    pkey = open(self.key).read()
    cert = open(self.certificate).read()
    cert_pem = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

    payload = dict(
      reason=message,
      revoke_crt=cert)

    wrapped = utils.wrap(payload, pkey, [self.digest])
    request_url = '%s/crt/revoke' % self.ca_url
    data = {'payload': json.dumps(wrapped)}

    self.logger.info("Sending Certificate revocation request of CN: %s." % (
                      cert_pem.get_subject().CN))

    response = self._request('put', request_url, data=data)
    break_code = [201, 404, 500, 404]

    while response is None or response.status_code not in break_code:
      self.logger.error("%s: Failed to send revoke request. \n%s" % (
          response.status_code, response.text))

      self.logger.info("will retry in %s seconds..." % self.sleep_time)
      time.sleep(self.sleep_time)

      response = self._request('put', request_url, data=data)
      retry += 1
      if retry > self.max_retry:
        break

    if not response or response.status_code != 201:
      raise Exception("ERROR: failed to put revoke certificate after %s retry. Exiting..." % retry)

    self.logger.info("Certificate %s was successfully revoked." % (
                      self.certificate))

  def renewCertificate(self, csr_file, backup_dir, threshold, renew_key=True,
                      after_script=''):
    """
    Renew the current certificate. Regenerate private key if renew_key is `True`
    """
    
    new_key_path = '%s.renew' % self.key
    new_cert_path = '%s.renew' % self.certificate
    key_file = self.key
    cert = open(self.certificate).read()
    cert_pem = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    csr_key = ""

    if self.isCertExpirationDateValid(cert_pem, threshold):
      self.logger.info("Nothing to do, no need to renew the certificate.")
      return

    try:
      if renew_key:
        self.generatePrivatekey(new_key_path)
        key_file = new_key_path

      if os.path.exists(RENEW_CSR_KEY_FILE):
        csr_key = open(RENEW_CSR_KEY_FILE).read()

      if not csr_key:
        if not os.path.exists(csr_file):
          csr = self.generateCertificateRequest(key_file,
                                                cn=cert_pem.get_subject().CN,
                                                csr_file=csr_file)
        else:
          csr = open(csr_file).read()

        csr_key = self._sendCertificateRenewal(cert, csr)

      self.logger.info("Waiting for signed certificate...")
      new_cert = self._getSignedCertificate('%s.crt.pem' % csr_key[:-8])

      if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

      self._writeNewFile(new_cert_path, new_cert)
      # change location of files
      if renew_key:
        os.rename(self.key,
                  os.path.join(backup_dir, os.path.basename(self.key)))
        os.rename(new_key_path, self.key)
        self.logger.info("Private correctly renewed at %s." % self.key)

      os.rename(self.certificate,
                os.path.join(backup_dir, os.path.basename(self.certificate)))
      os.rename(new_cert_path, self.certificate)

      self.logger.info("Validating signed certificate...")

      if not self.checkCertificateValidity(new_cert):
        # certificate verification failed, should raise ?
        self.logger.warn("Certificate validation failed.\n" \
          "Please double check the signed certificate before use. Also consider" \
          "revoke it and request a new signed certificate.")
      else:
        self.logger.info("Certificate correctly renewed at %s." % self.certificate)
    except:
      raise
    else:
      for path in [csr_file, RENEW_CSR_KEY_FILE]:
        if os.path.exists(path):
          os.unlink(path)
      if after_script:
        output = popenCommunicate([os.path.realpath(after_script)])
        self.logger.info("Successfully executed script '%s' with output:\n%s" % (
          after_script, output))
    finally:
      for path in [new_cert_path, new_key_path]:
        if os.path.exists(path):
          os.unlink(path)


  def updateCertificateRevocationList(self, crl_file, after_script=''):
    """
      Download or update crl. If the crl_file exists, it will be updated if
      the new CRL has changed.
    """

    crl_url = '%s/crl' % self.ca_url
    self.logger.info("Downloading crl file from %s ..." % crl_url)
    response = self._request('get', crl_url)
    retry = 1

    while not response or response.status_code != 200:
      time.sleep(self.sleep_time)
      response = self._request('get', crl_url)
      retry += 1
      if retry > self.max_retry:
        break

    if not response or response.status_code != 200:
      raise Exception("ERROR: failed to get crl file after %s retry. Exiting..." % retry)

    crl_string = response.text
    # load crl string so we are sure that it is a valid crl string
    crl = crypto.load_crl(crypto.FILETYPE_PEM, crl_string)
    # Dumped string contain only the CRL without extra info
    crl_string = crypto.dump_crl(crypto.FILETYPE_PEM, crl)
    update_crl = False
    if os.path.exists(crl_file):
      with open(crl_file) as fcrl:
        old_checksum = hashlib.md5(fcrl.read()).hexdigest()
        checksum = hashlib.md5(crl_string).hexdigest()
        if checksum != old_checksum:
          update_crl = True
    else:
      update_crl = True

    if update_crl:
      fd = os.open(crl_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0644)
      try:
        os.write(fd, crl_string)
      finally:
        os.close(fd)
      self.logger.info("New CRL file was saved in %s ..." % crl_file)
      if after_script:
        output = popenCommunicate([os.path.realpath(after_script)])
        self.logger.info("Successfully executed script '%s' with output:\n%s" % (
          after_script, output))
    else:
      self.logger.info("crl file don't need to be updated.")
