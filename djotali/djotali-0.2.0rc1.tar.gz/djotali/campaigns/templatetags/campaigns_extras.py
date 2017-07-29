# coding: utf-8
from django import template

from djotali.campaigns.tasks import is_campaign_launched

register = template.Library()


@register.filter
def can_launch_campaign(campaign):
    return campaign.is_started() and not is_campaign_launched(campaign.id)
