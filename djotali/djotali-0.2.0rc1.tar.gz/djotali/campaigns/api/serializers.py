# coding: utf-8
from rest_framework import serializers

from djotali.campaigns.models import Campaign, Notification


class NotificationSerializer(serializers.ModelSerializer):
    contact = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = ('status', 'send_date', 'contact')


class CampaignSerializer(serializers.ModelSerializer):
    notifications = serializers.StringRelatedField()

    class Meta:
        model = Campaign
        fields = ('name', 'start_date', 'message', 'notifications')
