#!/usr/bin/env python

# Dependencies
import requests
import hmac
from datetime import datetime
import hashlib
import json

class purple(object):

    # Class attributes


    # Instance attributes
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

        # The request time has to be defined when the instance is created because the datetime is used in both
        # the plaintext api request and the hashed signature, and the values have to match.
        self.__request_time = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        self.__venue = ''
        self.__date_from = ''
        self.__date_to = ''

        # This determines what the api request will query for.
        # It will default to 'venue'; the alternative option is 'visitor'.
        self.__target = 'venue'

    def __generate_url(self):
        if self.__target == 'venue':
            return 'https://purpleportal.net/api/company/v1/venues'

        elif self.__target == 'visitor':

            # If the user HASN'T passed the from/to dates, then the last part of the request url will be missing:
            url_end = ''

            # If the user HAS passed the from/to dates, then this creates the last part of the request url:
            if self.__date_from != '' and self.__date_to != '':
                url_end = '?from='+self.__date_from+'&to='+self.__date_to

            return 'https://purpleportal.net/api/company/v1/venue/'+self.__venue+'/visitors'+url_end

    def __generate_signature(self):
        line_1 = 'application/json\n'
        line_2 = 'purpleportal.net\n'

        if self.__target == 'venue':
            line_3 = '/api/company/v1/venues\n'
        elif self.__target == 'visitor':
            if self.__date_from == '' and self.__date_to == '':
                line_3 = '/api/company/v1/venue/'+self.__venue+'/visitors'+'\n'
            elif self.__date_from != '' and self.__date_to != '':
                line_3 = '/api/company/v1/venue/'+self.__venue+'/visitors?from='+self.__date_from+'&to='+self.__date_to+'\n'

        line_4 = self.__request_time

        return str(line_1+line_2+line_3+line_4+'\n\n')

    def __generate_hash(self):
        # String must be converted to bytes for Python 3 compatibility.
        pkey_bytes = bytes(self.private_key, 'latin-1')
        sig_bytes = bytes(self.__generate_signature(), 'latin-1')

        hash_message = hmac.new(
            pkey_bytes,
            sig_bytes,
            hashlib.sha256
        ).hexdigest()

        return hash_message

    def __generate_header(self):
        header = {'Host':'purpleportal.net',
                  'Accept':'*/*',
                  'Content-Type':'application/json',
                  'Content-Length':'0',
                  'Date':self.__request_time,
                  'X-API-Authorization':self.public_key+":"+self.__generate_hash()}

        return header

    def venues_json(self):
        """Returns a json object containing full details of all venues in the Purple instance.
        """

        self.__target = 'venue'
        url = self.__generate_url()
        get_request = requests.get(url, headers = self.__generate_header())
        venues_json = get_request.json()

        return venues_json

    def venues(self):
        """Returns a simple dictionary with the format:
            {'venue name':'venue unique id'}"""

        venue_json = self.venues_json()
        if venue_json['success'] == False:
            return venue_json
        names = [venue_json['data']['venues'][venue]['name'] for venue in range(len(venue_json['data']['venues']))]
        ids = [venue_json['data']['venues'][venue]['id'] for venue in range(len(venue_json['data']['venues']))]
        venue_dict = {}
        for venue in range(len(venue_json['data']['venues'])):
            venue_dict.update({names[venue]: ids[venue]})

        return venue_dict

    def visitor_json(self, venue, date_from='', date_to=''):
        """Returns a dictionary of all visitors to a specified venue.
        To obtain the unique venue IDs run .venues() first to get a full list.
        If no dates are passed as arguments default query is for visitors who are online now.

        Args:

            * venue: unique ID representing the venue, e.g. 12324.
            * date_from: optional argument specifying start of date range to be queried. Date format must be YYYYMMDD.
            * date_to: optional argument specifying end of date range to be queried. Date format must be YYYYMMDD.


        """

        #Pass the user's variables into the Purple instance.
        self.__target = 'visitor'
        self.__venue = venue
        self.__date_from = date_from
        self.__date_to = date_to

        get_request = requests.get(self.__generate_url(), headers = self.__generate_header())
        visitor_json = get_request.json()

        return visitor_json
