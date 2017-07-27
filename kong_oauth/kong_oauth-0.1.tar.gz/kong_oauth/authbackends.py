from django.conf import settings
from django.contrib.auth import get_user_model
import requests

class AppointmentGuruBackend(object):

    def authenticate(self, request, username=None, password=None):
        url = '{}/api/auth/login/'.format(settings.APPGURU_URL)
        data = {
            "username": username,
            "password": password
        }
        result = requests.post(url, data)
        if result.status_code == 200:
            user = get_user_model()
            user.id = result.json().get('id')
            user.username = result.json().get('id')
            return user
        else:
            return None

    def get_user(self, user_id):
        #todo: get from API
        user = get_user_model()
        user.id = result.json().get('id')
        user.username = result.json().get('id')
