""" unit tests """
import unittest
import os
import EtipsApi

def new_request():
    """ creates a new request """
    return EtipsApi.Request(os.environ['E5_HOST'], os.environ['E5_PORT'])

class Connectivity(unittest.TestCase):

    def testCanPing(self):
        self.assertTrue(new_request().ping())

class Authentication(unittest.TestCase):

    def testCanAuthenticate(self):
        request = new_request()
        self.assertFalse(request.is_authenticated())
        self.assertTrue(request.authenticate(
            os.environ['E5_USERNAME'],
            os.environ['E5_PASSWORD']
        ))
        self.assertTrue(request.is_authenticated())
    def testCannotAuthenticateWithoutCredentials(self):
        with self.assertRaises(EtipsApi.AuthError):
            new_request().authenticate('', '')
        self.assertFalse(new_request().is_authenticated())

def main():
    unittest.main()

if __name__ == '__main__':
    main()
