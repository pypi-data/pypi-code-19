import datetime
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django_api_base.utils import random_number_generator

REFRESH_TOKEN_EXPIRE_COUNT = getattr(settings, 'REFRESH_TOKEN_EXPIRE_COUNT', 10)
ACCESS_TOKEN_EXPIRE_DAYS = getattr(settings, 'ACCESS_TOKEN_EXPIRE_DAYS', 30)


def generate_access_token_expiry():
    return timezone.now() + timezone.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)


class DeviceID(models.Model):
    """
    Model for Saving Device Id
    """
    device_id = models.CharField(max_length=50)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.device_id


class AccessToken(models.Model):
    """For saving access tokens"""
    user = models.ForeignKey(User)
    token = models.CharField(max_length=50, default=random_number_generator)
    expires = models.DateField(default=generate_access_token_expiry)

    def __str__(self):
        return self.token


class RefreshToken(models.Model):
    """For storing the refresh tokens"""
    user = models.ForeignKey(User)
    token = models.CharField(max_length=50, default=random_number_generator)
    device_id = models.ForeignKey(DeviceID)
    expire_count = models.IntegerField(default=REFRESH_TOKEN_EXPIRE_COUNT)

    def __str__(self):
        return self.token


class UserProfile(models.Model):
    """
    Model for saving extra user credentials like access token, reset key etc.
    This model can be inherited to get make appropriate user profile models
    """
    CHOICE = (
        ('-', '-'),
        ('male', 'Male'),
        ('female', 'Female'),
    )
    user = models.OneToOneField(User)
    reset_key = models.CharField(max_length=30, blank=True, null=True, default='')
    reset_key_expiration = models.DateTimeField(default=None, blank=True, null=True)
    otp = models.CharField(max_length=500, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True, default=None)
    phone_number = models.BigIntegerField(default=0)
    gender = models.CharField(max_length=10, choices=CHOICE, default='-')
    date_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def set_reset_key(self):
        self.reset_key = random_number_generator()
        self.reset_key_expiration = timezone.now() + datetime.timedelta(hours=1)

    def verify_reset_key_expiry(self):
        if timezone.now() <= self.reset_key_expiration:
            return True
        else:
            return False

    def set_otp(self, length=4):
        raw_otp = random_number_generator(length, '0123456789')
        self.otp = make_password(raw_otp)
        self.otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
        self.raw_otp = raw_otp

    def verify_otp(self, raw_otp):
        if self.otp is not None:
            try:
                salt = self.otp.split('$')[2]
                hashed_otp = make_password(raw_otp, salt)
                if self.otp == hashed_otp:
                    if timezone.now() <= self.otp_expiry:
                        return True
                    else:
                        return False
            except IndexError:
                return None
        else:
            return None
