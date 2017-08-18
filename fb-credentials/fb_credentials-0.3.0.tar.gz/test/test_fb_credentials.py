import unittest
import nose.tools
from nose_parameterized import parameterized
import mock

import shutil, tempfile
from os import path

import fb_credentials

@parameterized([ # token, username, password
    ('a', 'a', ''), # token and username
    ('a', '', 'a'), # token and password
    ('', 'a', ''), # username and no password
    ('', '', 'a'), # password and no username
])

def test_FogBugz_raiseIfWrongCredentialOptionsProvided(token, username, password):
    nose.tools.assert_raises(TypeError, fb_credentials.FogBugz, '', '', token=token,
                             username=username, password=password)

@mock.patch('fb_credentials.get_credential', side_effect=['token', 'username', 'pwd'])
def test_FogBugzNoUserNameNorToken(mock_get_credential):
    mock_fogbugz = mock.Mock()
    ret = fb_credentials.FogBugz(mock_fogbugz, 'hostname', storeCredentials=True)
    nose.tools.assert_equals(mock_get_credential.call_count, 3)
    ret.logon.assert_called_once_with('username', 'pwd')
    # Also test storeCredentials
    nose.tools.assert_equals(ret.username, 'username')
    nose.tools.assert_equals(ret.password, 'pwd')

def test_FogBugzWithUsernameNoToken():
    mock_fogbugz = mock.Mock()
    ret = fb_credentials.FogBugz(mock_fogbugz, 'hostname', username='uUsername', password='uPassword')
    ret.logon.assert_called_once_with('uUsername', 'uPassword')

@mock.patch('fb_credentials.validate_token')
def test_FogBugzWithValidToken(mock_validate_token):
    mock_fogbugz = mock.Mock()
    mock_validate_token.return_value = True
    ret = fb_credentials.FogBugz(mock_fogbugz, 'hostname', token='uToken')
    mock_fogbugz.assert_called_once_with('hostname', token='uToken')

@mock.patch('fb_credentials.validate_token')
@mock.patch('fb_credentials.get_credential')
def test_FogBugzWithInvalidToken(mock_validate_token, mock_get_credential):
    mock_fogbugz = mock.Mock()
    mock_validate_token.return_value = False
    ret = fb_credentials.FogBugz(mock_fogbugz, 'hostname', token='uToken')
    mock_get_credential.assert_called_once()

@mock.patch('fb_credentials.FogBugz')
def test_FogBugz_cm(mock_FogBugz):
    with fb_credentials.FogBugz_cm('a', 'b') as cm:
        pass
    mock_FogBugz.assert_called_once_with('a', 'b')
    nose.tools.assert_equals(cm.logoff.call_count, 0)

    with fb_credentials.FogBugz_cm('a', 'b', logoff=True) as cm:
        pass
    nose.tools.assert_equals(cm.logoff.call_count, 1)

class test_validate_token(unittest.TestCase):
    '''Tests for validate_token'''

    def test_validate_token_noToken(self):
        self.assertFalse(fb_credentials.validate_token('host', None))

class test_get_credential(unittest.TestCase):
    '''Tests for get_credential'''

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        with open(path.join(self.test_dir, '.fogbugzrc'), 'w') as f:
            f.write('pref.username = uName\ndummyLine\npref.password = pwd')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_credentials_NoArgsNoFogbugzrcNoInteractive(self):
        fb_credentials.os.path.expanduser = mock.Mock(return_value='/FolderThatDoesNotExist')
        ret = fb_credentials.get_credential('username', interactive=False)
        self.assertFalse(ret)
        self.assertEquals(fb_credentials.os.path.expanduser.call_count, 1)

    def test_get_credentials_NoArgsNoFogbugzrc_username(self):
        fb_credentials.os.path.expanduser = mock.Mock(return_value='/FolderThatDoesNotExist')
        fb_credentials.get_input = mock.Mock(return_value='myName')
        ret = fb_credentials.get_credential('username')
        self.assertEquals(ret, 'myName') #username
    
    def test_get_credentials_NoArgsNoFogbugzrc_password(self):
        fb_credentials.os.path.expanduser = mock.Mock(return_value='/FolderThatDoesNotExist')
        fb_credentials.getpass.getpass = mock.Mock(return_value='myPwd')
        ret = fb_credentials.get_credential('password')
        self.assertEquals(ret, 'myPwd') #password
    
    def test_read_fogbugzrc_file(self):
        ret = fb_credentials.get_credential('username', path.join(self.test_dir, '.fogbugzrc'))
        self.assertEquals(ret, 'uName')
    
    def test_unsupported_credential(self):
        self.assertRaises(ValueError, fb_credentials.get_credential, 'fakeCred')
