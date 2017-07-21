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


import logging
import os, errno
import argparse
import traceback
import json
import flask
from flask import (session, request, redirect, url_for, render_template,
                    jsonify, abort, send_file, flash, g, Response)
from flask_user import UserManager, SQLAlchemyAdapter
from wtforms import StringField, SubmitField, validators
from flask_wtf import FlaskForm
from flask_mail import Mail
from flask_user import login_required, current_user
from flask_login import logout_user  #, login_user, current_user, login_required
from caucase.ca import CertificateAuthority, DEFAULT_DIGEST_LIST, MIN_CA_RENEW_PERIOD
from caucase.exceptions import (NoStorage, NotFound, Found, BadSignature,
                                BadCertificateSigningRequest,
                                BadCertificate,
                                CertificateVerificationError,
                                ExpiredCertificate)
from functools import wraps
from caucase import utils, app, db

class DisabledStringField(StringField):
  def __call__(self, *args, **kwargs):
    kwargs.setdefault('disabled', True)
    return super(ReadonlyStringField, self).__call__(*args, **kwargs)

# Define the User profile form
class UserProfileForm(FlaskForm):
  username = StringField('Username')
  first_name = StringField('First name', validators=[
      validators.DataRequired('First name is required')])
  last_name = StringField('Last name', validators=[
      validators.DataRequired('Last name is required')])
  email = StringField('Email', validators=[
      validators.DataRequired('Email is required')])
  submit = SubmitField('Save')

def parseArguments(argument_list=[]):
  """
  Parse arguments for Certificate Authority instance.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--ca-dir',
                      help='Certificate authority base directory')
  parser.add_argument('-H', '--host',
                      default='127.0.0.1',
                      help='Host or IP of ca server. Default: %(default)s')
  parser.add_argument('-P', '--port',
                      default='9086', type=int,
                      help='Port for ca server. Default: %(default)s')
  parser.add_argument('-d', '--debug',
                      action="store_true", dest="debug", default=False,
                      help='Enable debug mode.')
  parser.add_argument('-l', '--log-file',
                      help='Path for log output')
  parser.add_argument('--crt-life-time',
                      default=365*24*60*60, type=int,
                      help='The time in seconds before a generated certificate will expire. Default: 365*24*60*60 seconds (1 year)')
  parser.add_argument('-s', '--subject',
                      default='',
                      help='Formatted subject string to put into generated CA Certificate file. Ex: /C=XX/ST=State/L=City/OU=OUnit/O=Company/CN=CAAuth/emailAddress=xx@example.com')
  parser.add_argument('--ca-life-period',
                      default=10, type=float,
                      help='Number of individual certificate validity periods during which the CA certificate is valid. Default: %(default)s')
  parser.add_argument('--ca-renew-period',
                      default=MIN_CA_RENEW_PERIOD, type=float,
                      help='Number of individual certificate validity periods during which both the existing and the new CA Certificates are valid. Default: %(default)s')
  parser.add_argument('--crl-life-period',
                      default=1/50., type=float,
                      help='Number of individual certificate validity periods during which the CRL is valid. Default: %(default)s')
  parser.add_argument('-D', '--digest',
                      action='append', dest='digest_list', default=DEFAULT_DIGEST_LIST,
                      help='Allowed digest for all signature. Default: %(default)s')
  parser.add_argument('--max-request-amount',
                      default=50,
                      help='Maximun pending certificate signature request amount. Default: %(default)s')
  parser.add_argument('--crt-keep-time',
                      default=30*24*60*60, type=int,
                      help='The time in seconds before a generated certificate will be deleted on CA server. Set 0 to never delete. Default: 30*24*60*60 seconds (30 days)')
  parser.add_argument('--external-url',
                      help="The HTTP URL at which this tool's \"/\" path is reachable by all certificates users in order to retrieve latest CRL.")
  parser.add_argument('--auto-sign-csr-amount', 
                      default=1, type=int,
                      help='Say how many csr must be signed automatically. Has no effect if there is more than the specified value of csr submitted.')

  if argument_list:
    return parser.parse_args(argument_list)
  return parser.parse_args()


def getLogger(debug=False, log_file=None):
  logger = logging.getLogger("CertificateAuthority")
  logger.setLevel(logging.INFO)

  if not log_file:
    logger.addHandler(logging.StreamHandler())
  else:
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.info('Configured logging to file %r' % log_file)

  if debug:
    logger.setLevel(logging.DEBUG)
  return logger

def getConfig(self, key):
  if key in self.keys():
    temp_dict = dict()
    temp_dict.update(self)
    return temp_dict[key]
  else:
    raise KeyError

def start():
  """
    Start Web Flask application server
  """
  options = parseArguments()
  configure_flask(options)
  app.logger.info("Certificate Authority server started on http://%s:%s" % (
      options.host, options.port))
  app.run(
        host=options.host,
        port=int(options.port)
    )

def configure_flask(options):
  """
    Configure certificate authority service
  """

  if not options.ca_dir:
    options.ca_dir = os.getcwd()
  else:
    options.ca_dir = os.path.abspath(options.ca_dir)
  if not options.external_url:
    options.external_url = 'http://[%s]:%s' % (options.host, options.port)
  db_file = "sqlite:///%s"% os.path.join(options.ca_dir, 'ca.db')

  # work in ca directory
  os.chdir(options.ca_dir)

  # init Flask app
  app.config.update(
    DEBUG=options.debug,
    CSRF_ENABLED=True,
    USER_AFTER_LOGIN_ENDPOINT='manage_csr',
    USER_AFTER_LOGOUT_ENDPOINT='index',
    USER_ENABLE_USERNAME=True,
    USER_ENABLE_EMAIL=False,
    USER_ENABLE_REGISTRATION=False,
    USER_ENABLE_CHANGE_USERNAME=False,
    SECRET_KEY = 'This is an UNSECURE Secret. Please CHANGE THIS for production environments.',
    SQLALCHEMY_DATABASE_URI=db_file
  )

  flask.config.Config.__getattr__ = getConfig

  mail = Mail(app)

  # Setup Flask-User
  # XXX - User table Will go away when switching to CA for Users
  if not app.config['TESTING']:
    from caucase.storage import User
    db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
    user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

  logger = getLogger(options.debug, options.log_file)
  app.logger.addHandler(logger)

  # Instanciate storage
  from caucase.storage import Storage
  storage = Storage(db,
                    max_csr_amount=options.max_request_amount,
                    crt_keep_time=options.crt_keep_time,
                    csr_keep_time=options.crt_keep_time)

  ca = CertificateAuthority(
      storage=storage,
      ca_life_period=options.ca_life_period,
      ca_renew_period=options.ca_renew_period,
      crt_life_time=options.crt_life_time,
      crl_renew_period=options.crl_life_period,
      digest_list=options.digest_list,
      crl_base_url='%s/crl' % options.external_url,
      ca_subject=options.subject,
      auto_sign_csr_amount=options.auto_sign_csr_amount
    )

  # XXX - Storage argument Will go away when switching to CA for Users
  app.config.update(
    storage=storage,
    ca=ca,
    log_file=options.log_file,
  )


def check_authentication(username, password):
  user = app.config.storage.findUser(username)
  if user:
    return app.user_manager.verify_password(password, user)
  else:
    return False

def authenticated_method(func):
  """ This decorator ensures that the current user is logged in before calling the actual view.
      Abort with 401 when the user is not logged in."""
  @wraps(func)
  def decorated_view(*args, **kwargs):
      # User must be authenticated
      auth = request.authorization
      if not auth:
        return abort(401)
      elif not check_authentication(auth.username, auth.password):
        return abort(401)
      # Call the actual view
      return func(*args, **kwargs)
  return decorated_view


class FlaskException(Exception):
  status_code = 400
  code = 400

  def __init__(self, message, status_code=None, payload=None):
    Exception.__init__(self)
    self.message = message
    if status_code is not None:
      self.status_code = status_code
    self.payload = payload

  def to_dict(self):
    rv = dict(self.payload or ())
    # rv['code'] = self.code
    rv['message'] = self.message
    return rv

@app.errorhandler(FlaskException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(401)
def error401(error):
  if error.description is None:
    message = {
      'code': 401,
      'name': 'Unauthorized',
      'message': "Authenticate."
    }
  else:
    message = error.description
  response = jsonify(message)

  response.status_code = 401
  response.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'

  return response

@app.errorhandler(403)
def error403(error):
  if error.description is None:
    message = {
      'code': 404,
      'name': 'Forbidden',
      'message': 'Forbidden. Your are not allowed to access %s' % request.url,
    }
  else:
    message = error.description
  response = jsonify(message)
  response.status_code = 404

  return response

@app.errorhandler(404)
def error404(error):
  if error.description is None:
    message = {
      'code': 404,
      'name': 'NotFound',
      'message': 'Resource not found: ' + request.url,
    }
  else:
    message = error.description
  response = jsonify(message)
  response.status_code = 404

  return response

@app.errorhandler(400)
def error400(error):
  if error.description is None:
    message = {
      'code': 400,
      'name': 'BadRequest',
      'message': 'The request could not be understood by the server, you probably provided wrong parameters.'
    }
  else:
    message = error.description
  response = jsonify(message)
  response.status_code = 400

  return response

def send_file_content(content, filename, mimetype='text/plain'):
  return Response(content,
             mimetype=mimetype,
             headers={"Content-Disposition":
                          "attachment;filename=%s" % filename})


@app.before_request
def before_request():
  # XXX - This function Will be modified or removed when switching to CA for Users
  is_admin_path = request.path.startswith('/admin') or request.path.startswith('/user')
  if  not is_admin_path and not request.path.startswith('/certificates'):
    return
  if is_admin_path:
    csr_count = app.config.storage.countPendingCertificateSiningRequest()
    if csr_count < 10:
      csr_count = '0%s' % csr_count
    session['count_csr'] = csr_count
  if request.path == '/admin/configure' or request.path == '/admin/setpassword':
    # check if password file exists, if yes go to index
    if app.config.storage.findUser('admin'):
      return redirect(url_for('admin'))
    return
  # XXX - using hard username
  if not app.config.storage.findUser('admin'):
    return redirect(url_for('configure'))
  g.user = current_user



# Routes for certificate Authority

@app.route('/crl', methods=['GET'])
def get_crl():
  """
    Get the lastest CRL (certificate revocation list)
  """

  crl_content = app.config.ca.getCertificateRevocationList()
  return send_file_content(crl_content, 'ca.crl.pem')

@app.route('/csr/<string:csr_id>', methods=['GET'])
def get_csr(csr_id):
  """
    Get a CSR string in PEM format from identified by `csr_id`.
  """

  try:
    csr_content = app.config.ca.getPendingCertificateRequest(csr_id)
  except NotFound, e:
    raise FlaskException(str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})

  return send_file_content(csr_content, csr_id)

@app.route('/csr', methods=['PUT'])
def request_cert():
  """
    Store certificate signature request (csr) in PEM format
  """
  csr_content = request.form.get('csr', '').encode('utf-8')
  if not csr_content:
    raise FlaskException("'csr' parameter is mandatory",
              payload={"name": "MissingParameter", "code": 2})

  try:
    csr_id = app.config.ca.createCertificateSigningRequest(csr_content)
  except BadCertificateSigningRequest, e:
    raise FlaskException(str(e),
              payload={"name": "FileFormat", "code": 3})
  except NoStorage, e:
    raise FlaskException(str(e),
              payload={"name": "NoStorage", "code": 4})

  response = Response("", status=201)
  response.headers['Location'] = url_for('get_csr', _external=True, csr_id=csr_id)

  return response

@app.route('/csr/<string:csr_id>', methods=['DELETE'])
@authenticated_method
def remove_csr(csr_id):
  """
    Delete a Certificate signature request. Authentication required
  """

  try:
    app.config.ca.deletePendingCertificateRequest(csr_id)
  except NotFound, e:
    raise FlaskException("%s" % str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})

  response = Response("", status=200)

  return response

@app.route('/crt/<string:cert_id>', methods=['GET'])
def get_crt(cert_id):
  """
    Get a certificate by the id `cert_id`
  """

  try:
    cert_content = app.config.ca.getCertificate(cert_id)
  except NotFound, e:
    raise FlaskException("%s" % str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})

  return send_file_content(cert_content, cert_id)

@app.route('/crt/serial/<string:serial>', methods=['GET'])
def crt_fromserial(serial):
  """
    Get a certificate by the serial
  """
  try:
    cert_content = app.config.ca.getCertificateFromSerial(serial)
  except NotFound, e:
    raise FlaskException("%s" % str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})

  return send_file_content(cert_content, '%s.crt.pem' % serial)

@app.route('/crt/ca.crt.pem', methods=['GET'])
def get_cacert():
  """
    Get CA Certificate in PEM format string.
  """

  ca_cert = app.config.ca.getCACertificate()

  return send_file_content(ca_cert, 'ca.crt.pem')

@app.route('/crt/ca.crt.json', methods=['GET'])
def get_cacert_json():
  """
    Return CA certificate chain list, if the CA certificate is being renewed
    the list will contain the next certificate and the old certificate which
    will expire soon.
  """
  ca_chain_list = app.config.ca.getValidCACertificateChain()

  return jsonify(ca_chain_list)

def signcert(csr_key, subject_dict=None, redirect_to=''):

  try:
    cert_id = app.config.ca.createCertificate(csr_key, subject_dict=subject_dict)
  except NotFound, e:
    raise FlaskException("%s" % str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})
  except Found, e:
    # Certificate is found
    raise FlaskException("%s" % str(e),
                payload={"name": "FileFound", "code": 5})

  # XXX - to remove (flask UI)
  flash('Certificate is signed!', 'success')
  if redirect_to:
    return redirect(url_for(redirect_to))

  response = Response("", status=201)
  response.headers['Location'] = url_for('get_crt', _external=True, cert_id=cert_id)

  return response

@app.route('/crt', methods=['PUT'])
@authenticated_method
def sign_cert():
  """
    Sign a certificate, require authentication
  """
  key = request.form.get('csr_id', '').encode('utf-8')
  if not key:
    raise FlaskException("'csr_id' parameter is a mandatory parameter",
              payload={"name": "MissingParameter", "code": 2})

  try:
    subject = request.form.get('subject', '').encode('utf-8')
    subject_dict = None
    if subject:
      subject_dict = json.loads(subject)
    return signcert(key, subject_dict=subject_dict)
  except ValueError, e:
    traceback.print_exc()
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except AttributeError, e:
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})

@app.route('/crt/renew', methods=['PUT'])
def renew_cert():
  """
  this method is used to renew expired certificate.
  """
  payload = request.form.get('payload', '')

  if not payload:
    # Bad parameters
    raise FlaskException("'payload' parameter is mandatory",
              payload={"name": "MissingParameter", "code": 2})

  try:
    wrapped = json.loads(payload)
  except ValueError, e:
    raise FlaskException("payload parameter is not a valid Json string: %s" % str(e),
                payload={"name": "FileFormat", "code": 3})

  try:
    cert_id = app.config.ca.renew(wrapped)
  except ValueError, e:
    traceback.print_exc()
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except KeyError, e:
    traceback.print_exc()
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except BadSignature, e:
    raise FlaskException(str(e),
                payload={"name": "SignatureMismatch", "code": 6})
  except BadCertificateSigningRequest, e:
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except BadCertificate, e:
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except CertificateVerificationError, e:
    raise FlaskException(str(e),
                payload={"name": "SignatureMismatch", "code": 6})
  except NoStorage, e:
    raise FlaskException(str(e),
              payload={"name": "NoStorage", "code": 4})
  except NotFound, e:
    raise FlaskException(str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})
  except Found, e:
    # Certificate is found
    raise FlaskException(str(e),
                payload={"name": "FileFound", "code": 5})

  response = Response("", status=201)
  response.headers['Location'] = url_for('get_crt', _external=True, cert_id=cert_id)

  return response


@app.route('/crt/revoke', methods=['PUT'])
def request_revoke_crt():
  """
    Revoke method existing and valid certificate
  """
  payload = request.form.get('payload', '')
  if not payload:
    # Bad parameters
    raise FlaskException("'payload' parameter is mandatory",
              payload={"name": "MissingParameter", "code": 2})

  try:
    wrapped = json.loads(payload)
  except ValueError, e:
    raise FlaskException("payload parameter is not a valid Json string: %s" % str(e),
                payload={"name": "FileFormat", "code": 3})

  try:
    app.config.ca.revokeCertificate(wrapped)
  except ValueError, e:
    traceback.print_exc()
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except KeyError, e:
    traceback.print_exc()
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except BadSignature, e:
    raise FlaskException(str(e),
                payload={"name": "SignatureMismatch", "code": 6})
  except CertificateVerificationError, e:
    raise FlaskException(str(e),
                payload={"name": "SignatureMismatch", "code": 6})
  except BadCertificate, e:
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except ExpiredCertificate, e:
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except NotFound, e:
    raise FlaskException(str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})

  response = Response("", status=201, )
  return response

@app.route('/crt/revoke/id', methods=['PUT'])
@authenticated_method
def revoke_crt():
  """
    Directly revoke a certificate from his serial
  """

  try:
    crt_id = request.form.get('crt_id', '')
    if not crt_id:
      raise FlaskException("'crt_id' parameter is mandatory",
              payload={"name": "MissingParameter", "code": 2})

    app.config.ca.revokeCertificateFromID(crt_id)
  except ValueError, e:
    traceback.print_exc()
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except ExpiredCertificate, e:
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})
  except NotFound, e:
    raise FlaskException(str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})

  response = Response("", status=201)

  return response


#Manage routes (Authentication required) - Flask APP
# XXX - this routes will be updated or removed after implement ca_user

@app.route('/')
def home():
  return redirect(url_for('index'))

@app.route('/certificates')
def index():
  # page to list certificates, also connection link
  data_list = app.config.ca.getSignedCertificateList()
  return render_template("index.html", data_list=data_list)

@app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/')
@login_required
def admin():
  return index()

@app.route('/admin/csr_requests', methods=['GET'])
@login_required
def manage_csr():
  data_list = app.config.ca.getPendingCertificateRequestList()
  return render_template('manage_page.html', data_list=data_list)

@app.route('/admin/configure', methods=['GET'])
def configure():
  return render_template("configure.html")

@app.route('/admin/setpassword', methods=['POST'])
def setpassword():
  username = 'admin'
  password = request.form.get('password', '').encode('utf-8')
  if not password:
    raise FlaskException("'password' parameter is mandatory",
              payload={"name": "MissingParameter", "code": 2})

  app.config.storage.findOrCreateUser(
    "Admin",
    "admin",
    "admin@example.com",
    username,
    app.user_manager.hash_password(password))
  logout_user()
  return redirect(url_for('manage_csr'))

@app.route('/admin/signcert', methods=['GET'])
@login_required
def do_signcert_web():
  csr_id = request.args.get('csr_id', '').encode('utf-8')
  if not csr_id:
    raise FlaskException("'csr_id' parameter is a mandatory parameter",
              payload={"name": "MissingParameter", "code": 2})
  try:
    return signcert(csr_id, subject_dict=None, redirect_to='manage_csr')
  except ValueError, e:
    raise FlaskException(str(e),
                payload={"name": "FileFormat", "code": 3})

@app.route('/admin/deletecsr', methods=['GET'])
@login_required
def deletecsr():
  """
    Delete certificate signature request file
  """
  csr_id = request.args.get('csr_id', '').encode('utf-8')
  if not csr_id:
    raise FlaskException("'csr_id' parameter is a mandatory parameter",
              payload={"name": "MissingParameter", "code": 2})

  try:
    app.config.ca.deletePendingCertificateRequest(csr_id)
  except NotFound, e:
    raise FlaskException("%s" % str(e),
                status_code=404, payload={"name": "FileNotFound", "code": 1})

  return redirect(url_for('manage_csr'))

@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    form = UserProfileForm(request.form, obj=current_user)
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        del form.username  # revove username from recieved form
        form.populate_obj(current_user)
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('index'))

    return render_template('user_profile.html',
                           form=form)

