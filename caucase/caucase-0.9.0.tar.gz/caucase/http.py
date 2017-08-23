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
"""
Caucase - Certificate Authority for Users, Certificate Authority for SErvices
"""
from __future__ import absolute_import
import argparse
import datetime
import glob
import os
import signal
import socket
from SocketServer import ThreadingMixIn
import ssl
import sys
import tempfile
from threading import Thread
from urlparse import urlparse
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from . import utils
from .wsgi import Application
from .ca import CertificateAuthority, UserCertificateAuthority
from .storage import SQLite3Storage

_cryptography_backend = default_backend()

BACKUP_SUFFIX = '.sql.caucased'

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
  """
  Threading WSGI server
  """
  daemon_threads = True

  def __init__(self, server_address, *args, **kw):
    self.address_family, _, _, _, _ = socket.getaddrinfo(*server_address)[0]
    assert self.address_family in (socket.AF_INET, socket.AF_INET6), self.address_family
    WSGIServer.__init__(self, server_address, *args, **kw)

class CaucaseWSGIRequestHandler(WSGIRequestHandler):
  """
  Make WSGIRequestHandler logging more apache-like.
  """
  def log_date_time_string(self):
    """
    Apache-style date format.

    Compared to python's default (from BaseHTTPServer):
    - ":" between day and time
    - "+NNNN" timezone is displayed
    - ...but, because of how impractical it is in python to get system current
      timezone (including DST considerations), time it always logged in GMT
    """
    now = datetime.datetime.utcnow()
    return now.strftime('%d/' + self.monthname[now.month] + '/%Y:%H:%M:%S +0000')

class CaucaseSSLWSGIRequestHandler(CaucaseWSGIRequestHandler):
  """
  Add SSL_CLIENT_CERT to environ when client has sent a certificate.
  """
  ssl_client_cert_serial = '-'
  def get_environ(self):
    environ = WSGIRequestHandler.get_environ(self)
    client_cert_der = self.request.getpeercert(binary_form=True)
    if client_cert_der is not None:
      cert = x509.load_der_x509_certificate(
        client_cert_der,
        _cryptography_backend,
      )
      self.ssl_client_cert_serial = str(cert.serial_number)
      environ['SSL_CLIENT_CERT'] = utils.dump_certificate(cert)
    return environ

  # pylint: disable=redefined-builtin
  def log_message(self, format, *args):
    # Note: compared to BaseHTTPHandler, logs the client certificate serial as
    # user name.
    sys.stderr.write(
      "%s - %s [%s] %s\n" % (
        self.client_address[0],
        self.ssl_client_cert_serial,
        self.log_date_time_string(),
        format % args,
      )
    )
  # pylint: enable=redefined-builtin

def startServerThread(server):
  """
  Create and start a "serve_forever" thread, and return it.
  """
  server_thread = Thread(target=server.serve_forever)
  server_thread.daemon = True
  server_thread.start()

def updateSSLContext(
  https,
  key_len,
  threshold,
  server_key_path,
  hostname,
  cau,
  cas,
  wrap=False,
):
  """
  Build a new SSLContext with updated CA certificates, CRL and server key pair,
  apply it to <https>.socket and return the datetime of next update.
  """
  ssl_context = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH,
  )
  # SSL is used for client authentication, and is only required for very few
  # users on any given caucased. So make ssl_context even stricter than python
  # does.
  # No TLSv1 and TLSv1.1, leaving (currently) only TLSv1.2
  ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

  # If a client wishes to use https for unauthenticated operations, that's
  # fine too.
  ssl_context.verify_mode = ssl.CERT_OPTIONAL
  # Note: it does not seem possible to get python's openssl context to check
  # certificate revocation:
  # - calling load_verify_locations(cadata=<crl data>) or
  #   load_verify_locations(cadata=<crl data> + <ca crt data>) raises
  # - calling load_verify_locations(cadata=<ca crt data> + <crl data>) fails to
  #   validate CA completely
  # Anyway, wsgi application level is supposed (and automatically tested to)
  # verify revocations too, so this should not be a big issue... Still,
  # implementation cross-check would have been nice.
  #ssl_context.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
  ssl_context.load_verify_locations(
    cadata=cau.getCACertificate().decode('ascii'),
  )
  cas_certificate_list = cas.getCACertificateList()
  threshold_delta = datetime.timedelta(threshold, 0)
  if os.path.exists(server_key_path):
    old_crt_pem = utils.getCert(server_key_path)
    old_crt = utils.load_certificate(old_crt_pem, cas_certificate_list, None)
    if old_crt.not_valid_after - threshold_delta < datetime.datetime.utcnow():
      new_key = utils.generatePrivateKey(key_len)
      new_key_pem = utils.dump_privatekey(new_key)
      new_crt_pem = cas.renew(
        crt_pem=old_crt_pem,
        csr_pem=utils.dump_certificate_request(
          x509.CertificateSigningRequestBuilder(
          ).subject_name(
            # Note: caucase server ignores this, but cryptography
            # requires CSRs to have a subject.
            old_crt.subject,
          ).sign(
            private_key=new_key,
            algorithm=utils.DEFAULT_DIGEST_CLASS(),
            backend=_cryptography_backend,
          ),
        ),
      )
      with open(server_key_path, 'w') as crt_file:
        crt_file.write(new_key_pem)
        crt_file.write(new_crt_pem)
  else:
    new_key = utils.generatePrivateKey(key_len)
    csr_id = cas.appendCertificateSigningRequest(
      csr_pem=utils.dump_certificate_request(
        x509.CertificateSigningRequestBuilder(
        ).subject_name(
          x509.Name([
            x509.NameAttribute(
              oid=x509.oid.NameOID.COMMON_NAME,
              value=hostname.decode('ascii'),
            ),
          ]),
        ).add_extension(
          x509.KeyUsage(
            # pylint: disable=bad-whitespace
            digital_signature =True,
            content_commitment=False,
            key_encipherment  =True,
            data_encipherment =False,
            key_agreement     =False,
            key_cert_sign     =False,
            crl_sign          =False,
            encipher_only     =False,
            decipher_only     =False,
            # pylint: enable=bad-whitespace
          ),
          critical=True,
        ).sign(
          private_key=new_key,
          algorithm=utils.DEFAULT_DIGEST_CLASS(),
          backend=_cryptography_backend,
        ),
      ),
      override_limits=True,
    )
    cas.createCertificate(csr_id)
    new_crt_pem = cas.getCertificate(csr_id)
    new_key_pem = utils.dump_privatekey(new_key)
    old_mask = os.umask(077)
    try:
      with open(server_key_path, 'w') as crt_file:
        crt_file.write(new_key_pem)
        crt_file.write(new_crt_pem)
    finally:
      os.umask(old_mask)
  ssl_context.load_cert_chain(server_key_path)
  if wrap:
    https.socket = ssl_context.wrap_socket(
      sock=https.socket,
      server_side=True,
    )
  else:
    https.socket.context = ssl_context
  return utils.load_certificate(
    utils.getCert(server_key_path),
    cas_certificate_list,
    None,
  ).not_valid_after - threshold_delta

def main(argv=None):
  """
  Caucase stand-alone http server.
  """
  parser = argparse.ArgumentParser(description='caucased')
  parser.add_argument(
    '--db',
    default='caucase.sqlite',
    help='Path to the SQLite database. default: %(default)s',
  )
  parser.add_argument(
    '--server-key',
    default='server.key.pem',
    metavar='KEY_PATH',
    help='Path to the ssl key pair to use for https socket. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--netloc',
    required=True,
    help='<host>[:<port>] of HTTP socket. '
    'HTTPS socket netloc will be deduced following caucase rules: if port is '
    '80 or not provided, https port will be 443, else it will be port + 1. '
    'If not provided, http port will be picked among available ports and '
    'https port will be the next port. Also, signed certificates will not '
    'contain a CRL distribution point URL. If https port is not available, '
    'this program will exit with an aerror status. '
    'Note on encoding: only ascii is currently supported. Non-ascii may be '
    'provided idna-encoded.',
  )
  parser.add_argument(
    '--threshold',
    default=31,
    type=float,
    help='The remaining certificate validity period, in days, under '
    'which a renew is desired. default: %(default)s',
  )
  parser.add_argument(
    '--key-len',
    default=2048,
    type=int,
    metavar='BITLENGTH',
    help='Number of bits to use when generating a new private key. '
    'default: %(default)s',
  )

  service_group = parser.add_argument_group(
    'CAS options: normal certificates, which are not given any privilege on '
    'caucased',
  )

  user_group = parser.add_argument_group(
    'CAU options: special certificates, which are allowed to sign other '
    'certificates and can decrypt backups',
  )

  service_group.add_argument(
    '--service-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. '
    'default: %(default)s',
  )
  user_group.add_argument(
    '--user-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. '
    'default: %(default)s',
  )

  service_group.add_argument(
    '--service-max-csr',
    default=50,
    type=int,
    help='Maximum number of pending CSR. Further CSR get refused until '
    'an existing ones gets signed or rejected. default: %(default)s',
  )
  user_group.add_argument(
    '--user-max-csr',
    default=50,
    type=int,
    help='Maximum number of pending CSR. Further CSR get refused until '
    'an existing ones gets signed or rejected. default: %(default)s',
  )

  service_group.add_argument(
    '--service-auto-approve-count',
    default=0,
    type=int,
    metavar='COUNT',
    help='Number service certificates which should be automatically signed on '
    'submission, excluding the one needed to serve caucase. '
    'default: %(default)s'
  )
  user_group.add_argument(
    '--user-auto-approve-count',
    default=1,
    type=int,
    metavar='COUNT',
    help='Number of user certificates which should be automatically signed on '
    'submission. default: %(default)s',
  )
  parser.add_argument(
    '--lock-auto-approve-count',
    action='store_true',
    help='The first time this option is given, --service-auto-approve-count '
    'and --user-auto-approve-count values are stored inside caucase database '
    'and will not be altered by further invocations. Once the respective '
    'certificate issuance counters reach these values, no further '
    'certificates will be ever automatically signed.'
  )

  backup_group = parser.add_argument_group(
    'Backup options',
  )
  backup_group.add_argument(
    '--backup-directory',
    help='Backup file path template. Backups will be periodically stored in '
    'given directory, encrypted with all certificates which are valid at the '
    'time of backup generation. Any one of the associated private keys can '
    'decypher it. If not set, no backup will be created.',
  )
  backup_group.add_argument(
    '--backup-period',
    default=1,
    type=float,
    help='Number of days between backups. default: %(default)s'
  )
  backup_group.add_argument(
    '--restore-backup',
    nargs=4,
    metavar=('BACKUP_PATH', 'KEY_PATH', 'CSR_PATH', 'CRT_PATH'),
    help='Restore the file at BACKUP_PATH, decyphering it with the key '
    'at KEY_PATH, revoking corresponding certificate and issuing a new '
    'one in CRT_PATH using the public key in CSR_PATH. '
    'If database is not empty, nothing is done. '
    'Then process will exit and must be restarted wihtout this option.',
  )
  args = parser.parse_args(argv)

  # pylint: disable=unused-argument
  def onTERM(signum, stack):
    """
    Sigterm handler
    """
    # The main objective of this signal hander is to fix coverage scores:
    # without it, it seems hits generated by this process do not get
    # accounted for (atexit not called ?). With it, interpreter shutdown
    # seems nicer.
    raise SystemExit
  # pylint: enable=unused-argument
  signal.signal(signal.SIGTERM, onTERM)

  base_url = u'http://' + args.netloc.decode('ascii')
  parsed_base_url = urlparse(base_url)
  hostname = parsed_base_url.hostname
  http_port = parsed_base_url.port
  cau_crt_life_time = args.user_crt_validity
  cau_db_kw = {
    'table_prefix': 'cau',
    'max_csr_amount': args.user_max_csr,
    # Effectively disables certificate expiration
    'crt_keep_time': cau_crt_life_time,
    'crt_read_keep_time': cau_crt_life_time,
    'enforce_unique_key_id': True,
  }
  cau_kw = {
    'ca_subject_dict': {
      'CN': u'Caucase CAU' + (
        u'' if base_url is None else u' at ' + base_url + '/cau'
      ),
    },
    'ca_key_size': args.key_len,
    'crt_life_time': cau_crt_life_time,
    'auto_sign_csr_amount': args.user_auto_approve_count,
    'lock_auto_sign_csr_amount': args.lock_auto_approve_count,
  }
  if args.restore_backup:
    (
      backup_path,
      backup_key_path,
      backup_csr_path,
      backup_crt_path,
    ) = args.restore_backup
    try:
      _, key_pem, _ = utils.getKeyPair(backup_key_path)
    except ValueError:
      # maybe user extracted their private key ?
      key_pem = utils.getKey(backup_key_path)
    with open(backup_path) as backup_file:
      with open(backup_crt_path, 'a') as new_crt_file:
        new_crt_file.write(
          UserCertificateAuthority.restoreBackup(
            db_class=SQLite3Storage,
            db_path=args.db,
            read=backup_file.read,
            key_pem=key_pem,
            csr_pem=utils.getCertRequest(backup_csr_path),
            db_kw=cau_db_kw,
            kw=cau_kw,
          ),
        )
    return
  cau = UserCertificateAuthority(
    storage=SQLite3Storage(
      db_path=args.db,
      **cau_db_kw
    ),
    **cau_kw
  )
  cas = CertificateAuthority(
    storage=SQLite3Storage(
      db_path=args.db,
      table_prefix='cas',
      max_csr_amount=args.service_max_csr,
    ),
    ca_subject_dict={
      'CN': u'Caucase CAS' + (
        u'' if base_url is None else u' at ' + base_url + '/cas'
      ),
    },
    crl_base_url=None if base_url is None else base_url + u'/cas/crl',
    ca_key_size=args.key_len,
    crt_life_time=args.service_crt_validity,
    auto_sign_csr_amount=args.service_auto_approve_count,
    lock_auto_sign_csr_amount=args.lock_auto_approve_count,
  )
  application = Application(cau=cau, cas=cas)
  http = make_server(
    host=hostname,
    port=http_port,
    app=application,
    server_class=ThreadingWSGIServer,
    handler_class=CaucaseWSGIRequestHandler,
  )
  https = make_server(
    host=hostname,
    port=443 if http_port == 80 else http_port + 1,
    app=application,
    server_class=ThreadingWSGIServer,
    handler_class=CaucaseSSLWSGIRequestHandler,
  )
  next_deadline = next_ssl_update = updateSSLContext(
    https=https,
    key_len=args.key_len,
    threshold=args.threshold,
    server_key_path=args.server_key,
    hostname=hostname,
    cau=cau,
    cas=cas,
    wrap=True,
  )
  if args.backup_directory:
    backup_period = datetime.timedelta(args.backup_period, 0)
    try:
      next_backup = max(
        datetime.datetime.utcfromtimestamp(os.stat(x).st_ctime)
        for x in glob.iglob(
          os.path.join(args.backup_directory, '*' + BACKUP_SUFFIX),
        )
      ) + backup_period
    except ValueError:
      next_backup = datetime.datetime.utcnow()
    next_deadline = min(
      next_deadline,
      next_backup,
    )
  else:
    next_backup = None
  startServerThread(http)
  startServerThread(https)
  try:
    while True:
      now = utils.until(next_deadline)
      if now >= next_ssl_update:
        next_ssl_update = updateSSLContext(
          https=https,
          key_len=args.key_len,
          threshold=args.threshold,
          server_key_path=args.server_key,
          hostname=hostname,
          cau=cau,
          cas=cas,
        )
      if next_backup is None:
        next_deadline = next_ssl_update
      else:
        if now >= next_backup:
          tmp_backup_fd, tmp_backup_path = tempfile.mkstemp(
            prefix='caucase_backup_',
          )
          with os.fdopen(tmp_backup_fd, 'w') as backup_file:
            result = cau.doBackup(backup_file.write)
          if result:
            backup_path = os.path.join(
              args.backup_directory,
              now.strftime('%Y%m%d%H%M%S') + BACKUP_SUFFIX,
            )
            os.rename(tmp_backup_path, backup_path)
            next_backup = now + backup_period
          else:
            os.unlink(tmp_backup_path)
            next_backup = now + datetime.timedelta(0, 3600)
        next_deadline = min(
          next_ssl_update,
          next_backup,
        )
  except utils.SleepInterrupt:
    pass
