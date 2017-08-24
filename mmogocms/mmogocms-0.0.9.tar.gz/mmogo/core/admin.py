from django.contrib import admin
from mmogo.core.models import BaseModel

class BaseModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

	def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()


admin.site.register(BaseModel, BaseModelAdmin)