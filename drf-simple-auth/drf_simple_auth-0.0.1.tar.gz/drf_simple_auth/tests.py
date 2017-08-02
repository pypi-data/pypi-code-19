from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import AuthToken


class LoginAPITestCase(TestCase):

    def test_user_can_login(self):
        user = get_user_model().objects.create_user('test', email='test', password='test')

        client = APIClient()

        response = client.post(reverse('auth-login'), {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        auth_token = AuthToken.objects.get(user=user)

        data = response.json()
        token = data['token']
        self.assertEqual(token, auth_token.token)

    def test_user_cant_login_with_invalid_username(self):
        get_user_model().objects.create_user('test', email='test', password='test')

        client = APIClient()

        response = client.post(reverse('auth-login'), {'username': 'invalid', 'password': 'test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = response.json()
        self.assertEqual(data, {u'detail': u'Invalid email or password.  Please try logging in again.'})

    def test_user_cant_login_with_invalid_password(self):
        get_user_model().objects.create_user('test', email='test', password='test')

        client = APIClient()

        response = client.post(reverse('auth-login'), {'username': 'test', 'password': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = response.json()
        self.assertEqual(data, {u'detail': u'Invalid email or password.  Please try logging in again.'})

    def test_user_can_login_with_device(self):
        user = get_user_model().objects.create_user('test', email='test', password='test')

        client = APIClient()

        response = client.post(reverse('auth-login'), {'username': 'test', 'password': 'test', 'device_id': 'device-1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        auth_token = AuthToken.objects.get(user=user, device_id='device-1')

        data = response.json()
        token = data['token']
        self.assertEqual(token, auth_token.token)

        # Same device ID should return same token
        response = client.post(reverse('auth-login'), {'username': 'test', 'password': 'test', 'device_id': 'device-1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        token = data['token']
        self.assertEqual(token, auth_token.token)

        # Different device ID should return different token
        response = client.post(reverse('auth-login'), {'username': 'test', 'password': 'test', 'device_id': 'device-2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        auth_token = AuthToken.objects.get(user=user, device_id='device-2')

        data = response.json()
        token = data['token']
        self.assertEqual(token, auth_token.token)


class SignupAPITestCase(TestCase):

    def test_user_can_signup(self):
        client = APIClient()

        response = client.post(reverse('auth-signup'), {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(username='test')
        self.assertEqual(user.email, user.username)

        auth_token = AuthToken.objects.get(user=user)

        data = response.json()
        token = data['token']
        self.assertEqual(token, auth_token.token)

    def test_user_cant_signup_with_same_username(self):
        get_user_model().objects.create_user('test', email='test', password='test')

        client = APIClient()

        response = client.post(reverse('auth-signup'), {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(data, {u'detail': u'Username already taken'})
