from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object

class FakeRequest(object):
    """
    A replacement for Django's Request object. This is only used for unit
    tests at the moment. If you're not using Django and need to create such
    a class have a look at the source for the tests fake request class in
    in tests/request.py
    """
    #: Boolean, if the connection is secured or not
    secure = False

    #: HTTP headers like in the PHP $_SERVER variable, see
    #: http://php.net/manual/en/reserved.variables.server.php
    headers = {}

    #: Cookies... work in progress
    COOKIES = False

    def __init__(self, headers):
        """
        Configure request object according to the headers we get

        :param headers: See http://www.python-requests.org/en/master/
        :type headers: dict
        :rtype: None
        """
        self.headers = headers
        if self.headers['HTTPS']:
            self.secure = True  # TODO test this..
        if self.headers['HTTP_REFERER']:
            self.url = self.headers['HTTP_REFERER']

    def is_secure(self):
        """
        Returns a boolean, if the connection is secured

        :rtype: bool
        """
        return self.secure
