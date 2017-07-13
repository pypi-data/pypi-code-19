import ujson
import requests
import datetime
import time
import os
from ConfigParser import ConfigParser, NoOptionError
import ipaddress


class api:
    user = {}
    cookies = {}
    stack = None

    def __init__(self, stack='default', user=None, password=None, server=None):

        self.stack = stack
        self.users = {}

        if stack != 'default':
            self.config = dict()
            self.config = ConfigParser(allow_no_value=True)

            # Try to load files
            myfiles = (
                os.path.join(os.curdir, "picardapi.cfg"),
                os.path.join(os.curdir, ".picardapi.cfg"),
                os.path.join(os.path.expanduser("~"), "picardapi.cfg"),
                os.path.join(os.path.expanduser("~"), ".picardapi.cfg"),
            )
            for conffile in myfiles:
                self.config.read(conffile)

            # Check stack section existence
            if not self.config.has_section(stack):
                    print "Config file does not exist or has no section " + stack + ", exiting."
                    exit(1)

            # Set up user from config file
            try:
                self.users[self.config.get(self.stack, 'username')] = {
                    'un': self.config.get(self.stack, 'username'),
                    'pw': self.config.get(self.stack, 'password')
                }
                self.server = str(self.config.get(self.stack, 'server'))

            except NoOptionError:
                pass
        else:
            self.users = [{
                'un': user,
                'pw': password
            }]
            self.server = server

    @staticmethod
    def get_timestamp():
        """
            Gets a timestamp for logging

            Returns:
                str: Current timestamp
        """
        return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    def login(self, user=None, fake_ip=None, fake_time=None, fake_agent=None):
        """
        Logs in user with test user class, used to load session in test client

        Args:
            user (str): User to login with, by key
            fake_ip (str): Forged ip to send
            fake_time (datetime.datetime): Datatime object with forged timestamp
            fake_agent (str): Agent to use for call

        Returns:
            dict: Response
        """
        self.logout()
        params = {
            'name': self.users[user]['un'],
            'password': self.users[user]['pw']
        }
        rv = self.query('/auth/login',
                        method='post',
                        params=params,
                        fake_ip=fake_ip,
                        fake_time=fake_time,
                        fake_agent=fake_agent)

        if 'session' in rv.cookies:
            self.cookies['session'] = rv.cookies.get('session')

        return rv

    def logout(self, fake_ip=None, fake_time=None, fake_agent=None):
        """
        Log out user

        Args:
            fake_ip (str): Forged ip to send
            fake_time (datetime.datetime): Datatime object with forged timestamp
            fake_agent (str): Agent to use for call

        Returns:
            dict: Response
        """
        return self.query('/auth/logout',
                          method='post',
                          fake_ip=fake_ip,
                          fake_time=fake_time,
                          fake_agent=fake_agent)

    def validate_ip(self, myip):
        """
        Validate an ip address is properly formatted

        Args:
            myip (str): Ip address

        Returns:
            Bool
        """
        try:
            ipaddress.ip_address(myip)
        except ValueError:
            return False

        return True

    def query(self, query=None, params=None, method='get', fake_ip=None, fake_time=None, fake_agent=None, debug=False):
        """
        Query wrapper for doing api calls via test client

        Args:
            query (str): Query path
            params (dict): Query parameters
            method (str): Query method
            fake_ip (str): Forged ip to send
            fake_time (datetime.datetime): Datatime object with forged timestamp
            fake_agent (str): Agent to use for call
            debug (bool): Debug response by printing during call

        Returns:
            object: Response dictionary
        """
        # Set up valid api request
        if params is None:
            params = dict()

        func = getattr(requests, method, None)

        mycall = self.server + query

        myheaders = dict()
        myheaders['content-type'] = 'application/json'
        myheaders['X-Picard'] = 'X-Picard'
        myheaders['Origin'] = self.server + '/'

        # DEMO_MODE must be enabled on server to do this
        if fake_agent:
            myheaders['User-Agent'] = fake_agent

        if fake_ip and self.validate_ip(fake_ip):
            myheaders['X-Picard-Fake-IP'] = fake_ip
        if fake_time:
            # Translate from datetime into iso w/o timezone, thus this is localtime based on user IP
            myheaders['X-Picard-Fake-Localtime'] = fake_time.isoformat()

        method = method.lower()

        if method == 'post' or method == 'put':
            myresponse = func(mycall, data=ujson.dumps(params), headers=myheaders, cookies=self.cookies)
        elif method == 'get' or method == 'delete':
            myresponse = func(mycall, params={'p': ujson.dumps(params)}, headers=myheaders, cookies=self.cookies)
        else:
            return {'error': 'http method must be one of post, put, get, or delete.'}
        # Assuming json responses on endpoints as in api spec
        try:
            myresponse.json = ujson.loads(myresponse.text)
        except:
            myresponse.json = None

        if debug is True:
            print format(myresponse)
            print format(myresponse.json)

        return myresponse
