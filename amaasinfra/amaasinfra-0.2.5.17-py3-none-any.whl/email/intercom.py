"""
This module is used to handle Rest APIs of Intercom
"""
import json
import requests


class IntercomClient(object):
    """
    This is a client class to handle Intercom Rest API calls
    """
    def __init__(self, app_id='n0cz9mcf',
                 access_token='dG9rOjg4MTAyZmY2XzljNDlfNGE4YV84ZGJiXzc5YzI1N2ExMjI5YjoxOjA='):
        self.app_id = app_id
        self.access_token = access_token
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json',
                        'authorization': 'Bearer {}'.format(access_token)}

    def create_leads(self, payload,
                     end_point='https://api.intercom.io/contacts'):
        """
        This method consumes Intercom API to create new leads record.
        Only email info required
        """
        leads = json.loads(requests.get(''.join([end_point, '?email=',
                                                 payload['email']]),
                                        headers=self.headers).text)
        if leads['total_count'] == 0:
            return requests.post(end_point,
                                 data=json.dumps(payload),
                                 headers=self.headers)
        else:
            return False

    def create_user(self, payload, end_point='https://api.intercom.io/users'):
        """
        This method consumes Intercom API to create new user account
        """
        return requests.post(end_point,
                             data=json.dumps(payload),
                             headers=self.headers)
