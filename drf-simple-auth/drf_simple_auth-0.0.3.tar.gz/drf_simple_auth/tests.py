from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework.views import APIView

from .auth import SimpleAuthTokenAuthentication
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
        self.assertEqual(token, auth_token.key)

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
        self.assertEqual(token, auth_token.key)

        # Same device ID should return same token
        response = client.post(reverse('auth-login'), {'username': 'test', 'password': 'test', 'device_id': 'device-1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        token = data['token']
        self.assertEqual(token, auth_token.key)

        # Different device ID should return different token
        response = client.post(reverse('auth-login'), {'username': 'test', 'password': 'test', 'device_id': 'device-2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        auth_token = AuthToken.objects.get(user=user, device_id='device-2')

        data = response.json()
        token = data['token']
        self.assertEqual(token, auth_token.key)


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
        self.assertEqual(token, auth_token.key)

    def test_user_cant_signup_with_same_username(self):
        get_user_model().objects.create_user('test', email='test', password='test')

        client = APIClient()

        response = client.post(reverse('auth-signup'), {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        data = response.json()
        self.assertEqual(data, {u'detail': u'Username already taken'})

    def test_username_email_address_validation(self):
        with self.settings(CHECK_USERNAME_IS_EMAIL=True):
            client = APIClient()

            response = client.post(reverse('auth-signup'), {'username': 'test', 'password': 'test'})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            data = response.json()
            self.assertEqual(data, {u'detail': u'Please provide a valid email address.'})


class MockView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response({'success': True})


urlpatterns = [
    url(
        r'^token-authenticated-view/$',
        MockView.as_view(authentication_classes=[SimpleAuthTokenAuthentication]),
        name='token-authenticated-view'
    ),
]


@override_settings(ROOT_URLCONF='drf_simple_auth.tests')
class APIAuthTestCase(TestCase):

    def test_user_can_access_authenticated_endpoint(self):
        client = APIClient()

        response = client.get(reverse('token-authenticated-view'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user = get_user_model().objects.create_user('test', email='test', password='test')
        token = AuthToken.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION='DToken ' + token.key)

        response = client.get(reverse('token-authenticated-view'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
