# coding: utf-8
from djotali.campaigns.api import router
from djotali.campaigns.api.viewsets import CampaignViewSet

urlpatterns = [
    router.register(r'campaigns', CampaignViewSet)
]
