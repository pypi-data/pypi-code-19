from django.contrib import admin
from mmogo.people.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)