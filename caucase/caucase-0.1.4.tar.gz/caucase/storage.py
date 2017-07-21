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

import os
import errno
import uuid
import hashlib
from datetime import datetime, timedelta
from OpenSSL import crypto
from caucase import db
from caucase import utils
from caucase.exceptions import (NoStorage, NotFound, Found, ExpiredCertificate)
from flask_user import UserMixin

STATUS_VALIDATED = 'validated'
STATUS_REVOKED = 'invalidated'
STATUS_REJECTED = 'rejected'
STATUS_PENDING = 'pending'

class Storage(object):

  def __init__(self, db_instance, max_csr_amount=None,
                     crt_keep_time=None, csr_keep_time=None):

    self.db = db_instance

    # initialise tables
    self.db.create_all()

    # store some config in storage
    if max_csr_amount:
      self.__setConfig('max-csr-amount', max_csr_amount)
    if crt_keep_time is not None:
      self.__setConfig('crt-keep-time', crt_keep_time) # 0 mean always keep in storage
    if csr_keep_time is not None:
      self.__setConfig('csr-keep-time', csr_keep_time) # 0 mean always keep non pending csr in storage

  def _getConfig(self, key):
    return Config.query.filter(Config.key == key).first()

  def __setConfig(self, key, value):
    """
      Add new config to storage
    """
    entry = self._getConfig(key)
    if not entry:
      entry = Config(key=key, value='%s' % value)
      self.db.session.add(entry)
    else:
      # update value
      entry.value = value
    self.db.session.commit()

  def getConfig(self, key, default=None):
    """
      Return a config value or default
    """
    entry = self._getConfig(key)
    if not entry:
      return default
    return entry.value

  def _getMaxCsrCount(self):
    return int(self.getConfig('max-csr-amount', 50))

  def getCAKeyPairList(self):
    """
    Return the chronologically sorted (oldest in [0], newest in [-1]) certificate authority
    key pairs.
    """
    item_list = CAKeypair.query.filter(
        CAKeypair.active == True
        ).order_by(
          CAKeypair.creation_date.asc()
        ).all()

    if not item_list:
      return []

    keypair_list = []
    for keypair in item_list:
      keypair_list.append({
        'crt': crypto.load_certificate(crypto.FILETYPE_PEM, keypair.certificate),
        'key': crypto.load_privatekey(crypto.FILETYPE_PEM, keypair.key)
      })

    return keypair_list

  def storeCAKeyPair(self, key_pair):
    """
    Store a certificate authority key pair.
    """
    serial = utils.getSerialToInt(key_pair['crt'])
    crt_string = crypto.dump_certificate(crypto.FILETYPE_PEM, key_pair['crt'])
    key_string = crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair['key'])

    # check that keypair is not stored
    keypair = CAKeypair.query.filter(
        CAKeypair.active == True
        ).filter(
          CAKeypair.serial == serial
        ).first()
    if keypair:
      raise Found('Another CA certificate exists with serial %r' % (serial, ))

    saved_pair = CAKeypair(
        serial=serial,
        common_name=key_pair['crt'].get_subject().CN,
        expire_after=datetime.strptime(
            key_pair['crt'].get_notAfter(), '%Y%m%d%H%M%SZ'
          ),
        start_before=datetime.strptime(
            key_pair['crt'].get_notBefore(), '%Y%m%d%H%M%SZ'
          ),
        key=key_string,
        certificate=crt_string,
        active=True,
        creation_date=datetime.utcnow()
      )

    self.db.session.add(saved_pair)
    self.db.session.commit()

  def storeCertificateSigningRequest(self, csr):
    """
    Store acertificate signing request and generate a unique ID for it.
    """
    csr_amount = self.countPendingCertificateSiningRequest()
    if csr_amount >= self._getMaxCsrCount():
      raise NoStorage('Too many pending CSRs')

    content = crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr)
    checksum = hashlib.md5(content).hexdigest()
    check_csr = CertificateRequest.query.filter(
        CertificateRequest.status == STATUS_PENDING
      ).filter(
        CertificateRequest.checksum == checksum
      ).first()
    if check_csr:
      # this only prevent client loop sending the same csr until csr_amount is reached
      return check_csr.csr_id

    key = str(uuid.uuid1().hex)
    csr_id = '%s.csr.pem' % key
    crt_id = '%s.crt.pem' % key
    req = CertificateRequest(
      content=content,
      creation_date=datetime.utcnow(),
      common_name=csr.get_subject().CN,
      checksum=checksum,
      csr_id=csr_id,
      crt_id=crt_id)

    request_amount = self._getConfig('csr-requested-amount')
    if not request_amount:
      request_amount = Config(key='csr-requested-amount', value='1')
      self.db.session.add(request_amount)
    else:
      request_amount.value = '%s' % (int(request_amount.value) + 1,)

    self.db.session.add(req)
    self.db.session.commit()

    return csr_id

  def deletePendingCertificateRequest(self, csr_id):
    csr = CertificateRequest.query.filter(
        CertificateRequest.status == STATUS_PENDING
      ).filter(
        CertificateRequest.csr_id == csr_id
      ).first()
    if csr:
      self.db.session.delete(csr)
      self.db.session.commit()
    else:
      raise NotFound('No pending CSR with id %r' % (csr_id, ))

  def getPendingCertificateRequest(self, csr_id):
    csr = CertificateRequest.query.filter(
        CertificateRequest.status == STATUS_PENDING
      ).filter(
        CertificateRequest.csr_id == csr_id
      ).first()
    if csr:
      return csr.content
    raise NotFound('No pending CSR with id %r' % (csr_id, ))

  def getPendingCertificateRequestList(self, limit=0, with_data=False):
    """
      Return list of all CSR 
    """
    data_list = []
    index = 1
    query = CertificateRequest.query.filter(
        CertificateRequest.status == STATUS_PENDING
        )
    if limit > 0:
      query.limit(limit)
    csr_list = query.all()
    for request_csr in csr_list:
      csr = {
        'index': index,
        'csr_id': request_csr.csr_id,
        'crt_id': request_csr.crt_id,
        'common_name': request_csr.common_name,
        'creation_date': request_csr.creation_date
      }
      if with_data:
        certificate['content'] = request_csr.content
      data_list.append(csr)
      index += 1

    return data_list

  def storeCertificate(self, csr_id, crt):
    """
    Store certificate as crt_id. crt is a certificate PEM object.
    """
    csr = csr = CertificateRequest.query.filter(
        CertificateRequest.status == STATUS_PENDING
      ).filter(
        CertificateRequest.csr_id == csr_id
      ).first()
    if not csr:
      raise NotFound('No pending CSR with id %r' % (csr_id, ))

    cert = Certificate.query.filter(
        Certificate.status == STATUS_VALIDATED
      ).filter(
        Certificate.crt_id == csr.crt_id
      ).first()

    if cert:
      raise Found('CRT already exists')

    cert_db = Certificate(
        crt_id=csr.crt_id,
        serial=utils.getSerialToInt(crt),
        common_name=crt.get_subject().CN,
        expire_after=datetime.strptime(crt.get_notAfter(), '%Y%m%d%H%M%SZ'),
        start_before=datetime.strptime(crt.get_notBefore(), '%Y%m%d%H%M%SZ'),
        creation_date=datetime.utcnow(),
        content=crypto.dump_certificate(crypto.FILETYPE_PEM, crt)
    )
    # Change Csr status as 'validated', so it can be trashed
    csr.status = STATUS_VALIDATED

    self.db.session.add(cert_db)
    self.db.session.commit()

    return csr.crt_id

  def getCertificateFromSerial(self, serial):
    cert = Certificate.query.filter(
        Certificate.status == STATUS_VALIDATED
      ).filter(
        Certificate.serial == '%s' % serial
      ).first()

    if cert:
      return cert

    raise NotFound('No certficate with serial %r' % (serial, ))
    # schedule certificate removal

  def getCertificate(self, crt_id):
    cert = Certificate.query.filter(
        Certificate.status == STATUS_VALIDATED
      ).filter(
        Certificate.crt_id == crt_id
      ).first()

    if cert and cert.content:
      # if content is emtpy, maybe the certificate content was stripped ?
      return cert.content

    raise NotFound('No certficate with id %r' % (crt_id, ))
    # schedule certificate removal

  def getSignedCertificateList(self, limit=0, with_data=False):
    data_list = []
    index = 1
    query = Certificate.query.filter(
        Certificate.status == STATUS_VALIDATED
        )
    if limit > 0:
      query.limit(limit)
    signed_cert_list = query.all()
    for signed_cert in signed_cert_list:
      certificate = {
        'index': index,
        'serial': signed_cert.serial,
        'crt_id': signed_cert.crt_id,
        'common_name': signed_cert.common_name,
        'expire_after': signed_cert.expire_after,
        'start_before': signed_cert.start_before,
      }
      if with_data:
        certificate['content'] = signed_cert.content
      data_list.append(certificate)
      index += 1

    return data_list

  def revokeCertificate(self, serial=None, crt_id=None, reason=''):
    """
    Add serial to the list of revoked certificates.
    Associated certificate must expire at (or before) not_after_date, so
    revocation can be pruned.
    
    serial or crt_id should be send to get the certificate. If both are set,
    serial is used.
    """
    if serial is None and crt_id is None:
      raise ValueError("serial or crt_id are not set to revokeCertificate.")

    query = Certificate.query.filter(Certificate.status == STATUS_VALIDATED)
    if serial:
      query = query.filter(Certificate.serial == serial)
    else:
      query = query.filter(Certificate.crt_id == crt_id)

    cert = query.first()

    if not cert:
      raise NotFound('No certficate with serial or id %r found!' % (
                    serial or crt_id, ))

    expire_in = cert.expire_after  - datetime.utcnow()
    if expire_in.days < 0:
      raise ExpiredCertificate("Certificate with serial %r has expired" \
              " since %r day(s)." % (serial, -1*expire_in.days))

    revoke = Revocation(
        serial=cert.serial,
        creation_date=datetime.utcnow(),
        reason=reason,
        crt_expire_after=cert.expire_after
      )
    # Set latest CRL as expired, it will be regenerated
    crl = CertificateRevocationList.query.filter(
        CertificateRevocationList.active == True
      ).first()
    if crl:
      crl.active = False
    # this certificate is not valid anymore
    cert.status = STATUS_REVOKED
    self.db.session.add(revoke)
    self.db.session.commit()

  def getCertificateRevocationList(self):
    """
      Get Certificate Rovocation List of None if there is no valid CRL
    """
    last_revocation = CertificateRevocationList.query.order_by(
          CertificateRevocationList.id.desc()
        ).first()

    if last_revocation and last_revocation.active:
      if (last_revocation.crl_expire_after - datetime.utcnow()).days >= 0:
        return last_revocation.content
    return None

  def getNextCRLVersionNumber(self):
    last_revocation = CertificateRevocationList.query.order_by(
          CertificateRevocationList.id.desc()
        ).first()
    if last_revocation:
      return last_revocation.id + 1
    else:
      return 1

  def storeCertificateRevocationList(self, crl, expiration_date):
    """
      Store Certificate Revocation List, return stored crl string
      
      XXX - send expiration_date because crypto.crl has no method to read this from crl object
    """
    # Fetch cached CRL (or re-generate and store if not cached).
    dumped_crl = crypto.dump_crl(crypto.FILETYPE_PEM, crl)

    revocation_list = CertificateRevocationList(
        creation_date=datetime.utcnow(),
        crl_expire_after=expiration_date,
        content=dumped_crl,
        active=True
      )
    self.db.session.add(revocation_list)
    self.db.session.commit()
    return dumped_crl

  def getRevocationList(self):
    """
      Get the list of all revoked certificate which are not expired
    """
    return Revocation.query.filter(
          Revocation.crt_expire_after >= datetime.utcnow()
        ).all()

  def getCertificateSigningRequestAmount(self):
    """
      Return number of CSR which was requested until now
    """
    return int(self.getConfig('csr-requested-amount', 0))

  def countValidatedCertificate(self):
    return Certificate.query.filter(
        Certificate.status == STATUS_VALIDATED
        ).count()

  def countPendingCertificateSiningRequest(self):
    return CertificateRequest.query.filter(
        CertificateRequest.status == STATUS_PENDING
        ).count()

  def countRevokedCertificate(self):
    return Certificate.query.filter(
        Certificate.status == STATUS_REVOKED
        ).count()

  def countCertificateRevocation(self):
    return Revocation.query.count()


  def housekeep(self):
    """
    Remove outdated certificates (because they were retrieved long ago),
    ca certificates (because they exceeded their "not valid after" date),
    revocation of anway-expired certificates.
    """
    crt_keep_time = int(self.getConfig('crt-keep-time', 0))
    csr_keep_time = int(self.getConfig('csr-keep-time', 0))

    expired_keypair_list = CAKeypair.query.filter(
          CAKeypair.expire_after < datetime.utcnow()
        ).all()
    for key_pair in expired_keypair_list:
      # Desactivate this ca certificate
      key_pair.active = False

    # wipe certificate content
    if crt_keep_time > 0:
      check_date = datetime.utcnow() - timedelta(0, crt_keep_time)
      cert_list = Certificate.query.filter(
          Certificate.creation_date <= check_date
          )
      for cert in cert_list:
        # clear x509 certificate information
        cert.content = ""

    # delete certificate request
    if csr_keep_time > 0:
      check_date = datetime.utcnow() - timedelta(0, csr_keep_time)
      csr_list = CertificateRequest.query.filter(
            CertificateRequest.status != STATUS_PENDING
          ).filter(
            CertificateRequest.creation_date <= check_date
          )
      for csr in csr_list:
        self.db.session.delete(csr)

    # delete all expired Certificate Rovocation
    revocation_list = Revocation.query.filter(
          Revocation.crt_expire_after < datetime.utcnow()
        ).all()
    for revocation in revocation_list:
      self.db.session.delete(revocation)

    # Delete all expired Certificate Rovocation List (CRL)
    crl_list = CertificateRevocationList.query.filter(
          CertificateRevocationList.crl_expire_after < datetime.utcnow()
        ).all()
    for crl in crl_list:
      self.db.session.delete(crl)

    self.db.session.commit()


  def findOrCreateUser(self, first_name, last_name, email, username, hash_password):
    """ Find existing user or create new user """

    user = User.query.filter(User.username == username).first()
    if not user:
      user = User(email=email,
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=hash_password,
        active=True,
        confirmed_at=datetime.utcnow()
      )
      db.session.add(user)
      db.session.commit()
    return user

  def findUser(self, username):
    return User.query.filter(User.username == username).first()


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)

  # User authentication information
  username = db.Column(db.String(50), nullable=False, unique=True)
  password = db.Column(db.String(255), nullable=False, server_default='')

  # User email information
  email = db.Column(db.String(255), nullable=False, unique=True)
  confirmed_at = db.Column(db.DateTime())

  # User information
  active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
  first_name = db.Column(db.String(100), nullable=False, server_default='')
  last_name = db.Column(db.String(100), nullable=False, server_default='')

class Config(db.Model):
  """
    This table store some configs and information
  """
  __tablename__ = 'config'
  key = db.Column(db.String(50), primary_key=True)
  value = db.Column(db.Text)

class CAKeypair(db.Model):
  """
    This table is used ca certificate key pair
  """
  __tablename__ = 'ca_keypair'
  id = db.Column(db.Integer, primary_key=True)
  serial = db.Column(db.String(50), unique=True)
  expire_after = db.Column(db.DateTime)
  start_before = db.Column(db.DateTime)
  common_name = db.Column(db.String(50), unique=False)
  active = db.Column(db.Boolean(), nullable=False, server_default='1')
  certificate = db.Column(db.Text)
  key = db.Column(db.Text)
  creation_date = db.Column(db.DateTime)

class CertificateRequest(db.Model):
  """
    This table is used to store certificate signature request
  """
  __tablename__ = 'csr'
  id = db.Column(db.Integer, primary_key=True)
  csr_id=db.Column(db.String(80), unique=True)
  crt_id = db.Column(db.String(80), unique=True)
  common_name = db.Column(db.String(50), unique=False)
  content = db.Column(db.Text)
  creation_date = db.Column(db.DateTime)
  status = db.Column(db.String(20), unique=False, server_default=STATUS_PENDING)
  # checksum prevent to store twice the same csr
  checksum = db.Column(db.String(50))

class Certificate(db.Model):
  """
    This table is used to store some informations about certificate
  """
  __tablename__ = 'certificate'
  id = db.Column(db.Integer, primary_key=True)
  crt_id = db.Column(db.String(80), unique=True)
  serial = db.Column(db.String(50), unique=True)
  common_name = db.Column(db.String(50), unique=False)
  expire_after = db.Column(db.DateTime)
  start_before = db.Column(db.DateTime)
  creation_date = db.Column(db.DateTime)
  # status = validated or revoked
  status = db.Column(db.String(20), unique=False, server_default=STATUS_VALIDATED)
  content = db.Column(db.Text)

class Revocation(db.Model):
  """
    This table store certificate revocation request from users
  """
  __tablename__ = 'revoked'
  id = db.Column(db.Integer, primary_key=True)
  serial = db.Column(db.String(50), unique=False)
  crt_expire_after = db.Column(db.DateTime)
  reason = db.Column(db.String(200), unique=False)
  creation_date = db.Column(db.DateTime)

class CertificateRevocationList(db.Model):
  """
    This table store certificate revocation list content
  """
  __tablename__ = 'crl'
  id = db.Column(db.Integer, primary_key=True)
  active = db.Column(db.Boolean(), nullable=False, server_default='1')
  creation_date = db.Column(db.DateTime)
  crl_expire_after = db.Column(db.DateTime)
  content = db.Column(db.Text)
