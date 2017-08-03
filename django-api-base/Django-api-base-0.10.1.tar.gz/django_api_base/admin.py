from django.contrib import admin
from .models import *


# Register your models here.
class AdminDisplay(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super(AdminDisplay, self).__init__(model, admin_site)

admin.site.register(AccessToken, AdminDisplay)
admin.site.register(RefreshToken, AdminDisplay)
admin.site.register(DeviceID, AdminDisplay)
