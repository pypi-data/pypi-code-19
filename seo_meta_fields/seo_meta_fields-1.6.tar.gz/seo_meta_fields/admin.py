from django.contrib import admin
from seo_meta_fields.models import MetaImage, SiteInformation, OpenGraph, GoogleVerification, BingVerification, BasicTags, AdvancedTags
# Register your models here.
admin.site.register(MetaImage)
admin.site.register(SiteInformation)
admin.site.register(OpenGraph)
admin.site.register(GoogleVerification)
admin.site.register(BingVerification)
admin.site.register(BasicTags)
admin.site.register(AdvancedTags)
