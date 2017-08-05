# coding: utf-8

'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from __future__ import absolute_import

import os
import sys
import unittest

from som.api.radiology import Client
from som.api.validators.responses import receive_identifiers
from som.api.validators.requests import validate_identifiers
from som.utils import read_json

here = os.path.dirname(os.path.realpath(__file__))

class TestDevelopersApi(unittest.TestCase):
    """ DevelopersApi unit tests"""


    def setUp(self):
        self.client = Client()
        self.identifiers = read_json('%s/data/developers_uid.json' %(here))


    def tearDown(self):
        pass

    def test_uid(self):
        '''Test case for uid
        Accepts a list of identified items, returns a list of study specific identifiers
        '''

        print("Case 1: Formatting of identifiers input is correct.")
        self.assertTrue(validate_identifiers(self.identifiers))

        print("Case 2: Respones returns status 200, json object")
        response = self.client.deidentify(self.identifiers)
        self.assertTrue(isinstance(response,list))       

        # Validate response
        print("Case 3: Formatting of identifiers response is correct.")
        self.assertTrue(receive_identifiers(response))

        # Assert we have the same number of inputs and outputs
        print("Case 4: Response returns same number of identifiers as given, %s" %(len(response)))
        self.assertEqual(len(response),len(self.identifiers['identifiers']))


if __name__ == '__main__':
    unittest.main()
