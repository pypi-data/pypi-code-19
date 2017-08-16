#!/usr/bin/env python
"""
skylinesms - a module to send sms using the Skylinesms REST apis, www.skylinesms.com
"""

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import json
import base64
import urllib

class SkylineSms(object):

    """ A class for handling communication with the Skyline SMS REST apis. """

    SEND_SMS_URL = 'http://skylinesms.com/api/v2/json/messages'
    CHECK_STATUS_URL = 'http://skylinesms.com/api/v2/json/delivery'
    BALANCE_URL = 'http://skylinesms.com/api/v2/json/balance'


    def __init__(self, app_key):
        """
           Visit your dashboard at http://skylinesms.com to locate your application key.
           This can be found under Developer/API credentials section.
        """

        self._token = app_key

    def _request(self, url, values=None):
        """ Send a request and read response.

            Sends a get request if values are None, post request otherwise.
        """

        url += "?{}".format(urllib.urlencode(values))

        request = urllib2.Request(url)

        try:
            connection = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            return {'status': 'Failed', 'message': str(e.reason)}
        except urllib2.URLError, e:
            return {'status': 'Failed', 'message': str(e.reason)}
        except httplib.HTTPException, e:
            return {'status': 'Failed', 'message': str(e.reason)}
        except Exception as exception:
            return {'status': 'Failed', 'message': str(exception)}

        response = connection.read()
        connection.close()


        try:
            result = json.loads(response.decode())
        except ValueError as exception:
            return {'status': 'Failed', 'message': str(exception)}

        return result

    def send_message(self, to_number, message, from_number=None):
        """ Send a message to the specified number and return a response dictionary.

            The numbers must be specified in international format starting without a '+'.
            Returns a dictionary that contains a 'reference' key with the sent message id value or
            contains 'status' and 'message' on error.
        """

        values = {'token': self._token, 'to': to_number, 'message': message}
        if from_number is not None:
            values['from'] = from_number
        else:
            values['from'] = 'skylinesms'

        return self._request(self.SEND_SMS_URL, values)

    def check_status(self, message_id):
        """ Request the status of a message with the provided id and return a response dictionary.

            Returns a dictionary that contains a 'delivery' key with the status value string or
            contains 'errorCode' and 'message' on error.
        """

        values = {'token': self._token, 'reference': message_id}
        return self._request(self.CHECK_STATUS_URL, values)

    def balance(self):
        values = {'token': self._token}
        return self._request(self.BALANCE_URL, values)

def _main():
    """ A simple demo to be used from command line. """
    import sys

    def log(message):
        print(message)

    def print_usage():
        log('usage: %s <application key> send <number> <message> <from_number>' % sys.argv[0])
        log('       %s <application key> status <message_id>' % sys.argv[0])
        log('       %s <application key> balance' % sys.argv[0])

    if len(sys.argv) > 4 and sys.argv[2] == 'send':
        key, number, message = sys.argv[1], sys.argv[3], sys.argv[4]
        client = SkylineSms(key)
        if len(sys.argv) > 6:
            log(client.send_message(number, message, sys.argv[6]))
        else:
            log(client.send_message(number, message))
    elif len(sys.argv) > 2 and sys.argv[2] == 'status':
        key, message_id = sys.argv[1], sys.argv[3]
        client = SkylineSms(key)
        log(client.check_status(message_id))
    elif len(sys.argv) > 2 and sys.argv[2] == 'balance':
        key = sys.argv[1]
        client = SkylineSms(key)
        log(client.balance())
    else:
        print_usage()
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    _main()
