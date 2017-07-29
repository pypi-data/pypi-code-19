# coding: utf-8
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from djotali.campaigns.api.serializers import NotificationSerializer, CampaignSerializer
from djotali.campaigns.models import Campaign
from djotali.campaigns.models import Notification


class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    @detail_route(methods=['get'])
    def notifications(self, request, pk=None):
        notifications = Notification.objects.filter(campaign_id=pk).prefetch_related('contact')
        return Response(NotificationSerializer(notifications, many=True).data)
