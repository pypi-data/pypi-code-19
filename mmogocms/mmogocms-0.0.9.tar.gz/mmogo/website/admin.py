from django.contrib import admin
from mmogo.website.models import Website

class WebsiteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Website, WebsiteAdmin)