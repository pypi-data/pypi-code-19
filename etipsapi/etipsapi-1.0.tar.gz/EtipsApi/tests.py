""" unit tests """
import unittest
import os
import EtipsApi

REQUEST = EtipsApi.Request(os.environ['E5_HOST'], os.environ['E5_PORT'])
USERNAME = os.environ['E5_USERNAME']
PASSWORD = os.environ['E5_PASSWORD']

class Connectivity(unittest.TestCase):

    def testCanPing(self):
        self.assertTrue(REQUEST.ping())

class Authentication(unittest.TestCase):

    def testCanAuthenticate(self):
        self.assertTrue(REQUEST.authenticate(USERNAME, PASSWORD))
    def testCannotAuthenticateWithoutCredentials(self):
        with self.assertRaises(EtipsApi.AuthError):
            REQUEST.authenticate('', '')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
