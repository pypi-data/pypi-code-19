from picardapi import PicardApi
from faker import Factory
import pickle
import os
from Mobile_uagent import MobileAgent
import random
import requests
from pprint import pprint
from babel import Locale
import uuid
from unidecode import unidecode
from contextlib import closing
from os.path import basename


class Simulate(object):
    api = None
    fakers = dict()
    usermap = None
    verbose = False

    def __init__(self, stack, usermap=None, verbose=False):
        self.stack = stack
        self.verbose = verbose

        # Set up api client, references option set from .picardapi.cfg file [stackid]
        self.api = PicardApi.api(stack)

        self.faker = self.get_locale_faker('en_US')

        # User map file location can be specified in the .picardapi.cfg file.
        # In the [stackid] section look for the line that starts with usermap=
        if usermap is not None:
            self.usermap = usermap
        else:
            try:
                self.usermap = self.api.config.get(stack, 'usermap')
            except Exception, e:
                self.usermap = './simulate.user.map'

        if self.verbose:
            print "LaForger engaging for stack %s" % self.stack

    def fakeloc_spec(self, targettype='city', supertarget=None, supertype=None):
        """
        Generate random location per spec, slower but more specific

        Args:
            targettype (str): Type of target to find (city/state/country/continent)
            supertarget (str): Supertarget name to find target in
            supertype (str): Type of supertarget to find target in

        Returns:
            tuple
        """
        params = {
            'targettype': targettype,
            'count': 1
        }
        if supertarget:
            params['supertarget'] = supertarget
        if supertype:
            params['supertype'] = supertype

        rv = self.api.query('/geoiptool/targetList', method='get', params=params)
        return rv.json['list'][0]

    def fakeloc_get(self,target, targettype='city', supertarget=None, supertype=None):
        """
        Gets full location data from small hints

        Args:
            target (str):
            targettype (str):
            supertarget (str):
            supertype (str):

        Returns:
            tuple
        """
        params = {
            'target': target,
            'targettype': targettype,
        }
        if supertarget:
            params['supertarget'] = supertarget
        if supertype:
            params['supertype'] = supertype
        rv = self.api.query('/geoiptool/targetGuess', method='get', params=params)
        return rv.json['list'][0]

    def fakeloc_toip(self, target, targettype='city', supertarget=None, supertype=None, count=1):
        """
        Translate a city and state to a random IP

        Args:
            target (str): Target name
            targettype (str): Target type (city/state/country/continent)
            supertarget (str): Supertarget name
            supertype (str): Type of supertarget

        Returns:
            IP Address
        """
        params = {
            "type": targettype,
            "target": target,
            "count": count,
            "location": True
        }
        if supertarget:
            params['supertarget'] = supertarget
        if supertype:
            params['supertype'] = supertype

        rv = self.api.query('/geoiptool/randomList', method='get', params=params)
        if len(rv.json['ipaddresses']) > 0:
            return rv.json['ipaddresses']
        else:
            return None

    # Load users from file
    def load_users(self):
        """
        Loads users form localmap for reuse
        """
        if os.path.isfile(self.usermap):
            print "Loading users from %s" % (self.usermap,)
            users = pickle.load(open(self.usermap, 'r'))
            self.api.users = dict(self.api.users.items() + users.items())
            return True
        else:
            if self.verbose is True:
                print "Map file %s does not exist, nothing to load, creating this run." % (self.usermap,)
            return False

    # Create individual user
    def create_user(self, user, ip, registration_date, registration_device):
        """
        Create user for tests

        Args:
            user (dict): User object to create
            ip (list: list of ip addresses
            registration_date (datetime): datetime of user registration
            registration_device (str): string representing header from user registration device
        """
        try:
            params = {
                'name': user['login']['username'],
                'email': user['email'],
                'password': "password123"
            }
            try:
                rv = self.api.query('/auth/user',
                                    method='post',
                                    params=params,
                                    fake_ip=ip[0][0],
                                    fake_time=registration_date,
                                    fake_agent=registration_device)
            except Exception, e:
                print "Failed creating user"
                return False

            if rv.status_code != 200:
                print "User already exists"
                return False

            myid = rv.json['id']

            user['id'] = myid
            user['username'] = user['login']['username']
            user.pop('login')
            self.api.users[user['username']] = user
            self.api.users[user['username']]['un'] = user['username']
            self.api.users[user['username']]['pw'] = 'password123'
            self.save_users()
            self.api.login(user['username'],
                           fake_ip=ip[0][0],
                           fake_time=registration_date,
                           fake_agent=registration_device)

            user.pop('registered')
            user_copy = user.copy()
            user_copy.pop('pw')
            user_copy['image_filename'] = basename(user['picture']['medium'])
            user_copy['profileId'] = myid
            user_params = {
                'doctypename': 'userProfile',
                'document': user_copy,
                '_id': myid
            }

            try:
                rv = self.api.query('/custom/document',
                                    method="post",
                                    params=user_params,
                                    fake_ip=ip[0][0],
                                    fake_time=registration_date,
                                    fake_agent=registration_device)
            except Exception, e:
                raise Exception("User profile document cannot be added.  This should not happen after "
                                "creating the user account succeeds.  Look into this")

            try:
                # get the user profile image and upload to S3
                resp = requests.get(user['picture']['medium'], stream=True)
                with open(basename(user['picture']['medium']), 'wb') as f:
                    f.write(resp.content)

                rv2 = self.api.query('/files/file', method="post", params={'id': rv.json['id'], 'filename': basename(user['picture']['medium'])})
                with open(basename(user['picture']['medium']), 'rb') as content_file:
                    requests.put(rv2.json['url'], data=content_file, headers={"Content-Type":"image/jpeg"})
                os.remove(basename(user['picture']['medium']))

                # with closing(requests.get(user['picture']['medium'], stream=True)) as r:
                #     requests.put(rv2.json['url'], data=r, headers={"Content-Type": "image/jpeg"})
            except Exception, e:
                print 'Cannot upload user image'
            return user
        except Exception, e:
            print e


    @staticmethod
    def define_user(user, keep_password=False):
        user_type = user['behavior']['user_type']
        days_since_first_use = user['behavior']['days_since_first_use']
        if user_type == 'never':
            user['behavior']['total_days_using'] = 0
            user['behavior']['num_uses'] = 0
        elif user_type == 'once':
            user['behavior']['total_days_using'] = 1
            user['behavior']['num_uses'] = 1
            user['behavior']['days_using'] = sorted([random.randint(0, days_since_first_use) for x in range(user['behavior']['num_uses'])])
        elif user_type == 'steady':
            user['behavior']['total_days_using'] = days_since_first_use - random.sample([0,0,0,0,0,1,2,3],1)[0]
            user['behavior']['num_uses'] = int(user['behavior']['total_days_using'] * random.uniform(0.6, 0.8))
            user['behavior']['days_using'] = sorted([random.randint(days_since_first_use - user['behavior']['total_days_using'], days_since_first_use) for x in range(user['behavior']['num_uses'])])
        elif user_type == 'abandoner':
            if days_since_first_use < 20:
                user['behavior']['days_since_first_use'] = random.randrange(20, 100, 1)
                days_since_first_use = user['behavior']['days_since_first_use']
            user['behavior']['total_days_using'] = random.randint(0,10)
            user['behavior']['num_uses'] = int(user['behavior']['total_days_using'] * random.uniform(0.6, 0.8))
            user['behavior']['days_using'] = sorted([random.randint(days_since_first_use - user['behavior']['total_days_using'], days_since_first_use) for x in range(user['behavior']['num_uses'])])

        user['behavior']['days_using'].reverse()
        if not keep_password:
            user['login'].pop("password", None)
        return user

    def save_users(self):
        """
        Save all users to map, overwriting
        """
        pickle.dump(self.api.users, open(self.usermap, 'w'))

    def get_locale_faker(self, locale):
        """
        Generates a faker based on locale. For invalid faker, returns en_US faker

        Args:
            locale (str): Locale code

        Returns:
            Factory
        """
        if locale not in self.fakers:
            try:
                self.fakers[locale] = Factory.factory(locale)
                self.fakers[locale].add_provider(MobileAgent)
                return self.fakers[locale]
            except AttributeError:
                if 'en_US' not in self.fakers:
                    self.fakers['en_US'] = Factory.create('en_US')
                    self.fakers[locale].add_provider(MobileAgent)
                return self.fakers['en_US']
        else:
            return self.fakers[locale]

    # Create n users with random identities and locations
    def create_users(self, start=1, count=100, target=None, targettype='city', supertype=None, supertarget=None,
                     agent=None):
        """
        Create users for tests

        Args:
            start (int): User number to start on, for batch creation
            count (int): Number of users to generate
            target (str): Target to generate IPs (ie, Seattle)
            targettype (str): Type of target (city/state/country/continent)
            supertarget (str): Type of target (ie, Washington)
            supertype (str): Supertype of supertarget (city/state/country/continent)
            agent (str): User Agent to send on requests
        """
        i = 0
        newcount = 0
        self.api.login('admin')
        for i in range(start, start+count):
            if i in self.api.users:
                if self.verbose is True:
                    print "User %d already exists in map, unable to overwrite" % (i,)
                continue
            else:
                try:
                    if target is None:
                        myip = None
                        while myip is None:
                            (city, state, region, country, continent, code) = self.fakeloc_spec(targettype=targettype,
                                                                                                supertype=supertype,
                                                                                                supertarget=supertarget)
                            if city is None:
                                print "No such place found, no users created."
                                return False

                            myip = self.fakeloc_toip(target=city,
                                                     targettype=targettype,
                                                     supertype=supertype,
                                                     supertarget=supertarget)[0]

                    else:
                        (city, state, region, country, continent, code) = self.fakeloc_get(target=target,
                                                                                           targettype=targettype,
                                                                                           supertype=supertype,
                                                                                           supertarget=supertarget)

                        myip = self.fakeloc_toip(target=target,
                                                 targettype=targettype,
                                                 supertype=supertype,
                                                 supertarget=supertarget)

                    myloc = Locale.parse('und_' + code)
                    mylocale = myloc.language + '_' + code
                    mydomain = ['yahoo.com', 'gmail.com', 'hotmail.com'][random.choice(range(3))]

                    # Faker can generate all sorts of interesting stuff, see http://www.joke2k.net/faker/
                    # here we generate names based on locale code
                    myfaker = self.get_locale_faker(mylocale)
                    firstname = unidecode(myfaker.first_name()).replace(" ", "")
                    lastname = unidecode(myfaker.last_name()).replace(" ", "")
                    myemail = unidecode(myfaker.safe_email()).replace(" ", "")

                    myusername = None
                    iter = 0
                    while myusername is None:
                        iter += 1
                        if iter > 100:
                            raise Exception("Cannot create a unique user name.")
                        rv = self.api.query('/auth/userList', method='get', params={"limit": 10000})
                        tmp = unidecode(myfaker.user_name()).replace(" ", "")
                        try:
                            next(index for (index, d) in enumerate(rv.json['users']) if d["name"] == tmp)
                        except Exception, e:
                            myusername = tmp
                    mypassword = "password123"

                    params = {
                        'name': myusername,
                        'email': myemail,
                        'password': mypassword
                    }

                    try:
                        rv = self.api.query('/auth/user', method='post', params=params)
                    except Exception, e:
                        print e

                    if rv.status_code != 200:
                        raise Exception('Failed to create user ' + myusername + ' with status ' + str(rv.status_code) +
                                        ' ' + rv.reason + ': ' + str(rv.json))
                    myid = rv.json['id']

                    newcount += 1

                    if agent is None and random.randint(1, 100) > 95:
                        agent = myfaker.mobile_agent()
                    else:
                        agent = myfaker.user_agent()

                    self.api.users[i] = {
                        'un': myusername,
                        'pw': mypassword,
                        'name': firstname + ' ' + lastname,
                        'id': myid,
                        'city': city,
                        'state': state,
                        'region': region,
                        'country': country,
                        'continent': continent,
                        'locale': mylocale,
                        'ip': myip[0],
                        'latitude': myip[1],
                        'longitude': myip[2],
                        'useragent': agent
                    }
                    if self.verbose is True:
                        print "Created user %s who is %s from %s, %s @ %s" % (myusername, self.api.users[i]['name'], city,
                                                                              state, myip)
                except Exception, e:
                    print e

        # Dump all users to map for later user
        if self.verbose is True:
            print "%d new users, %d total users. Saving to map." % (newcount, len(self.api.users))
        self.save_users()
        self.api.logout()


    # Create n users with random identities and locations
    def create_users_usa(self, start=1, count=100, target=None, targettype='city', supertype=None, supertarget=None,
                     agent=None):
        """
        Create users for tests

        Args:
            start (int): User number to start on, for batch creation
            count (int): Number of users to generate
            target (str): Target to generate IPs (ie, Seattle)
            targettype (str): Type of target (city/state/country/continent)
            supertarget (str): Type of target (ie, Washington)
            supertype (str): Supertype of supertarget (city/state/country/continent)
            agent (str): User Agent to send on requests
        """
        i = 0
        newcount = 0
        self.api.login('admin')
        seed = str(uuid.uuid4().get_hex().upper()[0:10])
        users = requests.get('https://randomuser.me/api/?results=' + str(count*20) + '&nat=us&seed=' + seed).json()['results']
        for i in range(start, start+count):
            try:
                myip = None
                iter = 0
                while myip is None:
                    user = users.pop(0)
                    myip = self.fakeloc_toip(target = user['location']['city'],
                                             supertype="city",
                                             supertarget=user['location']['city'])
                    iter += 1
                    if iter > 100:
                        raise Exception('Cannot find IP address for 100 cities in a row.  City names are probably not real.')

                params = {
                    'name': user['login']['username'],
                    'email': user['email'],
                    'password': "password123"
                }
                try:
                    rv = self.api.query('/auth/user', method='post', params=params)
                except Exception, e:
                    continue

                if rv.status_code != 200:
                    continue
                myid = rv.json['id']

                newcount += 1

                user['id'] = myid
                user['username'] = user['login']['username']
                user.pop('login')
                user.pop('registered')
                user_params = {
                    'doctypename': 'userProfile',
                    'document': user
                }
                try:
                    rv = self.api.query('/custom/document', method="post", params=user_params)
                except Exception, e:
                    raise Exception("User profile document cannot be added.  This should not happen after "
                                    "creating the user account succeeds.  Look into this")

                # Add the new user to the list of all users
                self.api.users[i] = user

                if self.verbose is True:
                    print "Created user %s who is %s from %s, %s @ %s" % (user['username'],
                                                                          self.api.users[i]['name']['first'],
                                                                          user['location']['city'],
                                                                          user['location']['state'],
                                                                          myip)
            except Exception, e:
                print e

        # Dump all users to map for later user
        if self.verbose is True:
            print "%d new users, %d total users. Saving to map." % (newcount, len(self.api.users))
        self.save_users()
        self.api.logout()
