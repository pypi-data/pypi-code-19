# coding: utf-8

from rest_framework import routers

from djotali.campaigns.api.viewsets import CampaignViewSet

router = routers.DefaultRouter()

router.register(r'campaigns', CampaignViewSet)
