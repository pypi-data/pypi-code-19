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
import httplib
import json
import traceback
import sys
from . import utils
from . import exceptions

__all__ = ('Application', )

def _getStatus(code):
  return '%i %s' % (code, httplib.responses[code])

class ApplicationError(Exception):
  """
  WSGI HTTP error base class.
  """
  status = _getStatus(httplib.INTERNAL_SERVER_ERROR)
  response_headers = ()

class BadRequest(ApplicationError):
  """
  HTTP bad request error
  """
  status = _getStatus(httplib.BAD_REQUEST)

class NotFound(ApplicationError):
  """
  HTTP not found error
  """
  status = _getStatus(httplib.NOT_FOUND)

class BadMethod(ApplicationError):
  """
  HTTP bad method error
  """
  status = _getStatus(httplib.METHOD_NOT_ALLOWED)

class Conflict(ApplicationError):
  """
  HTTP conflict
  """
  status = _getStatus(httplib.CONFLICT)

class TooLarge(ApplicationError):
  """
  HTTP too large error
  """
  status = _getStatus(httplib.REQUEST_ENTITY_TOO_LARGE)

class InsufficientStorage(ApplicationError):
  """
  No storage slot available (not necessarily out of disk space)
  """
  # httplib lacks the textual description for 507, although it has the constant...
  status = '%i Insufficient Storage' % (httplib.INSUFFICIENT_STORAGE, )

STATUS_OK = _getStatus(httplib.OK)
STATUS_CREATED = _getStatus(httplib.CREATED)
STATUS_NO_CONTENT = _getStatus(httplib.NO_CONTENT)
MAX_BODY_LENGTH = 10 * 1024 * 1024 # 10 MB

class Application(object):
  """
  WSGI application class

  Thread- and process-safe (locks handled by sqlite3).
  """
  def __init__(self, cau, cas):
    """
    cau (caucase.ca.CertificateAuthority)
      CA for users.
      Will be hosted under /cau

    cas (caucase.ca.CertificateAuthority)
      CA for services.
      Will be hosted under /cas
    """
    self._cau = cau
    self._cas = cas

  def __call__(self, environ, start_response):
    """
    WSGI entry point
    """
    try: # Convert ApplicationError subclasses in error responses
      try: # Convert non-wsgi exceptions into WSGI exceptions
        path_item_list = [x for x in environ['PATH_INFO'].split('/') if x]
        try:
          context_id, method_id = path_item_list[:2]
        except ValueError:
          raise NotFound
        if context_id == 'cau':
          context = self._cau
        elif context_id == 'cas':
          context = self._cas
        else:
          raise NotFound
        if method_id.startswith('_'):
          raise NotFound
        try:
          method = getattr(self, method_id)
        except AttributeError:
          raise NotFound
        status, header_list, result = method(context, environ, path_item_list[2:])
      except ApplicationError:
        raise
      except exceptions.NotFound:
        raise NotFound
      except exceptions.Found:
        raise Conflict
      except exceptions.NoStorage:
        raise InsufficientStorage
      except exceptions.CertificateAuthorityException, e:
        raise BadRequest(str(e))
      except Exception:
        print >>sys.stderr, 'Unhandled exception',
        traceback.print_exc(file=sys.stderr)
        raise ApplicationError
    except ApplicationError, e:
      start_response(
        e.status,
        list(e.response_headers),
      )
      result = [str(x) for x in e.args]
    else:
      start_response(
        status,
        header_list,
      )
    return result

  @staticmethod
  def _read(environ):
    """
    Read the entire request body.

    Raises BadRequest if request Content-Length cannot be parsed.
    Raises TooLarge if Content-Length if over MAX_BODY_LENGTH.
    If Content-Length is not set, reads at most MAX_BODY_LENGTH bytes.
    """
    try:
      length = int(environ.get('CONTENT_LENGTH', MAX_BODY_LENGTH))
    except ValueError:
      raise BadRequest('Invalid Content-Length')
    if length > MAX_BODY_LENGTH:
      raise TooLarge('Content-Length limit exceeded')
    return environ['wsgi.input'].read(length)

  def _authenticate(self, environ):
    """
    Verify user authentication.

    Raises NotFound if authentication does not pass checks.
    """
    # Note on NotFound usage here: HTTP specs do not describe how to request
    # client to provide transport-level authentication mechanism (x509 cert)
    # so 401 is not applicable. 403 is not applicable either as spec requests
    # client to not retry the request. 404 is recommended when server does not
    # wish to disclose the reason why it rejected the access, so let's use
    # this.
    try:
      ca_list = self._cau.getCACertificateList()
      utils.load_certificate(
        environ.get('SSL_CLIENT_CERT', b''),
        trusted_cert_list=ca_list,
        crl=utils.load_crl(
          self._cau.getCertificateRevocationList(),
          ca_list,
        ),
      )
    except (exceptions.CertificateVerificationError, ValueError):
      raise NotFound

  def _readJSON(self, environ):
    """
    Read request body and convert to json object.

    Raises BadRequest if request Content-Type is not 'application/json', or if
    json decoding fails.
    """
    if environ.get('CONTENT_TYPE') != 'application/json':
      raise BadRequest('Bad Content-Type')
    data = self._read(environ)
    try:
      return json.loads(data)
    except ValueError:
      raise BadRequest('Invalid json')

  @staticmethod
  def crl(context, environ, subpath):
    """
    Handle /{context}/crl urls.
    """
    if subpath:
      raise NotFound
    if environ['REQUEST_METHOD'] != 'GET':
      raise BadMethod
    data = context.getCertificateRevocationList()
    return (
      STATUS_OK,
      [
        ('Content-Type', 'application/pkix-crl'),
        ('Content-Length', str(len(data))),
      ],
      [data],
    )

  def csr(self, context, environ, subpath):
    """
    Handle /{context}/csr urls.
    """
    http_method = environ['REQUEST_METHOD']
    if http_method == 'GET':
      if subpath:
        try:
          csr_id, = subpath
        except ValueError:
          raise NotFound
        try:
          csr_id = int(csr_id)
        except ValueError:
          raise BadRequest('Invalid integer')
        data = context.getCertificateSigningRequest(csr_id)
        content_type = 'application/pkcs10'
      else:
        self._authenticate(environ)
        data = json.dumps(context.getCertificateRequestList())
        content_type = 'application/json'
      return (
        STATUS_OK,
        [
          ('Content-Type', content_type),
          ('Content-Length', str(len(data))),
        ],
        [data],
      )
    elif http_method == 'PUT':
      if subpath:
        raise NotFound
      csr_id = context.appendCertificateSigningRequest(self._read(environ))
      return (
        STATUS_CREATED,
        [
          ('Location', str(csr_id)),
        ],
        [],
      )
    elif http_method == 'DELETE':
      try:
        csr_id, = subpath
      except ValueError:
        raise NotFound
      self._authenticate(environ)
      try:
        context.deletePendingCertificateSigningRequest(csr_id)
      except exceptions.NotFound:
        raise NotFound
      return (STATUS_NO_CONTENT, [], [])
    else:
      raise BadMethod

  def crt(self, context, environ, subpath):
    """
    Handle /{context}/crt urls.
    """
    http_method = environ['REQUEST_METHOD']
    try:
      crt_id, = subpath
    except ValueError:
      raise NotFound
    if http_method == 'GET':
      if crt_id == 'ca.crt.pem':
        data = context.getCACertificate()
        content_type = 'application/pkix-cert'
      elif crt_id == 'ca.crt.json':
        data = json.dumps(context.getValidCACertificateChain())
        content_type = 'application/json'
      else:
        try:
          crt_id = int(crt_id)
        except ValueError:
          raise BadRequest('Invalid integer')
        data = context.getCertificate(crt_id)
        content_type = 'application/pkix-cert'
      return (
        STATUS_OK,
        [
          ('Content-Type', content_type),
          ('Content-Length', str(len(data))),
        ],
        [data],
      )
    elif http_method == 'PUT':
      if crt_id == 'renew':
        payload = utils.unwrap(
          self._readJSON(environ),
          lambda x: x['crt_pem'],
          context.digest_list,
        )
        data = context.renew(
          crt_pem=payload['crt_pem'].encode('ascii'),
          csr_pem=payload['renew_csr_pem'].encode('ascii'),
        )
        return (
          STATUS_OK,
          [
            ('Content-Type', 'application/pkix-cert'),
            ('Content-Length', str(len(data))),
          ],
          [data],
        )
      elif crt_id == 'revoke':
        data = self._readJSON(environ)
        if data['digest'] is None:
          self._authenticate(environ)
          payload = utils.nullUnwrap(data)
          if 'revoke_crt_pem' not in payload:
            context.revokeSerial(payload['revoke_serial'])
            return (STATUS_NO_CONTENT, [], [])
        else:
          payload = utils.unwrap(
            data,
            lambda x: x['revoke_crt_pem'],
            context.digest_list,
          )
        context.revoke(
          crt_pem=payload['revoke_crt_pem'].encode('ascii'),
        )
        return (STATUS_NO_CONTENT, [], [])
      else:
        try:
          crt_id = int(crt_id)
        except ValueError:
          raise BadRequest('Invalid integer')
        body = self._read(environ)
        if not body:
          template_csr = None
        elif environ.get('CONTENT_TYPE') == 'application/pkcs10':
          template_csr = utils.load_certificate_request(body)
        else:
          raise BadRequest('Bad Content-Type')
        self._authenticate(environ)
        context.createCertificate(
          csr_id=crt_id,
          template_csr=template_csr,
        )
        return (STATUS_NO_CONTENT, [], [])
    else:
      raise BadMethod
