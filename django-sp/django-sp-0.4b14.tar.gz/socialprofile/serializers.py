from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from socialprofile.models import SocialProfile, Group

from rest_framework import serializers

# Serializers define the API representation.
class SocialProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SocialProfile
        fields = ('url', 'username', 'email', 'is_staff')
		
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
