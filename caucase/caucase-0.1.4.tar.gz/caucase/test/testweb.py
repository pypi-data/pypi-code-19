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
import urllib2
import shutil
import tempfile
import json
from datetime import datetime
from caucase.web import parseArguments, configure_flask
from OpenSSL import crypto, SSL
from caucase.exceptions import (NoStorage, NotFound, Found)
from caucase import utils
from flask_testing import TestCase
from flask import url_for

class CertificateAuthorityWebTest(TestCase):

  def setUp(self):
    self.ca_dir = tempfile.mkdtemp()
    configure_flask(parseArguments(['--ca-dir', self.ca_dir, '-s', '/CN=CA Auth Test/emailAddress=xx@example.com']))

  def tearDown(self):
    self.db.session.remove()
    self.db.drop_all()
    if os.path.exists(self.ca_dir):
      shutil.rmtree(self.ca_dir)

  def create_app(self):
    from caucase import db, app
    app.config['TESTING'] = True
    app.config['LIVESERVER_PORT'] = 0
    self.db = db
    return app

  def generateCSR(self, cn="toto.example.com"):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    req = crypto.X509Req()
    subject = req.get_subject()
    subject.CN = cn
    subject.C = "CC"
    subject.ST = "ST"
    subject.L = "LO"
    subject.O = "ORG"
    subject.OU = "OU"
    subject.emailAddress = "toto@example.com"
    req.set_pubkey(key)
    utils.X509Extension().setDefaultCsrExtensions(req)
    req.sign(key, 'sha256')

    return (req, key)

  def _init_password(self, password):
    response = self.client.post('/admin/setpassword', data=dict(password=password),
                                follow_redirects=True)
    self.assert200(response)

  def test_get_crl(self):
    response = self.client.get('/crl')
    self.assert200(response)
    crypto.load_crl(crypto.FILETYPE_PEM, response.data)

  def test_put_csr(self):
    csr, _ = self.generateCSR()
    csr_string = crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr)
    data = dict(csr=csr_string)
    response = self.client.put(url_for('request_cert'), data=data)
    self.assertEquals(response.status_code, 201)
    csr_key = response.headers['Location'].split('/')[-1]

    # the first csr is signed and csr is no longer available

    response2 = self.client.get('/csr/%s' % csr_key)
    self.assert404(response2)
    cert_url = '/crt/%s.crt.pem' %  csr_key[:-8]
    response3 = self.client.get(cert_url)
    self.assert200(response3)
    crypto.load_certificate(crypto.FILETYPE_PEM, response3.data)

    # put another csr
    csr2, _ = self.generateCSR()
    csr2_string = crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr)
    response4 = self.client.put(url_for('request_cert'), data=dict(csr=csr2_string))
    self.assertEquals(response4.status_code, 201)
    csr_key = response4.headers['Location'].split('/')[-1]
    # get csr will return the csr
    response5 = self.client.get('/csr/%s' % csr_key)
    self.assert200(response5)
    # the certificate is not signed
    cert_url = '/crt/%s.crt.pem' %  csr_key[:-8]
    response6 = self.client.get(cert_url)
    self.assert404(response6)
    self.assertEquals(response5.data, csr2_string)

  def test_get_csr_notfound(self):
    response = self.client.get('/csr/1234')
    self.assert404(response)
    
    # self.assertEquals(response.json['name'], 'FileNotFound'))

  def test_get_cacert(self):
    response = self.client.get('/crt/ca.crt.pem')
    self.assert200(response)
    crypto.load_certificate(crypto.FILETYPE_PEM, response.data)



