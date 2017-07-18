'''
    How we define a user for our website
'''

from transcend.services import *
x= 2
class User():
    '''
        Class to define a user
    '''
    drops = ['analytics']
    service_to_class = {
        'instagram': instagram.Instagram,
        'spotify': spotify.Spotify,
        'rescuetime': rescuetime.RescueTime,
        'moves': moves.Moves,
        'facebook': facebook.Facebook,
        'twitter': twitter.Twitter,
        'linkedin': linkedin.LinkedIn,
        'youtube': youtube.YouTube,
        'reddit': reddit.Reddit,
        'fitbit': fitbit.Fitbit,
        'underarmour': underarmour.UnderArmour
    }

    def __init__(self, user):
        '''
            Intialize user and save values
        '''
        self._id = user['_id']
        self.raw = user
        self.raw_data = {}
        for key in filter(lambda x: x not in User.drops, self.raw.keys()):
            self.raw_data[key] = self.raw[key]

        # services to be used
        self.services = map(str, self.raw_data['services'])

        # clean the data
        self.setup_services()

    def __str__(self):
        return '<Transcend-User: %s>' % self._id

    def __repr__(self):
        return '<Transcend-User: %s>' % self._id

    def setup_services(self):
        self.data = {}
        for service in self.services:
            serv_obj = data_service.DataService
            if service in User.service_to_class:
                self.data[service] = User.service_to_class[service](
                    self,
                    self.raw_data['services'][service], service)
            else:
                self.data[service] = data_service.DataService(
                    self, self.raw_data['services'][service], service)


