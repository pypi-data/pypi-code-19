# coding: utf-8

from django.contrib import admin

from djotali.campaigns import models


class CampaignAdmin(admin.ModelAdmin):
    model = models.Campaign
    list_display = ('name', 'start_date')


admin.site.register(models.Campaign, CampaignAdmin)
